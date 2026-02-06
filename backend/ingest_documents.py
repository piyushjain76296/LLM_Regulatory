"""Document ingestion script for regulatory documents."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag_engine import get_rag_engine


def ingest_all_documents():
    """Ingest all regulatory documents into the vector database."""
    
    print("Initializing RAG engine...")
    rag_engine = get_rag_engine()
    
    # Clear existing collection
    print("Clearing existing documents...")
    rag_engine.clear_collection()
    
    # Define documents to ingest
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "data", "regulatory_docs")
    
    documents = [
        {
            "path": os.path.join(docs_dir, "pra_rulebook_sample.txt"),
            "type": "PRA_Rulebook"
        },
        {
            "path": os.path.join(docs_dir, "corep_instructions_sample.txt"),
            "type": "COREP_Instructions"
        }
    ]
    
    # Ingest each document
    for doc in documents:
        if os.path.exists(doc["path"]):
            print(f"\nIngesting {doc['type']}...")
            rag_engine.ingest_document(doc["path"], doc["type"])
        else:
            print(f"Warning: Document not found: {doc['path']}")
    
    print("\n✓ Document ingestion complete!")
    print(f"Total documents in collection: {rag_engine.collection.count()}")


if __name__ == "__main__":
    ingest_all_documents()
