# app/routes.py
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

from app.rag import PDFRAG
from app.db import MongoDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize MongoDB client
def get_db():
    """
    Dependency function for MongoDB.
    Will try to connect to MongoDB, and fall back to in-memory storage if connection fails.
    """
    try:
        # Try to initialize MongoDB with connection to actual server
        db = MongoDB()
        if hasattr(db, 'use_in_memory') and db.use_in_memory:
            logger.warning("Using in-memory storage as MongoDB connection failed")
        return db
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        # Create MongoDB instance with fallback mode enabled
        return MongoDB(use_fallback=True)

# In-memory cache for active sessions to avoid recreating PDFRAG objects for every request
active_sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    question: str

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: MongoDB = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
    
    try:
        file_bytes = await file.read()
        logger.info(f"Received PDF file: {file.filename}, size: {len(file_bytes)} bytes")
        
        # Create a new PDFRAG instance
        pdf_rag = PDFRAG(file_bytes)
        
        # Generate a new session ID
        session_id = str(uuid.uuid4())
        logger.info(f"Created new session: {session_id}")
        
        # Store the session in MongoDB
        try:
            db.store_session(session_id, file_bytes)
        except Exception as e:
            logger.error(f"MongoDB storage failed: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to store session in database: {str(e)}")
        
        # Also keep it in memory for faster access
        active_sessions[session_id] = pdf_rag
        
        return {"session_id": session_id, "message": "PDF processed successfully."}
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.post("/chat")
async def chat_with_pdf(request: ChatRequest, db: MongoDB = Depends(get_db)):
    session_id = request.session_id
    question = request.question
    logger.info(f"Chat request for session {session_id}: '{question}'")

    # First check the in-memory cache
    pdf_rag = active_sessions.get(session_id)
    
    # If not in memory, try to load from MongoDB
    if pdf_rag is None:
        logger.info(f"Session {session_id} not in memory, attempting to load from MongoDB")
        try:
            # Get the PDF bytes from MongoDB
            pdf_bytes = db.load_session(session_id)
            if pdf_bytes is None:
                raise HTTPException(status_code=404, detail="Session ID not found. Please upload a PDF first.")
            
            # Create a new PDFRAG instance with the PDF bytes
            pdf_rag = PDFRAG(pdf_bytes)
            
            # Add to in-memory cache for future requests
            active_sessions[session_id] = pdf_rag
            logger.info(f"Successfully loaded session {session_id} from MongoDB")
        except Exception as e:
            logger.error(f"Error loading session from MongoDB: {e}")
            raise HTTPException(status_code=500, detail=f"Error loading session: {str(e)}")
    
    try:
        answer = pdf_rag.query(question)
        logger.info(f"Generated answer for session {session_id}")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error during query: {e}")
        raise HTTPException(status_code=500, detail=f"Error during query: {str(e)}")

# Route to list all active sessions
@router.get("/sessions")
async def list_sessions(db: MongoDB = Depends(get_db)):
    try:
        # Get session IDs from MongoDB
        sessions = list(db.sessions.find({}, {"session_id": 1, "_id": 0}))
        session_ids = [session["session_id"] for session in sessions]
        logger.info(f"Listed {len(session_ids)} sessions")
        return {"sessions": session_ids}
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

# Route to delete a session
@router.delete("/session/{session_id}")
async def delete_session(session_id: str, db: MongoDB = Depends(get_db)):
    try:
        # Remove from in-memory cache if present
        if session_id in active_sessions:
            del active_sessions[session_id]
            logger.info(f"Removed session {session_id} from memory cache")
        
        # Remove from MongoDB
        deleted = db.delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Successfully deleted session {session_id}")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

# Route to check MongoDB connection status
@router.get("/db-status")
async def check_db_status(db: MongoDB = Depends(get_db)):
    """Check MongoDB connection status"""
    if hasattr(db, 'use_in_memory') and db.use_in_memory:
        # We're in fallback mode
        session_count = len(db.in_memory_storage) if hasattr(db, 'in_memory_storage') else 0
        return {
            "status": "fallback",
            "message": "Using in-memory storage (MongoDB connection failed)",
            "active_sessions": session_count
        }
        
    try:
        # Try to ping the MongoDB server
        db.client.admin.command('ping')
        
        # Count existing sessions
        session_count = db.sessions.count_documents({})
        
        logger.info(f"DB Status: Connected, {session_count} active sessions")
        return {
            "status": "connected",
            "message": "Successfully connected to MongoDB",
            "database": db.db.name,
            "active_sessions": session_count
        }
    except Exception as e:
        logger.error(f"DB Status: Connection error - {e}")
        # If we get here, we're probably using in-memory storage as fallback
        session_count = len(db.in_memory_storage) if hasattr(db, 'in_memory_storage') else 0
        return {
            "status": "fallback",
            "message": f"Using in-memory storage (MongoDB error: {str(e)})",
            "active_sessions": session_count
        }