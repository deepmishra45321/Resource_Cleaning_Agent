import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_retriever():
    """Initializes and returns a FAISS retriever over the runbook documentation."""
    # Construct path to runbook.md
    current_dir = os.path.dirname(os.path.abspath(__file__))
    runbook_path = os.path.join(current_dir, "..", "docs", "runbook.md")
    
    loader = TextLoader(runbook_path)
    documents = loader.load()
    
    # Use CPU-friendly huggingface embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create FAISS vector store
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    return vectorstore.as_retriever()
