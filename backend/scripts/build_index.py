"""
Build FAISS Index Script
Run this to create/update the FAISS index from policy documents
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
import structlog
from core.document_processor import DocumentProcessor
from core.faiss_index import FAISSIndex
from app.config import settings

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def build_index():
    """
    Build FAISS index from policy documents
    """
    print("🚀 Building FAISS Index for Risk Copilot")
    print("=" * 50)
    
    # Step 1: Process documents
    print("\n📄 Processing policy documents...")
    processor = DocumentProcessor(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        embedding_model=settings.EMBEDDING_MODEL
    )
    
    # Process all documents in the policies folder
    policies_dir = Path("data/policies")
    if not policies_dir.exists():
        print(f"❌ Policies directory not found: {policies_dir}")
        return False
    
    try:
        data = processor.process_documents(str(policies_dir))
        
        print(f"✅ Processed {data['stats']['total_documents']} documents")
        print(f"📊 Created {data['stats']['total_chunks']} chunks")
        print(f"🔢 Embedding dimension: {data['stats']['embedding_dim']}")
        
        # Save processed data
        processed_dir = Path("data/processed")
        processor.save_processed_data(data, str(processed_dir))
        
    except Exception as e:
        print(f"❌ Error processing documents: {e}")
        return False
    
    # Step 2: Build FAISS index
    print("\n🔨 Building FAISS index...")
    index = FAISSIndex(
        index_path=settings.FAISS_INDEX_PATH,
        embedding_dim=data['stats']['embedding_dim'],
        embedding_model=settings.EMBEDDING_MODEL
    )
    
    try:
        # Create index from embeddings
        index.create_index(
            embeddings=data['embeddings'],
            chunks=[{"content": c.page_content, "metadata": c.metadata} 
                   for c in data['chunks']],
            documents=data['documents']
        )
        
        # Save index
        index.save()
        
        # Get stats
        stats = index.get_stats()
        print(f"✅ FAISS index created with {stats['total_vectors']} vectors")
        print(f"💾 Index saved to {settings.FAISS_INDEX_PATH}")
        
    except Exception as e:
        print(f"❌ Error building index: {e}")
        return False
    
    # Step 3: Test the index
    print("\n🧪 Testing index with sample queries...")
    test_queries = [
        "What is model risk?",
        "LLM governance requirements",
        "How often should models be validated?",
        "What are the AI ethics principles?"
    ]
    
    for query in test_queries:
        print(f"\n📍 Query: '{query}'")
        results = index.search(query, k=3, score_threshold=0.5)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result['score']:.3f} | Doc: {result['metadata']['document_name']}")
                print(f"     Section: {result['metadata'].get('section', 'N/A')}")
                print(f"     Preview: {result['content'][:100]}...")
        else:
            print("  No results found")
    
    print("\n" + "=" * 50)
    print("✅ FAISS index built successfully!")
    print("\nYou can now:")
    print("1. Start the backend: uvicorn app.main:app --reload")
    print("2. The chat endpoint will use this index for RAG")
    
    return True

def verify_index():
    """
    Verify that the index exists and is working
    """
    index_path = Path(settings.FAISS_INDEX_PATH)
    
    if not (index_path / "faiss.index").exists():
        print("❌ Index not found. Run build_index() first.")
        return False
    
    # Try loading the index
    index = FAISSIndex(
        index_path=settings.FAISS_INDEX_PATH,
        embedding_model=settings.EMBEDDING_MODEL
    )
    
    if index.load():
        stats = index.get_stats()
        print(f"✅ Index loaded successfully")
        print(f"📊 Stats: {stats}")
        return True
    else:
        print("❌ Failed to load index")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FAISS Index Builder")
    parser.add_argument("--verify", action="store_true", help="Verify existing index")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild index")
    
    args = parser.parse_args()
    
    if args.verify:
        verify_index()
    else:
        # Check if index exists
        index_path = Path(settings.FAISS_INDEX_PATH) / "faiss.index"
        if index_path.exists() and not args.rebuild:
            print("ℹ️  Index already exists. Use --rebuild to force rebuild.")
            verify_index()
        else:
            build_index()