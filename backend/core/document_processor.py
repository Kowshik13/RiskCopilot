"""
Document Processor for Risk Copilot
Handles document chunking, embedding, and indexing
"""

import os
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import numpy as np
from sentence_transformers import SentenceTransformer
import structlog

logger = structlog.get_logger()

class DocumentProcessor:
    """
    Processes policy documents for RAG implementation
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize document processor
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            embedding_model: Name of the sentence transformer model
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
        
    def load_document(self, file_path: str) -> Dict[str, Any]:
        """
        Load a document from file
        
        Args:
            file_path: Path to the document
            
        Returns:
            Document metadata and content
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate document ID from content hash
        doc_id = hashlib.md5(content.encode()).hexdigest()[:12]
        
        metadata = {
            "id": doc_id,
            "name": path.name,
            "path": str(path),
            "size": len(content),
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "type": path.suffix
        }
        
        return {
            "metadata": metadata,
            "content": content
        }
    
    def chunk_document(self, document: Dict[str, Any]) -> List[Document]:
        """
        Split document into chunks
        
        Args:
            document: Document dict with metadata and content
            
        Returns:
            List of document chunks
        """
        content = document["content"]
        metadata = document["metadata"]
        
        # Create LangChain documents
        doc = Document(
            page_content=content,
            metadata=metadata
        )
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([doc])
        
        # Add chunk-specific metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": f"{metadata['id']}_chunk_{i}",
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk.page_content)
            })
            
            # Extract section context (find headers)
            lines = content[:content.find(chunk.page_content)].split('\n')
            section = None
            for line in reversed(lines):
                if line.startswith('#'):
                    section = line.strip('#').strip()
                    break
            if section:
                chunk.metadata["section"] = section
        
        logger.info(f"Created {len(chunks)} chunks from {metadata['name']}")
        return chunks
    
    def embed_chunks(self, chunks: List[Document]) -> np.ndarray:
        """
        Generate embeddings for document chunks
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Numpy array of embeddings
        """
        texts = [chunk.page_content for chunk in chunks]
        
        # Generate embeddings in batches for efficiency
        batch_size = 32
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embedder.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            embeddings.append(batch_embeddings)
        
        # Concatenate all embeddings
        all_embeddings = np.vstack(embeddings) if embeddings else np.array([])
        
        logger.info(f"Generated {len(all_embeddings)} embeddings")
        return all_embeddings
    
    def process_documents(self, directory: str) -> Dict[str, Any]:
        """
        Process all documents in a directory
        
        Args:
            directory: Path to directory containing documents
            
        Returns:
            Dict with chunks, embeddings, and metadata
        """
        doc_dir = Path(directory)
        if not doc_dir.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        all_chunks = []
        all_embeddings = []
        doc_metadata = {}
        
        # Process markdown files
        for file_path in doc_dir.glob("*.md"):
            try:
                logger.info(f"Processing {file_path.name}")
                
                # Load document
                doc = self.load_document(str(file_path))
                doc_metadata[doc["metadata"]["id"]] = doc["metadata"]
                
                # Chunk document
                chunks = self.chunk_document(doc)
                
                # Generate embeddings
                embeddings = self.embed_chunks(chunks)
                
                all_chunks.extend(chunks)
                all_embeddings.append(embeddings)
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue
        
        # Combine all embeddings
        if all_embeddings:
            combined_embeddings = np.vstack(all_embeddings)
        else:
            combined_embeddings = np.array([])
        
        logger.info(f"Processed {len(doc_metadata)} documents, {len(all_chunks)} total chunks")
        
        return {
            "chunks": all_chunks,
            "embeddings": combined_embeddings,
            "documents": doc_metadata,
            "stats": {
                "total_documents": len(doc_metadata),
                "total_chunks": len(all_chunks),
                "embedding_dim": self.embedding_dim,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }
        }
    
    def save_processed_data(self, data: Dict[str, Any], output_dir: str):
        """
        Save processed data to disk
        
        Args:
            data: Processed data dict
            output_dir: Output directory path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save embeddings as numpy array
        np.save(output_path / "embeddings.npy", data["embeddings"])
        
        # Save chunks and metadata as JSON
        chunks_data = []
        for chunk in data["chunks"]:
            chunks_data.append({
                "content": chunk.page_content,
                "metadata": chunk.metadata
            })
        
        with open(output_path / "chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        # Save document metadata
        with open(output_path / "documents.json", "w", encoding="utf-8") as f:
            json.dump(data["documents"], f, indent=2)
        
        # Save processing stats
        with open(output_path / "stats.json", "w", encoding="utf-8") as f:
            json.dump(data["stats"], f, indent=2)
        
        logger.info(f"Saved processed data to {output_path}")


def main():
    """
    Main function for testing document processor
    """
    from app.config import settings
    
    processor = DocumentProcessor(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        embedding_model=settings.EMBEDDING_MODEL
    )
    
    # Process policy documents
    data = processor.process_documents("data/policies")
    
    # Save processed data
    processor.save_processed_data(data, "data/processed")
    
    print(f"✅ Processed {data['stats']['total_documents']} documents")
    print(f"📄 Created {data['stats']['total_chunks']} chunks")
    print(f"🔢 Embedding dimension: {data['stats']['embedding_dim']}")


if __name__ == "__main__":
    main()