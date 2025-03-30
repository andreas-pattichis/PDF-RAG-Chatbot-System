# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router

app = FastAPI(title="Local LLM with RAG for PDFs")

# API endpoints are served under /api
app.include_router(router, prefix="/api")

# Serve the UI from the frontend folder
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)