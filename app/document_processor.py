"""
Document processing utilities
"""
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import load_config
from app.database import get_database

async def process_document(file_path: str, filename: str) -> str:
    """
    Process a PDF document:
    1. Load document using PyPDFLoader
    2. Split into chunks
    3. Generate embeddings
    4. Store in MongoDB
    
    Returns:
        document_id: Unique ID for the document
    """
    # Load configuration
    config = load_config()
    
    # Generate a unique document ID
    document_id = str(uuid.uuid4())
    
    # Load the PDF
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"]
    )
    chunks = text_splitter.split_documents(documents)
    
    # Add metadata to chunks
    for chunk in chunks:
        # Add additional metadata
        chunk.metadata["source"] = filename
        chunk.metadata["document_id"] = document_id
        chunk.metadata["upload_date"] = datetime.now().isoformat()
    
    # Initialize embedding model
    embedding_model = HuggingFaceEmbeddings(model_name=config["embedding_model"])
    
    # Generate embeddings and prepare for MongoDB
    db_chunks = []
    for i, chunk in enumerate(chunks):
        try:
            # Generate embedding
            embedding = embedding_model.embed_query(chunk.page_content)
            
            # Prepare document for MongoDB
            db_chunk = {
                "text": chunk.page_content,
                "embedding": embedding,
                "metadata": chunk.metadata,
                "document_id": document_id,
                "chunk_id": i
            }
            
            db_chunks.append(db_chunk)
            print(f"Processed chunk {i+1}/{len(chunks)} for document: {filename}")
        except Exception as e:
            print(f"Error processing chunk {i}: {str(e)}")
    
    # Store chunks in MongoDB
    print(f"Storing {len(db_chunks)} chunks in MongoDB...")
    db = await get_database()
    await db.insert_document_chunks(db_chunks)
    print(f"Document processing complete: {filename}")
    
    return document_id