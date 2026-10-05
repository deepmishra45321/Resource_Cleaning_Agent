# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Initial project structure created.
- Setup scripts (`setup.bat`, `setup.sh`) to initialize venv and pull Ollama model `qwen2.5:1.5b`.
- Requirements file mapping to the correct tech stack.
- `app/whitelist.json` to store approved processes.
- `docs/runbook.md` with guidelines on critical system processes.
- `app/rag.py` configuring FAISS and HuggingFace embeddings for local RAG.
- `app/tools.py` implementing FastMCP In-Memory tools for metrics, getting top processes, and killing processes.
- `app/graph.py` defining the LangGraph workflow, checkpointer, and structured LLM evaluation.
- `app/app.py` delivering the Streamlit interface with session state caching, Streamlit graph continuation, and Audit mode.
