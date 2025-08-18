# OshaDocumentStorage.py
# OSHA-specific document storage and processing functionality

import os
import re
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain.schema import Document

from web_content_scraper import WebContentScraper
from pdf_content_processor import PDFContentProcessor


# Load environment variables from .env file
load_dotenv()
VectorDBPath = os.getenv("VECTOR_DB_PATH")


class OSHADocumentProcessor:
    """OSHA-specific document processing and storage class."""
    
    def __init__(self, base_url: str = "https://www.osha.gov"):
        self.base_url = base_url
        self.web_scraper = WebContentScraper(base_url=base_url)
        self.pdf_processor = PDFContentProcessor()
        
        # OSHA-specific content selectors for better extraction
        self.osha_content_selectors = {
            "headings": ["h1", "h2", "h3", "h4", "h5", "h6"],
            "paragraphs": ["p"],
            "lists": ["ul", "ol"],
            "tables": ["table"],
            "links": ["a"],
            "divs": ["div"],
            "osha_specific": ["div.regulation", "div.guidance", "div.compliance"]
        }
        
        # OSHA-specific metadata
        self.osha_metadata = {
            "source_type": "osha_regulation",
            "agency": "OSHA",
            "jurisdiction": "federal"
        }

    def fetch_osha_page(self, path: str) -> List[Document]:
        """Fetch and parse an OSHA page with OSHA-specific processing."""
        # Add OSHA-specific headers if needed
        osha_headers = {
            "Referer": self.base_url,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        self.web_scraper.set_custom_headers(osha_headers)
        
        # Fetch and parse with OSHA-specific selectors
        documents = self.web_scraper.fetch_and_parse(path, self.osha_content_selectors)
        
        # Add OSHA-specific metadata to all documents
        for doc in documents:
            doc.metadata.update(self.osha_metadata)
            doc.metadata["osha_path"] = path
            doc.metadata["content_type"] = "web_page"
            
        return documents

    def process_osha_pdf(self, pdf_path: str, 
                         content_selectors: Optional[Dict[str, Any]] = None,
                         max_pages: Optional[int] = None) -> List[Document]:
        """Process an OSHA PDF document with OSHA-specific processing."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Process PDF with the generic processor
        documents = self.pdf_processor.process_pdf(
            pdf_path, 
            content_selectors=content_selectors,
            max_pages=max_pages
        )
        
        # Add OSHA-specific metadata to all documents
        for doc in documents:
            doc.metadata.update(self.osha_metadata)
            doc.metadata["content_type"] = "pdf_document"
            doc.metadata["pdf_path"] = pdf_path
            
            # Extract regulation number from filename if possible
            regulation_number = self._extract_regulation_number_from_filename(pdf_path)
            if regulation_number:
                doc.metadata["regulation_number"] = regulation_number
                doc.metadata["regulation_type"] = self._classify_regulation(regulation_number)
        
        return documents

    def _extract_regulation_number_from_filename(self, pdf_path: str) -> str:
        """Extract OSHA regulation number from PDF filename."""
        filename = os.path.basename(pdf_path)
        
        # Common OSHA regulation patterns in filenames
        patterns = [
            r'1910\.(\d+)',  # General Industry
            r'1926\.(\d+)',  # Construction
            r'1915\.(\d+)',  # Maritime
            r'1917\.(\d+)',  # Marine Terminals
            r'1918\.(\d+)',  # Longshoring
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(0)
        return ""

    def process_osha_regulation(self, regulation_path: str) -> List[Document]:
        """Process a specific OSHA regulation with enhanced metadata."""
        documents = self.fetch_osha_page(regulation_path)
        
        # Extract regulation number from path if possible
        regulation_number = self._extract_regulation_number(regulation_path)
        if regulation_number:
            for doc in documents:
                doc.metadata["regulation_number"] = regulation_number
                doc.metadata["regulation_type"] = self._classify_regulation(regulation_path)
        
        return documents

    def _extract_regulation_number(self, path: str) -> str:
        """Extract OSHA regulation number from path."""
        # Common OSHA regulation patterns
        patterns = [
            r'1910\.(\d+)',  # General Industry
            r'1926\.(\d+)',  # Construction
            r'1915\.(\d+)',  # Maritime
            r'1917\.(\d+)',  # Marine Terminals
            r'1918\.(\d+)',  # Longshoring
        ]
        
        for pattern in patterns:
            match = re.search(pattern, path)
            if match:
                return match.group(0)
        return ""

    def _classify_regulation(self, path: str) -> str:
        """Classify the type of OSHA regulation based on path."""
        if "1910" in path:
            return "general_industry"
        elif "1926" in path:
            return "construction"
        elif "1915" in path:
            return "maritime"
        elif "1917" in path:
            return "marine_terminals"
        elif "1918" in path:
            return "longshoring"
        else:
            return "other"

    def ingest_osha_documents(self, paths: List[str], persist_dir: str = None) -> str:
        """Ingest multiple OSHA documents (web pages and PDFs) into vector database."""
        if persist_dir is None:
            persist_dir = VectorDBPath or "./osha_vector_db"
        
        all_documents = []
        
        for path in paths:
            try:
                print(f"Processing OSHA path: {path}")
                
                if path.lower().endswith('.pdf'):
                    # Process as PDF
                    docs = self.process_osha_pdf(path)
                    print(f"  - Extracted {len(docs)} PDF document chunks")
                else:
                    # Process as web page
                    docs = self.process_osha_regulation(path)
                    print(f"  - Extracted {len(docs)} web page document chunks")
                
                all_documents.extend(docs)
                
            except Exception as e:
                print(f"  - Error processing {path}: {e}")
        
        if not all_documents:
            print("No documents to process")
            return persist_dir
        
        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_documents(all_documents)
        
        # Create embeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # Store in Chroma DB
        vectorstore = Chroma.from_documents(
            chunks,
            embeddings,
            persist_directory=persist_dir
        )
        vectorstore.persist()
        
        print(f"Successfully ingested {len(chunks)} chunks into {persist_dir}")
        return persist_dir

    def ingest_mixed_osha_content(self, web_paths: List[str] = None, 
                                 pdf_paths: List[str] = None,
                                 persist_dir: str = None) -> str:
        """Ingest a mix of web pages and PDFs with separate processing."""
        if persist_dir is None:
            persist_dir = VectorDBPath or "./osha_vector_db"
        
        all_documents = []
        
        # Process web pages
        if web_paths:
            print("Processing web pages...")
            for path in web_paths:
                try:
                    docs = self.process_osha_regulation(path)
                    all_documents.extend(docs)
                    print(f"  - {path}: {len(docs)} chunks")
                except Exception as e:
                    print(f"  - Error processing web page {path}: {e}")
        
        # Process PDFs
        if pdf_paths:
            print("Processing PDFs...")
            for pdf_path in pdf_paths:
                try:
                    docs = self.process_osha_pdf(pdf_path)
                    all_documents.extend(docs)
                    print(f"  - {pdf_path}: {len(docs)} chunks")
                except Exception as e:
                    print(f"  - Error processing PDF {pdf_path}: {e}")
        
        if not all_documents:
            print("No documents to process")
            return persist_dir
        
        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_documents(all_documents)
        
        # Create embeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # Store in Chroma DB
        vectorstore = Chroma.from_documents(
            chunks,
            embeddings,
            persist_directory=persist_dir
        )
        vectorstore.persist()
        
        print(f"Successfully ingested {len(chunks)} chunks into {persist_dir}")
        return persist_dir

    def search_osha_documents(self, query: str, persist_dir: str = None, k: int = 5) -> List[Document]:
        """Search OSHA documents in the vector database."""
        if persist_dir is None:
            persist_dir = VectorDBPath or "./osha_vector_db"
        
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        try:
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
            
            results = vectorstore.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def get_processing_capabilities(self) -> Dict[str, Any]:
        """Get information about available processing capabilities."""
        return {
            "web_scraping": {
                "available": True,
                "base_url": self.base_url,
                "content_selectors": self.osha_content_selectors
            },
            "pdf_processing": {
                "available": True,
                "engines": self.pdf_processor.get_engine_info(),
                "supported_formats": ["PDF"]
            },
            "metadata_extraction": {
                "regulation_numbers": True,
                "regulation_types": True,
                "content_classification": True
            }
        }


# Convenience functions for backward compatibility
def ingest_osha(path: str, persist_dir: str = None) -> str:
    """Legacy function for ingesting a single OSHA document."""
    processor = OSHADocumentProcessor()
    return processor.ingest_osha_documents([path], persist_dir)


if __name__ == "__main__":
    # Example usage
    processor = OSHADocumentProcessor()
    
    # Example: OSHA regulations for General Industry (web pages)
    web_regulation_paths = [
        "/laws-regs/regulations/standardnumber/1910/1910.23",  # Guarding floor and wall openings
        "/laws-regs/regulations/standardnumber/1910/1910.95",  # Occupational noise exposure
        "/laws-regs/regulations/standardnumber/1910/1910.1200" # Hazard communication
    ]
    
    # Example: OSHA PDF documents (if you have them)
    pdf_paths = [
        # "path/to/osha_regulation_1910.23.pdf",
        # "path/to/osha_guidance_1910.95.pdf"
    ]
    
    # Ingest mixed content
    if pdf_paths:
        db_path = processor.ingest_mixed_osha_content(
            web_paths=web_regulation_paths,
            pdf_paths=pdf_paths
        )
    else:
        # Ingest only web pages
        db_path = processor.ingest_osha_documents(web_regulation_paths)
    
    # Search for specific information
    results = processor.search_osha_documents("noise exposure limits", db_path)
    print(f"Found {len(results)} relevant documents")
    
    # Show processing capabilities
    capabilities = processor.get_processing_capabilities()
    print(f"Processing capabilities: {capabilities}")
