# app/routes.py
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.rag import PDFRAG

router = APIRouter()

# In-memory storage for PDF sessions (for production, consider a persistent storage solution)
pdf_sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    question: str

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
    file_bytes = await file.read()
    try:
        pdf_rag = PDFRAG(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")
    
    session_id = str(uuid.uuid4())
    pdf_sessions[session_id] = pdf_rag
    return {"session_id": session_id, "message": "PDF processed successfully."}

@router.post("/chat")
async def chat_with_pdf(request: ChatRequest):
    session_id = request.session_id
    question = request.question

    if session_id not in pdf_sessions:
        raise HTTPException(status_code=404, detail="Session ID not found. Please upload a PDF first.")
    
    pdf_rag = pdf_sessions[session_id]
    try:
        answer = pdf_rag.query(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during query: {e}")
    
    return {"answer": answer}