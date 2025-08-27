#!/usr/bin/env python3
"""
DocumentAgent Web Application
A web interface for uploading PDFs, processing them, and chatting with the content using Ollama.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from pdf_content_processor import PDFContentProcessor
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Configuration
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# File upload configuration
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}
VECTOR_DB_PATH = os.environ.get('VECTOR_DB_PATH', './document_vector_db')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# Global variables
pdf_processor = PDFContentProcessor()
embeddings = OllamaEmbeddings(model="nomic-embed-text")
llm = OllamaLLM(model="gemma3:4b")  # Using the model you have installed

# Initialize conversation memory
conversation_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_vectorstore():
    """Get or create the vector store."""
    try:
        # Try to load existing vector store
        vectorstore = Chroma(
            persist_directory=VECTOR_DB_PATH,
            embedding_function=embeddings
        )
        # Check if it has documents
        if vectorstore._collection.count() > 0:
            return vectorstore
    except Exception:
        pass
    
    # Create new vector store if none exists
    return Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )

def process_and_store_pdf(file_path: str, filename: str) -> Dict[str, Any]:
    """Process PDF and store in vector database."""
    try:
        # Process PDF
        documents = pdf_processor.process_pdf(file_path)
        
        if not documents:
            return {"success": False, "error": "No content extracted from PDF"}
        
        # Split documents into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata.update({
                "uploaded_at": datetime.now().isoformat(),
                "original_filename": filename,
                "file_id": str(uuid.uuid4())
            })
        
        # Store in vector database
        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)
        vectorstore.persist()
        
        return {
            "success": True,
            "chunks_created": len(chunks),
            "filename": filename,
            "message": f"Successfully processed {len(chunks)} chunks from {filename}"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_documents(query: str, k: int = 5) -> List[Document]:
    """Search documents in the vector database."""
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search(query, k=k)
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

def get_chat_response(query: str, chat_history: List[Dict]) -> str:
    """Get response from Ollama using document context and general knowledge."""
    try:
        # Search for relevant documents
        relevant_docs = search_documents(query, k=3)
        
        if relevant_docs:
            # Create context from relevant documents
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Create prompt with document context
            prompt = f"""You are a helpful assistant that can answer questions using both the provided document context and your general knowledge. 
            Use the document context when it's relevant, but you can also provide general information if the documents don't cover the topic completely.
            Be concise and helpful.

            Document Context:
            {context}

            Question: {query}

            Answer:"""
        else:
            # No relevant documents found, use general knowledge only
            prompt = f"""You are a helpful assistant. Answer the following question using your general knowledge. 
            Be concise and helpful.

            Question: {query}

            Answer:"""
        
        # Get response from Ollama
        response = llm.invoke(prompt)
        
        return response.strip()
        
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"})
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                file.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            # Process and store PDF
            result = process_and_store_pdf(tmp_path, filename)
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            return jsonify(result)
            
        except RequestEntityTooLarge:
            return jsonify({"success": False, "error": "File too large. Maximum size is 100MB."})
        except Exception as e:
            return jsonify({"success": False, "error": f"Upload error: {str(e)}"})
    
    return jsonify({"success": False, "error": "Invalid file type. Only PDF files are allowed."})

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    data = request.get_json()
    query = data.get('message', '').strip()
    
    if not query:
        return jsonify({"success": False, "error": "No message provided"})
    
    # Get chat history from session
    chat_history = session.get('chat_history', [])
    
    # Get response
    response = get_chat_response(query, chat_history)
    
    # Update chat history
    chat_history.append({"user": query, "assistant": response})
    session['chat_history'] = chat_history[-10:]  # Keep last 10 messages
    
    return jsonify({
        "success": True,
        "response": response,
        "chat_history": chat_history
    })

@app.route('/documents')
def get_documents():
    """Get list of processed documents."""
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        
        # Get unique documents with actual chunk counts
        documents = []
        seen_files = {}
        
        try:
            # Get all documents from the collection
            all_docs = collection.get()
            if all_docs and 'metadatas' in all_docs:
                for i, metadata in enumerate(all_docs['metadatas']):
                    if metadata and 'original_filename' in metadata:
                        filename = metadata['original_filename']
                        
                        if filename not in seen_files:
                            # First time seeing this file, initialize
                            seen_files[filename] = {
                                "filename": filename,
                                "uploaded_at": metadata.get('uploaded_at', 'Unknown'),
                                "chunks": 1
                            }
                        else:
                            # Increment chunk count for this file
                            seen_files[filename]["chunks"] += 1
                
                # Convert to list
                documents = list(seen_files.values())
                
        except Exception as e:
            print(f"Error getting documents: {e}")
            pass
        
        return jsonify({"success": True, "documents": documents})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/delete_document', methods=['POST'])
def delete_document():
    """Delete a document and all its chunks."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"success": False, "error": "No filename provided"})
        
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        
        # Get all documents with this filename
        all_docs = collection.get()
        if not all_docs or 'metadatas' not in all_docs:
            return jsonify({"success": False, "error": "No documents found"})
        
        # Find indices of chunks to delete
        indices_to_delete = []
        for i, metadata in enumerate(all_docs['metadatas']):
            if metadata and metadata.get('original_filename') == filename:
                indices_to_delete.append(i)
        
        if not indices_to_delete:
            return jsonify({"success": False, "error": "Document not found"})
        
        # Delete chunks by their IDs
        if 'ids' in all_docs:
            ids_to_delete = [all_docs['ids'][i] for i in indices_to_delete]
            collection.delete(ids=ids_to_delete)
        
        return jsonify({
            "success": True, 
            "message": f"Successfully deleted {len(indices_to_delete)} chunks from {filename}"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    """Clear chat history."""
    session['chat_history'] = []
    return jsonify({"success": True, "message": "Chat history cleared"})

@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        # Check if Ollama is accessible
        llm.invoke("test")
        return jsonify({"status": "healthy", "ollama": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "ollama": "disconnected", "error": str(e)})

if __name__ == '__main__':
    print("Starting DocumentAgent Web Application...")
    print(f"Vector database path: {VECTOR_DB_PATH}")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print("Make sure Ollama is running with the required models!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
