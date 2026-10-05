# Local SysOps Agent

A production-grade "Local SysOps Agent" designed as a portfolio showcase. This project demonstrates advanced mastery of LangGraph v0.2+ (Supervisor patterns, checkpointers, conditional routing, human-in-the-loop via `interrupt`), RAG (Vector Stores with FAISS), the Model Context Protocol (FastMCP), and Streamlit.

## Architecture

- **UI Layer**: Streamlit dashboard with live telemetry, Audit Mode, live thought streaming, and Human-in-the-Loop policy engine.
- **Agent Layer**: LangGraph workflow with `SqliteSaver` checkpointer, Qwen2.5:1.5b, and structured outputs for process diagnosis.
- **System Access Layer**: FastMCP (In-Memory Client) wrapping `psutil` for safe system interactions.

## How to Run

1. Run the setup script for your OS:
   - Windows: `setup.bat`
   - Mac/Linux: `bash setup.sh`
2. Ensure [Ollama](https://ollama.ai) is installed and running.
3. Activate the virtual environment (if not already activated):
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Run the Streamlit application:
   ```bash
   streamlit run app/app.py
   ```
