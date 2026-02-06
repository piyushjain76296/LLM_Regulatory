"""RAG (Retrieval-Augmented Generation) engine for regulatory document retrieval."""

import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from backend.config import settings


class RAGEngine:
    """Retrieval-Augmented Generation engine for regulatory documents."""
    
    def __init__(self):
        """Initialize the RAG engine with ChromaDB and embedding model."""
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="regulatory_documents",
            metadata={"description": "PRA Rulebook and COREP instructions"}
        )
    
    def ingest_document(self, document_path: str, document_type: str):
        """
        Ingest a regulatory document into the vector database.
        
        Args:
            document_path: Path to the document file
            document_type: Type of document (e.g., 'PRA_Rulebook', 'COREP_Instructions')
        """
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split document into chunks (by sections/paragraphs)
        chunks = self._chunk_document(content)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Prepare metadata
        metadatas = [
            {
                "document_type": document_type,
                "source": os.path.basename(document_path),
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]
        
        # Generate IDs
        ids = [f"{document_type}_{i}" for i in range(len(chunks))]
        
        # Add to collection
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Ingested {len(chunks)} chunks from {document_path}")
    
    def _chunk_document(self, content: str) -> List[str]:
        """
        Split document into meaningful chunks.
        
        Strategy: Split by sections (## headers) and paragraphs.
        """
        chunks = []
        current_chunk = []
        
        lines = content.split('\n')
        
        for line in lines:
            # New section or subsection
            if line.startswith('##') or line.startswith('###'):
                if current_chunk:
                    chunks.append('\n'.join(current_chunk).strip())
                    current_chunk = [line]
                else:
                    current_chunk.append(line)
            # Empty line indicates paragraph break
            elif line.strip() == '':
                if current_chunk:
                    chunk_text = '\n'.join(current_chunk).strip()
                    if len(chunk_text) > 50:  # Minimum chunk size
                        chunks.append(chunk_text)
                    current_chunk = []
            else:
                current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk).strip())
        
        return [c for c in chunks if c]  # Filter empty chunks
    
    def retrieve_context(self, query: str, n_results: int = None) -> List[Dict]:
        """
        Retrieve relevant regulatory context for a query.
        
        Args:
            query: Natural language query
            n_results: Number of results to retrieve
            
        Returns:
            List of relevant document chunks with metadata
        """
        if n_results is None:
            n_results = settings.max_retrieval_results
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Query the collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results
        context_items = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                context_items.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })
        
        return context_items
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        self.client.delete_collection("regulatory_documents")
        self.collection = self.client.get_or_create_collection(
            name="regulatory_documents",
            metadata={"description": "PRA Rulebook and COREP instructions"}
        )
        print("Collection cleared")


# Global RAG engine instance
_rag_engine = None


def get_rag_engine() -> RAGEngine:
    """Get or create the global RAG engine instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
