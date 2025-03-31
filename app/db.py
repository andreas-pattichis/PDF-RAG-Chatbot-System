# app/db.py
import logging
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson.binary import Binary
import pickle
import io
from app.config import MONGO_CONNECTION_STR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self, use_fallback=False):
        if use_fallback:
            self.use_in_memory = True
            self.in_memory_storage = {}
            logger.warning("Using in-memory storage as fallback")
            return
            
        try:
            # Use certifi CA bundle for SSL validation
            # Set TLS/SSL parameters explicitly
            self.client = MongoClient(MONGO_CONNECTION_STR, serverSelectionTimeoutMS=5000)
            
            # Validate the connection
            self.client.admin.command('ping')
            self.db = self.client.pdf_rag_db
            self.sessions = self.db.sessions
            self.use_in_memory = False
            logger.info("Successfully connected to MongoDB")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB, using in-memory fallback: {e}")
            self.use_in_memory = True
            self.in_memory_storage = {}

    def store_session(self, session_id, pdf_bytes):
        """Store a new PDF session"""
        if self.use_in_memory:
            self.in_memory_storage[session_id] = pdf_bytes
            logger.info(f"Stored session {session_id} in memory (fallback mode)")
            return True
            
        try:
            # Store the original PDF bytes and session ID
            session_doc = {
                "session_id": session_id,
                "pdf_bytes": Binary(pdf_bytes)
            }
            
            # Check if session already exists
            existing = self.sessions.find_one({"session_id": session_id})
            if existing:
                self.sessions.replace_one({"session_id": session_id}, session_doc)
            else:
                self.sessions.insert_one(session_doc)
            
            logger.info(f"Successfully stored session {session_id} in MongoDB")
            return True
        except Exception as e:
            logger.error(f"Error storing session in MongoDB: {e}")
            
            # Fallback to in-memory if MongoDB fails
            self.in_memory_storage[session_id] = pdf_bytes
            logger.info(f"Falling back to in-memory storage for session {session_id}")
            return True

    def load_session(self, session_id):
        """Load a PDF session and return the stored PDF bytes"""
        if self.use_in_memory:
            pdf_bytes = self.in_memory_storage.get(session_id)
            if pdf_bytes is None:
                logger.warning(f"Session {session_id} not found in memory (fallback mode)")
                return None
            logger.info(f"Loaded session {session_id} from memory (fallback mode)")
            return pdf_bytes
            
        try:
            session = self.sessions.find_one({"session_id": session_id})
            if not session:
                logger.warning(f"Session {session_id} not found in MongoDB")
                return None
            
            # Return the PDF bytes
            logger.info(f"Successfully loaded session {session_id} from MongoDB")
            return session["pdf_bytes"]
        except Exception as e:
            logger.error(f"Error loading session from MongoDB, trying fallback: {e}")
            
            # Try fallback to in-memory if MongoDB fails
            pdf_bytes = self.in_memory_storage.get(session_id)
            if pdf_bytes is None:
                logger.warning(f"Session {session_id} not found in memory fallback")
                return None
            logger.info(f"Loaded session {session_id} from memory fallback")
            return pdf_bytes
    
    def session_exists(self, session_id):
        """Check if a session exists"""
        if self.use_in_memory:
            return session_id in self.in_memory_storage
            
        try:
            count = self.sessions.count_documents({"session_id": session_id})
            return count > 0
        except Exception as e:
            logger.error(f"Error checking session existence in MongoDB: {e}")
            return session_id in self.in_memory_storage
    
    def delete_session(self, session_id):
        """Delete a session"""
        if self.use_in_memory:
            if session_id in self.in_memory_storage:
                del self.in_memory_storage[session_id]
                logger.info(f"Deleted session {session_id} from memory (fallback mode)")
                return True
            return False
            
        try:
            result = self.sessions.delete_one({"session_id": session_id})
            if result.deleted_count > 0:
                logger.info(f"Successfully deleted session {session_id} from MongoDB")
                # Also remove from in-memory fallback if it exists
                if hasattr(self, 'in_memory_storage') and session_id in self.in_memory_storage:
                    del self.in_memory_storage[session_id]
                return True
            else:
                logger.warning(f"Session {session_id} not found in MongoDB for deletion")
                return False
        except Exception as e:
            logger.error(f"Error deleting session from MongoDB: {e}")
            
            # Try fallback to in-memory if MongoDB fails
            if hasattr(self, 'in_memory_storage') and session_id in self.in_memory_storage:
                del self.in_memory_storage[session_id]
                logger.info(f"Deleted session {session_id} from memory fallback")
                return True
            return False