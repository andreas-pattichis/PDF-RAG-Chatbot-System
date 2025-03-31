# PDF RAG Chatbot System
A simple web app that allows you to chat with your PDF documents using Retrieval Augmented Generation (RAG) technology. Upload any PDF and ask questions about its content to receive accurate, context-aware answers.

<img src="https://github.com/user-attachments/assets/73e4a4ed-c8af-47b9-9d0b-6cf378b3a832" alt="RAG Reader Preview" width="580">

## 🚀 Features

- **PDF Processing**: Upload and process PDF documents of any size
- **Natural Language Queries**: Ask questions in plain English about your document
- **Contextual Answers**: Get answers based on the content of your PDF
- **Interactive UI**: Clean, responsive user interface for direct interaction
- **Session Management**: Multiple document sessions with persistent storage
- **MongoDB Integration**: Store sessions for persistence across server restarts

## 🏗 System Architecture

The application is built with a backend-frontend architecture:

1. **Frontend**: HTML/CSS/JS interface that users interact with to upload PDFs and ask questions
2. **FastAPI Backend**: Handles HTTP requests, manages sessions, and coordinates the RAG workflow
3. **RAG Engine**: Processes PDFs, creates embeddings, and generates answers from queries
4. **Vector Database**: Stores document embeddings for efficient semantic retrieval
5. **LLM Integration**: Connects with OpenAI API to generate natural language responses
6. **MongoDB**: Stores PDF sessions persistently for access across server restarts

## 🧠 How RAG Works

Retrieval Augmented Generation (RAG) combines information retrieval with text generation for more accurate, contextual responses.

### RAG Process Flow:

<img src="https://github.com/user-attachments/assets/c50d595b-febe-4797-8a65-36f97f97e244" alt="RAG Process Flow" width="550">

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
- MongoDB (local installation or cloud)

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
MONGO_CONNECTION_STR=mongodb://localhost:27017
```

5. **Run the application**

```bash
uvicorn main:app --reload
```

6. **Access the application**

Open your browser and navigate to `http://localhost:8000`

## 🗄️ MongoDB Setup

The application uses MongoDB to store PDF sessions persistently. This allows for sessions to be maintained even if the server restarts.

### Setting Up Local MongoDB

1. **Install MongoDB Community Edition**:
   - Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Follow the installation instructions for your operating system
   - Make sure the MongoDB service is running

2. **Connect to Local MongoDB**:
   - The default connection string for local MongoDB is `mongodb://localhost:27017`
   - Update your `.env` file with this connection string
   - No authentication is required for local development setup

3. **Install MongoDB Compass (Optional but recommended)**:
   - MongoDB Compass is a GUI for MongoDB
   - Download from [MongoDB Compass Download](https://www.mongodb.com/products/compass)
   - Use it to visually inspect your database

### Alternative: Using MongoDB Atlas (Cloud)

If you prefer using MongoDB Atlas (cloud version):

1. **Create a MongoDB Atlas account**:
   - Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
   - Create a new cluster (the free tier is sufficient)

2. **Set up network access**:
   - Add your IP address to the IP Access List
   - Or set it to allow access from anywhere (for development only)

3. **Create a database user**:
   - Create a user with read/write privileges for the database

4. **Get your connection string**:
   - Go to "Connect" > "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your user's password
   - Add this connection string to your `.env` file

### Verifying MongoDB Setup

To verify your MongoDB setup is working correctly:

1. **Check via Application**:
   - Start the application with `uvicorn main:app --reload`
   - Access the `/api/db-status` endpoint in your browser:
     `http://localhost:8000/api/db-status`
   - You should see a status response indicating successful connection

2. **Check via MongoDB Compass**:
   - Connect to your MongoDB instance (local or Atlas)
   - After uploading a PDF, refresh Compass
   - You should see a `pdf_rag_db` database with a `sessions` collection
   - Each document contains a `session_id` and `pdf_bytes` field

3. **Testing Persistence**:
   - Upload a PDF and use the chat functionality
   - Stop and restart the application server
   - Your chat session should still be available

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
│   ├── db.py              # MongoDB integration
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

#### MongoDB Integration (`app/db.py`)

Handles persistent storage of PDF sessions:
- Connection to MongoDB (local or cloud)
- Session storage and retrieval
- Automatic fallback to in-memory storage if MongoDB fails
- Error handling and logging

```python
class MongoDB:
    def __init__(self):
        # Connect to MongoDB
        self.client = MongoClient(MONGO_CONNECTION_STR)
        self.db = self.client.pdf_rag_db
        self.sessions = self.db.sessions
```

#### API Routes (`app/routes.py`)

Handles HTTP requests for:
- PDF uploads
- Chat interactions
- Session management
- Database status checks

```python
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Process PDF upload and create session
    
@router.post("/chat")
async def chat_with_pdf(request: ChatRequest):
    # Process chat request and return answer

@router.get("/db-status")
async def check_db_status():
    # Check MongoDB connection status
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

1. User uploads a PDF through the browser interface
2. Browser sends the PDF to the FastAPI server via a POST request
3. Server generates embeddings using OpenAI API
4. Vectors are stored in the FAISS vector store
5. PDF bytes are stored in MongoDB for persistence
6. A session ID is returned to the browser
7. Browser notifies the user that the system is ready for chat
8. User sends questions through the chat interface
9. Relevant context is retrieved from the vector store
10. The context and question are sent to OpenAI to generate an answer
11. Answer is returned to the user through the chat interface

## 🗄️ MongoDB Integration

The MongoDB integration provides persistent storage for PDF sessions, allowing users to access their documents even after server restarts.

### What's Stored in MongoDB

Each document in the `sessions` collection contains:
- `session_id`: A unique identifier for the session
- `pdf_bytes`: Binary data of the uploaded PDF

### MongoDB Workflow

1. **Session Creation**:
   - When a PDF is uploaded, a new session is created
   - The raw PDF bytes are stored in MongoDB
   - A session ID is generated and returned to the client

2. **Session Retrieval**:
   - When a user makes a query, the session ID is used to identify the document
   - If the session is not in memory, it's loaded from MongoDB
   - The PDFRAG object is recreated from the stored PDF bytes

3. **Fallback Mechanism**:
   - If MongoDB connection fails, the system falls back to in-memory storage
   - This allows the application to continue functioning even without database access
   - Users can still upload and query PDFs, but sessions won't persist after server restart

### MongoDB Status Endpoint

The `/api/db-status` endpoint provides information about the MongoDB connection:
- Connection status (connected or fallback)
- Active sessions count
- Database name
- Error messages if connection failed

## 🛡 Technologies Used

### Backend

- **FastAPI**: Web framework
- **LangChain**: Framework for LLM application development
- **OpenAI API**: For embeddings and LLM capabilities
- **PyPDF2**: PDF processing library
- **FAISS**: Similarity search library
- **MongoDB**: Persistent storage for PDF sessions

### Frontend

- **HTML5/CSS3**: Web markup and styling
- **JavaScript**: Frontend interactivity
- **Fetch API**: Asynchronous HTTP requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created with ❤️ by Andreas Pattichis
