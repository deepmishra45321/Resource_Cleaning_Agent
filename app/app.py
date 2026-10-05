import streamlit as st
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
import sqlite3
import os

from graph import build_graph
from tools import get_system_metrics

st.set_page_config(page_title="Local SysOps Agent", layout="wide")

# 1. Initialize persistent state safely
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "sysops-session-2" # Reset thread ID to handle new graph schema

@st.cache_resource
def get_checkpointer():
    # check_same_thread=False is critical for Streamlit
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sysops.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return SqliteSaver(conn)

config = {"configurable": {"thread_id": st.session_state.thread_id}}
checkpointer = get_checkpointer()
builder = build_graph()
graph = builder.compile(checkpointer=checkpointer)

st.title("Local SysOps Agent: Smart Automation")

# Sidebar: Live Telemetry
st.sidebar.header("Live Telemetry")
metrics = get_system_metrics()
st.sidebar.text(metrics)

audit_mode = st.sidebar.checkbox("Audit Mode (Dry-Run)", value=True)
st.sidebar.write("In Audit Mode, processes are not actually terminated.")

# 2. Check for active interrupts
state = graph.get_state(config)
if state.next and state.tasks[0].interrupts:
    st.warning("Automated Cleanup Paused: Requires human approval to kill the following bloat processes.")
    interrupt_data = state.tasks[0].interrupts[0].value
    
    if interrupt_data.get("type") == "bulk_approval":
        st.write("### Recommended Processes to Stop")
        for t in interrupt_data["targets"]:
            st.info(f"**{t['name']}** (RAM: {t.get('ram_mb', 0):.2f} MB)  \n*Reason:* {t['reason']}")
    else:
        # Fallback for old interrupts
        st.write("### Process Evaluation")
        st.json(interrupt_data)
        
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Approve Cleanup"):
            graph.invoke(Command(resume="approve"), config=config)
            st.rerun()
            
    with col2:
        if st.button("Deny"):
            graph.invoke(Command(resume="deny"), config=config)
            st.rerun()
            
    with col3:
        if st.button("Whitelist All"):
            graph.invoke(Command(resume="approve_whitelist"), config=config)
            st.rerun()
            
    st.stop() # Prevent the rest of the UI from loading while waiting

# Main UI
st.write("Click below to start a smart diagnostic run. The agent will scan your top resource-consuming processes, identify idle or bloatware processes, and queue them for automated cleanup.")

if st.button("Run Smart Automated Cleanup"):
    initial_state = {
        "messages": [],
        "target_processes": [],
        "final_report": "",
        "audit_mode": audit_mode,
        "current_process_eval": None
    }
    
    # Live thought streaming
    with st.status("Agent Scanning System...", expanded=True) as status:
        for event in graph.stream(initial_state, config=config):
            for node, values in event.items():
                if "messages" in values and values["messages"]:
                    st.write(f"**{node}**: {values['messages'][-1]}")
                
                # Check if it was interrupted right after fixer
                current_state = graph.get_state(config)
                if current_state.next and current_state.tasks[0].interrupts:
                    st.write(f"**{node}**: Discovered processes to clean up! Interrupted for human approval.")
                    
        status.update(label="Scan complete!", state="complete", expanded=True)
    
    st.rerun()

st.write("### Current Graph State")
current_state = graph.get_state(config)
if current_state.values:
    if current_state.values.get("final_report"):
        st.success(f"**Final Report:**\n{current_state.values['final_report']}")
    with st.expander("Raw State Dictionary"):
        st.json(current_state.values)
