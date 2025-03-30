"""
RAG (Retrieval Augmented Generation) implementation
"""
from typing import Dict, List, Any, Optional
import logging
import pymongo

from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document

from app.models import Source
from app.database import get_database

class RAGChain:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize RAG Chain
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.k = config.get("default_k", 5)
        self.threshold = config.get("default_threshold", 0.2)
        
        # Initialize embedding model
        try:
            if "ollama" in config.get("embedding_model", "").lower():
                self.embedding_model = OllamaEmbeddings(
                    base_url=config.get("ollama_embed_host", "http://localhost:11434"),
                    model=config.get("embedding_model", "llama2")
                )
            else:
                self.embedding_model = HuggingFaceEmbeddings(
                    model_name=config.get("embedding_model", "sentence-transformers/all-mpnet-base-v2")
                )
        except Exception as e:
            logging.error(f"Error initializing embedding model: {e}")
            # Fall back to default
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2"
            )
        
        # Initialize LLM
        self.llm = ChatOllama(
            base_url=config.get("ollama_host", "http://localhost:11434"),
            model=config.get("llm_model", "llama2:7b"),
            format="json"
        )
        
        # Create RAG prompt
        self.prompt = PromptTemplate.from_template(
            """
            You are a helpful assistant that answers questions based on the provided context.
            
            Context:
            {context}
            
            Question: {question}
            
            Please provide a clear, concise answer based on the context. If the context doesn't contain 
            relevant information to answer the question, say "I don't have enough information to answer that question."
            
            Answer:
            """
        )
    
    async def _get_vector_store(self):
        """Create MongoDB vector store for retrieval"""
        db_name = self.config["database_name"]
        collection_name = self.config["collection_name"]
        
        # Create an instance of MongoDB client
        client = pymongo.MongoClient(self.config["mongo_connection_string"])
        db = client[db_name]
        collection = db[collection_name]
        
        return MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=self.embedding_model,
            text_key="text",
            embedding_key="embedding",
            index_name="default"
        )
    
    async def _retrieve_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents based on the query
        
        Args:
            query: User query
            
        Returns:
            List of retrieved documents
        """
        try:
            vector_store = await self._get_vector_store()
            
            # Log search query
            print(f"Searching for: {query}")
            
            # Perform similarity search
            docs = vector_store.similarity_search_with_score(
                query=query,
                k=self.k
            )
            
            print(f"Found {len(docs)} documents")
            
            # If no documents found, return empty list
            if not docs:
                print("No documents found in search")
                return []
                
            # Debug: show scores
            for doc, score in docs:
                print(f"Doc score: {score}, content preview: {doc.page_content[:50]}...")
            
            # Filter by threshold - RELAXED: using a higher threshold or disabling filtering
            # Scores closer to 0 are better in cosine similarity
            filtered_docs = [doc for doc, score in docs]  # No filtering, return all docs
            
            return filtered_docs
            
        except Exception as e:
            print(f"Error in retrieval: {str(e)}")
            # Return empty list on error
            return []
    
    def _format_context(self, docs: List[Document]) -> str:
        """Format retrieved documents into context string"""
        return "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
    
    def _extract_sources(self, docs: List[Document]) -> List[Source]:
        """Extract source information from documents"""
        sources = []
        for doc in docs:
            source = Source(
                document=doc.metadata.get("source", "Unknown"),
                page=doc.metadata.get("page", None),
                chunk=doc.metadata.get("chunk_id", 0)
            )
            sources.append(source)
        
        return sources
    
    async def generate_response(self, question: str) -> Dict[str, Any]:
        """
        Generate a response using RAG
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve relevant documents
        docs = await self._retrieve_documents(question)
        
        # Extract sources
        sources = self._extract_sources(docs)
        
        # Format context
        context = self._format_context(docs)
        
        # If no relevant documents found
        if not docs:
            return {
                "answer": "I don't have enough information to answer that question.",
                "sources": []
            }
        
        # Generate answer
        chain = (
            {"context": lambda x: context, "question": lambda x: question}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        answer = await chain.ainvoke({})
        
        return {
            "answer": answer,
            "sources": sources
        }