# app/rag.py
import io
from PyPDF2 import PdfReader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI  # Updated imports
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS  # Updated import
from langchain.chains import RetrievalQA

from app.config import OPENAI_API_KEY

class PDFRAG:
    def __init__(self, file_bytes: bytes):
        self.text = self.extract_text(file_bytes)
        self.vectorstore = self.create_vectorstore(self.text)
        self.qa_chain = self.create_qa_chain(self.vectorstore)

    def extract_text(self, file_bytes: bytes) -> str:
        """Extract text from a PDF file given as bytes."""
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    def create_vectorstore(self, text: str):
        """Split text into chunks and create a FAISS vector store."""
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_text(text)
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        vectorstore = FAISS.from_texts(texts, embeddings)
        return vectorstore

    def create_qa_chain(self, vectorstore):
        """Create a RetrievalQA chain using the vector store."""
        llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())
        return qa_chain

    def query(self, question: str) -> str:
        """Get an answer for the question using the QA chain."""
        return self.qa_chain.run(question)