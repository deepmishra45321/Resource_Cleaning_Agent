# Local SysOps Agent: Comprehensive Technical Guide

## 1. Project Overview & Purpose
The Local SysOps Agent is a smart, automated resource-cleaning tool. Its primary goal is to intelligently monitor a computer's RAM, identify idle bloatware or unnecessary background processes, and safely terminate them to speed up the system. It uses advanced Artificial Intelligence (Local LLMs) and Graph-based agent logic to ensure critical OS processes are never harmed.

## 2. Version Requirements & Tech Stack
- **Python:** 3.10+ (Developed and optimized for Python 3.12 environments)
- **OS:** Windows (Primary support for `psutil` process fetching), though logically compatible with Mac/Linux.
- **Ollama:** v0.3.0+ (Required to run the local LLM).
- **Qwen2.5:1.5b:** The specific local AI model used for fast, structured reasoning on low-end hardware.

### Detailed Breakdown of Tools & Libraries
| Tool/Library | Purpose in this Project | What it Actually Does |
|---|---|---|
| **Streamlit (v1.30+)** | The Frontend / UI | Renders the web dashboard. It displays the live CPU/RAM telemetry on the sidebar and creates the interactive buttons that trigger the AI. |
| **LangGraph (v0.2+)** | The "Brain's Routing System" | Orchestrates the AI workflow. It forces the application to follow a strict graph: Gather -> Diagnose -> Pause for Approval -> Kill. It prevents the AI from skipping steps. |
| **FastMCP** | System Access Layer | The Model Context Protocol (MCP) securely wraps our dangerous Python scripts (like killing processes) into isolated tools that the AI can understand and use safely. |
| **psutil** | Hardware Scanner | A Python library used for directly talking to the Windows kernel to fetch live RAM usage and actively terminate specific Process IDs (PIDs). |
| **FAISS (faiss-cpu)** | Memory / Vector Database | Used for Retrieval-Augmented Generation (RAG). It stores the text of our `runbook.md` as numbers (vectors) so the AI can rapidly search it to check if a process is critical. |
| **Langchain-Ollama** | AI Bridge | Connects our Python code to the locally running Ollama server, allowing us to enforce "Structured Outputs" (forcing the AI to reply in a strict JSON format instead of a chatty paragraph). |

---

## 3. Step-by-Step: What Happens Behind the Scenes?

When you click the **"Run Smart Automated Cleanup"** button, the following chain reaction occurs:

### Step 1: State Initialization
The app generates an empty `GraphState` dictionary. This dictionary acts as a temporary memory bank that is passed from node to node as the agent does its work.

### Step 2: Gathering Targets (The "Gather" Node)
The workflow enters the `gather_processes_node`. 
- The agent calls the FastMCP tool `get_top_processes(limit=5)`.
- It scans the operating system and retrieves a list of the 5 processes consuming the most RAM.
- It saves this list into the `GraphState` memory.

### Step 3: AI Diagnosis (The "Diagnoser" Node)
The workflow moves to the `diagnoser_node`. For each of the 5 gathered processes:
1. **RAG Lookup:** The agent searches the FAISS database (built from `docs/runbook.md`) for the process name (e.g., `explorer.exe`).
2. **AI Evaluation:** The found context and the process name are sent to the local **Qwen2.5:1.5b** AI model.
3. **The Prompt:** The AI is instructed: *"Is this critical? Or is it an unused background updater/bloatware?"*
4. **Structured Decision:** The AI responds strictly with `is_critical: True/False` and a `reason`.

### Step 4: The Safety Net & Human-in-the-Loop (The "Fixer" Node)
The workflow moves to the `fixer_node`.
- It filters out any process the AI marked as critical.
- It filters out any process saved in `whitelist.json`.
- **The Interrupt:** LangGraph executes the `interrupt()` function. This sends a signal back to Streamlit, immediately pausing the backend execution and throwing up the yellow warning box in the UI. 

### Step 5: Final Execution (Approve/Deny)
The app sits frozen in its SQLite database (`sysops.db`) waiting for you.
- If you click **Approve Cleanup**, the Graph resumes from the exact line of code where it paused. It loops through the approved targets and calls the `psutil.terminate()` command to free up your RAM.
- If **Audit Mode** is checked in the sidebar, it bypasses the termination code and simply prints a simulation message, keeping your system safe while you test.
