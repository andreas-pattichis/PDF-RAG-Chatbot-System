"""
MongoDB database connection and operations
"""
import pymongo
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Any, Optional

# Global database client
db_client = None
db = None
collection = None

async def init_database(config: Dict[str, Any]):
    """
    Initialize database connection
    """
    global db_client, db, collection
    
    # Connect to MongoDB
    db_client = AsyncIOMotorClient(config["mongo_connection_string"])
    
    # Get database and collection
    db = db_client[config["database_name"]]
    collection = db[config["collection_name"]]
    
    # Create text index for searching
    await collection.create_index([("text", pymongo.TEXT)])
    
    # Create index on document_id for faster retrieval
    await collection.create_index("document_id")
    
    # Create index on metadata.source for faster filtering
    await collection.create_index("metadata.source")

async def get_database():
    """
    Get database client
    """
    global db_client, db, collection
    
    class DatabaseInterface:
        async def insert_document_chunks(self, chunks: List[Dict[str, Any]]):
            """
            Insert document chunks into the database
            """
            if chunks:
                await collection.insert_many(chunks)
        
        async def get_all_documents(self):
            """
            Get a list of all unique documents (without duplicates)
            """
            pipeline = [
                {"$group": {"_id": "$metadata.source", "document": {"$first": "$$ROOT"}}},
                {"$project": {"_id": 0, "filename": "$document.metadata.source", "document_id": "$document.document_id", "upload_date": "$document.metadata.upload_date"}}
            ]
            
            documents = []
            async for doc in collection.aggregate(pipeline):
                documents.append(doc)
            
            return documents
        
        async def get_document_by_id(self, document_id: str):
            """
            Get document by ID
            """
            cursor = collection.find({"document_id": document_id})
            document_chunks = []
            async for chunk in cursor:
                document_chunks.append(chunk)
            
            return document_chunks
        
        async def delete_document(self, document_id: str):
            """
            Delete document by ID
            """
            result = await collection.delete_many({"document_id": document_id})
            return result.deleted_count
    
    return DatabaseInterface()