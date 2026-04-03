#!/usr/bin/env python3
"""Setup knowledge base for a CommunityOS bot."""

import argparse
import os
import sys
from pathlib import Path


def init_chroma_collection(project_path: Path, bot_id: str):
    """Initialize Chroma collection for a bot."""
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        print("Error: chromadb not installed. Run: pip install chromadb")
        sys.exit(1)
    
    # Create knowledge directory
    knowledge_dir = project_path / "knowledge" / bot_id
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Chroma
    chroma_dir = project_path / "chroma_db" / bot_id
    chroma_dir.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(chroma_dir))
    
    # Create collection
    collection_name = f"{bot_id}_knowledge"
    try:
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"bot_id": bot_id}
        )
        print(f"✓ Created Chroma collection: {collection_name}")
    except Exception as e:
        print(f"Error creating collection: {e}")
        sys.exit(1)
    
    # Create sample doc placeholder
    sample_doc = knowledge_dir / "README.md"
    if not sample_doc.exists():
        sample_doc.write_text("""# {bot_name} 知识库

Place your knowledge documents here.

## Supported Formats
- .txt - Plain text
- .md - Markdown
- .pdf - PDF documents (requires pdfplumber)
- .json - JSON data

## Usage
Add documents to this folder, then run indexing to update the vector database.
""".format(bot_name=bot_id))
        print(f"✓ Created sample docs: {sample_doc}")
    
    return collection


def index_documents(project_path: Path, bot_id: str, collection):
    """Index documents from knowledge folder into Chroma."""
    knowledge_dir = project_path / "knowledge" / bot_id
    
    if not knowledge_dir.exists():
        print(f"⚠ No knowledge folder: {knowledge_dir}")
        return
    
    indexed = 0
    for doc_path in knowledge_dir.glob("*.md"):
        content = doc_path.read_text()
        # Simple chunking
        chunks = [content[i:i+500] for i in range(0, len(content), 500)]
        
        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                ids=[f"{doc_path.stem}_{i}"],
                metadatas=[{"source": str(doc_path), "bot_id": bot_id}]
            )
            indexed += 1
    
    print(f"✓ Indexed {indexed} chunks from {knowledge_dir}")


def main():
    parser = argparse.ArgumentParser(description="Setup knowledge base for CommunityOS bot")
    parser.add_argument("project_path", help="Path to CommunityOS project")
    parser.add_argument("bot_id", help="Bot ID to setup knowledge for")
    parser.add_argument("--index", "-i", action="store_true",
                        help="Also index existing documents")
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path).resolve()
    
    # Validate project
    if not (project_path / "souls").exists():
        print(f"Error: {project_path} is not a valid CommunityOS project")
        sys.exit(1)
    
    print(f"Setting up knowledge base for bot: {args.bot_id}")
    print("-" * 40)
    
    # Initialize collection
    collection = init_chroma_collection(project_path, args.bot_id)
    
    # Index documents if requested
    if args.index:
        index_documents(project_path, args.bot_id, collection)
    
    print(f"\n✅ Knowledge base ready!")
    print(f"   Add documents to: {project_path / 'knowledge' / args.bot_id}")
    print(f"   Run with --index to re-index documents")


if __name__ == "__main__":
    main()
