"""
DocuChat - Main FastAPI Application
"""
import os
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import tempfile
import shutil
import uuid

from app.config import load_config
from app.database import get_database, init_database
from app.document_processor import process_document
from app.rag import RAGChain
from app.models import ChatRequest, ChatResponse

# Initialize FastAPI app
app = FastAPI(title="DocuChat", description="Chat with your PDF documents using LLMs and RAG")

# Get base directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

# Load configuration
config = load_config()

# Initialize RAG Chain
rag_chain = RAGChain(config)

# Initialize database connection on startup
@app.on_event("startup")
async def startup_db_client():
    await init_database(config)
    
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Render the chat interface page"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a PDF document
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Create temporary file
    temp_dir = tempfile.mkdtemp()
    try:
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # Save uploaded file to temp location
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the document and store in MongoDB
        document_id = await process_document(temp_file_path, file.filename)
        
        return {"status": "success", "message": f"Document '{file.filename}' uploaded and processed successfully", "document_id": document_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    finally:
        # Clean up temp files
        shutil.rmtree(temp_dir)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with documents using RAG
    """
    try:
        # Get response from RAG chain
        response = await rag_chain.generate_response(request.message)
        
        return ChatResponse(
            message_id=str(uuid.uuid4()),
            response=response["answer"],
            sources=response["sources"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/api/documents")
async def get_documents():
    """
    Get list of all uploaded documents
    """
    try:
        db = await get_database()
        documents = await db.get_all_documents()
        return {"documents": documents}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")