# PDF RAG Chatbot System

A simple web app that allows you to chat with your PDF documents using Retrieval Augmented Generation (RAG) technology. Upload any PDF and ask questions about its content to receive accurate, context-aware answers.

## 🚀 Features

- **PDF Processing**: Upload and process PDF documents of any size
- **Natural Language Queries**: Ask questions in plain English about your document
- **Contextual Answers**: Get answers based on the content of your PDF
- **Interactive UI**: Clean, responsive user interface for direct interaction
- **Session Management**: Multiple document sessions without server restarts

## 📋 Table of Contents

- [System Architecture](#-system-architecture)
- [How RAG Works](#-how-rag-works)
- [Setup Instructions](#-setup-instructions)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Key Components](#-key-components)
- [Session Management](#-session-management)
- [Technologies Used](#-technologies-used)
- [License](#-license)

## 🏗 System Architecture

The system follows a modular architecture:



The application is built with a backend-frontend architecture:

1. **Frontend**: HTML/CSS/JS interface that users interact with to upload PDFs and ask questions
2. **FastAPI Backend**: Handles HTTP requests, manages sessions, and coordinates the RAG workflow
3. **RAG Engine**: Processes PDFs, creates embeddings, and generates answers from queries
4. **Vector Database**: Stores document embeddings for efficient semantic retrieval
5. **LLM Integration**: Connects with OpenAI API to generate natural language responses

## 🧠 How RAG Works

Retrieval Augmented Generation (RAG) combines information retrieval with text generation for more accurate, contextual responses.

### RAG Process Flow:



The diagram above illustrates the two main phases of the RAG process:

1. **Document Processing Phase**:
   - **PDF Document**: The starting point - your uploaded PDF document
   - **Text Extraction**: Using PyPDF2 to extract raw text from the PDF document
   - **Chunk & Process Text**: Splitting text into manageable chunks with appropriate overlap using CharacterTextSplitter
   - **Create Embeddings**: Converting text chunks into vector embeddings using OpenAI's embedding model
   - **Store in Vector DB**: Storing these vector embeddings in a FAISS index for efficient similarity search

2. **Query Processing Phase**:
   - **User Question**: The natural language query from the user
   - **Query Embedding**: Converting the user's question into the same vector space using OpenAI Embeddings
   - **Retrieve Similar Chunks**: Finding the most relevant text chunks using FAISS similarity search
   - **Context Augmentation**: Using the retrieved chunks as context for the question via RetrievalQA Chain
   - **Answer Generation**: Generating a natural language response based on the provided context using ChatOpenAI

The Vector Database Connection ensures that the system can efficiently retrieve the most semantically relevant chunks from the document when answering user queries.

## 🛠 Setup Instructions

### Prerequisites

- Anaconda or Miniconda
- Python 11
- OpenAI API key
- MongoDB (optional, for persistent storage)

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/andreas-pattichis/PDF-RAG-Chatbot-System.git
cd PDF-RAG-Chatbot-System
```

2. **Create and activate a conda environment with Python 11**

```bash
conda create -n pdf-rag-env python=3.11
conda activate pdf-rag-env
```

3. **Install the required packages**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
MONGO_CONNECTION_STR=your_mongodb_connection_string  # Optional
```

5. **Run the application**

```bash
uvicorn main:app --reload
```

6. **Access the application**

Open your browser and navigate to `http://localhost:8000`

## 📖 Usage Guide

### Uploading a PDF

1. Open the application in your browser
2. Drag and drop a PDF file into the upload area or click to browse
3. Click the "Upload PDF" button
4. Wait for the processing to complete (larger PDFs will take longer)

### Chatting with your document

1. After successful upload, the chat interface will activate
2. Type your question in the text box at the bottom
3. Press Enter or click the send button
4. The system will process your question and display the answer
5. Continue asking questions as needed

### Tips for effective queries

- Be specific with your questions
- Prefer direct questions over open-ended ones
- Break complex queries into simpler ones
- Reference specific sections or pages if possible
- Use follow-up questions to drill deeper into a topic

## 📁 Project Structure

```
PDF-RAG-Chatbot-System/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration and environment variables
│   ├── rag.py             # RAG implementation
│   └── routes.py          # API endpoints
├── frontend/
│   ├── index.html         # Main HTML file
│   ├── script.js          # Frontend JavaScript
│   └── style.css          # CSS styles
├── .env                   # Environment variables (create this)
├── .gitignore             # Git ignore file
├── main.py                # Application entry point
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## 🔍 Key Components

### Backend Components

#### PDFRAG Class (`app/rag.py`)

The core RAG implementation that handles:
- Text extraction from PDFs
- Chunking and processing
- Vector embeddings creation
- Query processing and answer generation

```python
class PDFRAG:
    def __init__(self, file_bytes: bytes):
        self.text = self.extract_text(file_bytes)
        self.vectorstore = self.create_vectorstore(self.text)
        self.qa_chain = self.create_qa_chain(self.vectorstore)
```

#### API Routes (`app/routes.py`)

Handles HTTP requests for:
- PDF uploads
- Chat interactions
- Session management

```python
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Process PDF upload and create session
    
@router.post("/chat")
async def chat_with_pdf(request: ChatRequest):
    # Process chat request and return answer
```

### Frontend Components

#### User Interface

- Clean, responsive design
- Drag-and-drop PDF upload
- Interactive chat interface
- Loading indicators and error handling

#### JavaScript Functionality

- AJAX requests to backend API
- PDF upload handling
- Chat interaction management
- UI state management

## 🔀 Session Management

The application handles user sessions and data flow as follows:



The diagram illustrates the complete lifecycle of a user interaction:

1. User uploads a PDF through the browser interface
2. Browser sends the PDF to the FastAPI server via a POST request
3. Server generates embeddings using OpenAI API
4. Vectors are stored in the FAISS vector store
5. A session is created and stored in memory (or database in production)
6. Session ID is returned to the browser
7. Browser notifies the user that the system is ready for chat
8. User sends questions through the chat interface
9. Relevant context is retrieved from the vector store
10. The context and question are sent to OpenAI to generate an answer
11. Answer is returned to the user through the chat interface

This architecture enables stateful conversations about document content while maintaining efficiency and responsiveness.

## 🛡 Technologies Used

### Backend

- **FastAPI**: Web framework
- **LangChain**: Framework for LLM application development
- **OpenAI API**: For embeddings and LLM capabilities
- **PyPDF2**: PDF processing library
- **FAISS**: Similarity search library

### Frontend

- **HTML5/CSS3**: Web markup and styling
- **JavaScript**: Frontend interactivity
- **Fetch API**: Asynchronous HTTP requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created with ❤️ by Andreas Pattichis