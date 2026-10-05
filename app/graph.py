import json
import os
import ast
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langgraph.types import interrupt

from tools import get_top_processes, kill_process
from rag import get_retriever

class GraphState(TypedDict):
    messages: List[str]
    target_processes: List[Dict[str, Any]]
    final_report: str
    audit_mode: bool
    current_process_eval: Optional[Dict[str, Any]]

class ProcessEvaluation(BaseModel):
    is_critical: bool = Field(description="True if the process is a critical OS component")
    reason: str = Field(description="Brief reason for the decision")

def get_whitelist() -> List[str]:
    whitelist_path = os.path.join(os.path.dirname(__file__), "whitelist.json")
    if not os.path.exists(whitelist_path):
        return []
    try:
        with open(whitelist_path, "r") as f:
            return json.load(f)
    except:
        return []

def gather_processes_node(state: GraphState) -> GraphState:
    # Gather top 5 memory-consuming processes for bulk evaluation
    procs_str = get_top_processes(limit=5)
    try:
        procs = ast.literal_eval(procs_str)
    except:
        procs = []
    
    msg = f"Gathered top {len(procs)} memory-consuming processes." if procs else "No processes found."
    return {"target_processes": procs, "messages": state.get("messages", []) + [msg]}

def diagnoser_node(state: GraphState) -> GraphState:
    procs = state.get("target_processes", [])
    if not procs:
        return {"final_report": "No processes found.", "messages": state.get("messages", []) + ["No processes to diagnose."]}
    
    retriever = get_retriever()
    llm = ChatOllama(model="qwen2.5:1.5b", temperature=0)
    evaluator = llm.with_structured_output(ProcessEvaluation)
    
    messages = state.get("messages", [])
    messages.append("Starting AI evaluation of processes to find unused resource hogs...")
    
    for target in procs:
        process_name = target["name"]
        
        docs = retriever.invoke(process_name)
        context = "\n".join([doc.page_content for doc in docs])
        
        # We instruct the LLM to aggressively identify bloatware
        prompt = f"Context:\n{context}\n\nTask: Is '{process_name}' a critical OS component? If it is a non-essential background app, unused updater, or bloatware that consumes memory, set is_critical to false and explain why stopping it will make the system faster."
        
        try:
            evaluation = evaluator.invoke(prompt)
            target["is_critical"] = evaluation.is_critical
            target["reason"] = evaluation.reason
        except Exception as e:
            target["is_critical"] = True 
            target["reason"] = f"Fail-safe: Error {e}"
            
        messages.append(f"Evaluated {process_name}: Critical={target['is_critical']}")
        
    return {"target_processes": procs, "messages": messages}

def fixer_node(state: GraphState) -> GraphState:
    procs = state.get("target_processes", [])
    whitelist = get_whitelist()
    
    kill_targets = []
    for target in procs:
        if not target.get("is_critical", True) and target["name"] not in whitelist:
            kill_targets.append(target)
            
    if not kill_targets:
        msg = "System is optimized! All top processes are critical or whitelisted. Nothing to clean up."
        return {"final_report": msg, "messages": state.get("messages", []) + [msg]}
        
    # Trigger interrupt for Human-in-the-Loop for all targets
    interrupt_action = interrupt({
        "type": "bulk_approval",
        "targets": kill_targets
    })
    
    audit_mode = state.get("audit_mode", True)
    messages = state.get("messages", [])
    report_lines = []
    
    if interrupt_action == "deny":
        msg = "User denied automated cleanup."
        return {"final_report": msg, "messages": messages + [msg]}
        
    if interrupt_action == "approve_whitelist":
        # Add all to whitelist and skip
        whitelist_path = os.path.join(os.path.dirname(__file__), "whitelist.json")
        for t in kill_targets:
            if t["name"] not in whitelist:
                whitelist.append(t["name"])
        with open(whitelist_path, "w") as f:
            json.dump(whitelist, f, indent=4)
        msg = "Whitelisted the proposed processes. No kills executed."
        return {"final_report": msg, "messages": messages + [msg]}
        
    # Execute kills
    for t in kill_targets:
        res = kill_process(pid=t["pid"], audit_mode=audit_mode)
        report_lines.append(f"{t['name']} (PID {t['pid']}): {res}")
        messages.append(res)
        
    final_report = "Cleanup complete:\n" + "\n".join(report_lines)
    return {"final_report": final_report, "messages": messages}

def build_graph():
    builder = StateGraph(GraphState)
    builder.add_node("gather", gather_processes_node)
    builder.add_node("diagnoser", diagnoser_node)
    builder.add_node("fixer", fixer_node)
    
    builder.add_edge(START, "gather")
    builder.add_edge("gather", "diagnoser")
    builder.add_edge("diagnoser", "fixer")
    builder.add_edge("fixer", END)
    
    return builder
