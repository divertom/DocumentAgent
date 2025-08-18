# pdf_content_processor.py
# Generic PDF content processing module

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from langchain.schema import Document

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PDFContentProcessor:
    """Generic PDF content processing class that can handle various PDF formats."""
    
    def __init__(self, preferred_engine: str = "auto"):
        """
        Initialize PDF processor with preferred engine.
        
        Args:
            preferred_engine: "auto", "pymupdf", "pypdf", or "pypdf2"
        """
        self.preferred_engine = preferred_engine
        self.available_engines = self._check_available_engines()
        
        if not self.available_engines:
            raise ImportError(
                "No PDF processing libraries available. "
                "Please install one of: PyMuPDF (fitz), pypdf, or PyPDF2"
            )
    
    def _check_available_engines(self) -> List[str]:
        """Check which PDF processing engines are available."""
        engines = []
        
        if PYMUPDF_AVAILABLE:
            engines.append("pymupdf")
        if PYPDF_AVAILABLE:
            engines.append("pypdf")
        if PYPDF2_AVAILABLE:
            engines.append("pypdf2")
        
        return engines
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about available PDF processing engines."""
        return {
            "available_engines": self.available_engines,
            "preferred_engine": self.preferred_engine,
            "recommended_engine": self._get_recommended_engine()
        }
    
    def _get_recommended_engine(self) -> str:
        """Get the recommended engine based on availability and capabilities."""
        if "pymupdf" in self.available_engines:
            return "pymupdf"  # Best for text extraction and metadata
        elif "pypdf" in self.available_engines:
            return "pypdf"    # Good alternative
        elif "pypdf2" in self.available_engines:
            return "pypdf2"   # Basic functionality
        return "none"
    
    def process_pdf(self, file_path: str, 
                    content_selectors: Optional[Dict[str, Any]] = None,
                    max_pages: Optional[int] = None) -> List[Document]:
        """
        Process a PDF file and extract content into LangChain Documents.
        
        Args:
            file_path: Path to the PDF file
            content_selectors: Optional content filtering options
            max_pages: Maximum number of pages to process (None for all)
        
        Returns:
            List of LangChain Document objects
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Use preferred engine or fall back to best available
        engine = self._select_engine()
        
        if engine == "pymupdf":
            return self._process_with_pymupdf(file_path, content_selectors, max_pages)
        elif engine == "pypdf":
            return self._process_with_pypdf(file_path, content_selectors, max_pages)
        elif engine == "pypdf2":
            return self._process_with_pypdf2(file_path, content_selectors, max_pages)
        else:
            raise RuntimeError(f"No suitable PDF engine available: {engine}")
    
    def _select_engine(self) -> str:
        """Select the best available PDF processing engine."""
        if self.preferred_engine == "auto":
            return self._get_recommended_engine()
        elif self.preferred_engine in self.available_engines:
            return self.preferred_engine
        else:
            return self._get_recommended_engine()
    
    def _process_with_pymupdf(self, file_path: str, 
                             content_selectors: Optional[Dict[str, Any]] = None,
                             max_pages: Optional[int] = None) -> List[Document]:
        """Process PDF using PyMuPDF (fitz)."""
        documents = []
        
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
            
            for page_num in range(pages_to_process):
                try:
                    page = doc.load_page(page_num)
                    
                    # Extract text - handle different return types from PyMuPDF
                    text = self._extract_text_from_page(page)
                    
                    if text and text.strip():
                        # Extract page metadata
                        page_metadata = self._extract_page_metadata(page, page_num, file_path)
                        
                        # Apply content selectors if specified
                        if content_selectors and content_selectors.get("filter_text"):
                            text = self._apply_text_filters(text, content_selectors["filter_text"])
                        
                        documents.append(Document(
                            page_content=text,
                            metadata=page_metadata
                        ))
                    
                    # Extract images if requested
                    if content_selectors and content_selectors.get("extract_images", False):
                        image_info = self._extract_image_info(page)
                        if image_info:
                            documents.append(Document(
                                page_content=f"Page {page_num + 1} contains {len(image_info)} images",
                                metadata={
                                    "source": file_path,
                                    "page_number": page_num + 1,
                                    "type": "image_summary",
                                    "image_count": len(image_info),
                                    "images": image_info
                                }
                            ))
                except Exception as page_error:
                    print(f"Warning: Error processing page {page_num + 1}: {page_error}")
                    continue
            
            doc.close()
            
        except Exception as e:
            print(f"Warning: Error processing PDF with PyMuPDF: {e}")
            print(f"File: {file_path}, Page: {page_num if 'page_num' in locals() else 'unknown'}")
            # Continue processing other pages instead of failing completely
            return documents
        
        return documents
    
    def _process_with_pypdf(self, file_path: str,
                           content_selectors: Optional[Dict[str, Any]] = None,
                           max_pages: Optional[int] = None) -> List[Document]:
        """Process PDF using pypdf."""
        documents = []
        
        try:
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                total_pages = len(reader.pages)
                pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
                
                for page_num in range(pages_to_process):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        page_metadata = self._extract_basic_metadata(reader, page_num, file_path)
                        
                        # Apply content selectors if specified
                        if content_selectors and content_selectors.get("filter_text"):
                            text = self._apply_text_filters(text, content_selectors["filter_text"])
                        
                        documents.append(Document(
                            page_content=text,
                            metadata=page_metadata
                        ))
                        
        except Exception as e:
            raise RuntimeError(f"Error processing PDF with pypdf: {e}")
        
        return documents
    
    def _process_with_pypdf2(self, file_path: str,
                            content_selectors: Optional[Dict[str, Any]] = None,
                            max_pages: Optional[int] = None) -> List[Document]:
        """Process PDF using PyPDF2."""
        documents = []
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
                
                for page_num in range(pages_to_process):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        page_metadata = self._extract_basic_metadata(reader, page_num, file_path)
                        
                        # Apply content selectors if specified
                        if content_selectors and content_selectors.get("filter_text"):
                            text = self._apply_text_filters(text, content_selectors["filter_text"])
                        
                        documents.append(Document(
                            page_content=text,
                            metadata=page_metadata
                        ))
                        
        except Exception as e:
            raise RuntimeError(f"Error processing PDF with PyPDF2: {e}")
        
        return documents
    
    def _extract_page_metadata(self, page, page_num: int, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a PyMuPDF page."""
        metadata = {
            "source": file_path,
            "page_number": page_num + 1,
            "type": "pdf_page",
            "engine": "pymupdf"
        }
        
        # Extract page dimensions
        rect = page.rect
        metadata["page_width"] = rect.width
        metadata["page_height"] = rect.height
        
        # Extract page rotation
        metadata["rotation"] = page.rotation
        
        # Extract page annotations if any (avoid len() on generators)
        try:
            annotations_iter = page.annots()
            if annotations_iter is not None:
                try:
                    # Some versions return an iterator/generator
                    annotation_count = 0
                    for _ in annotations_iter:
                        annotation_count += 1
                except TypeError:
                    # Fallback to attribute-based iteration
                    annotation_count = 0
                    annot = getattr(page, "first_annot", None)
                    while annot is not None:
                        annotation_count += 1
                        annot = getattr(annot, "next", None)
                if annotation_count > 0:
                    metadata["annotation_count"] = annotation_count
        except Exception:
            # If annotations cannot be read, skip silently
            pass
        
        return metadata
    
    def _extract_basic_metadata(self, reader, page_num: int, file_path: str) -> Dict[str, Any]:
        """Extract basic metadata from a PDF page."""
        metadata = {
            "source": file_path,
            "page_number": page_num + 1,
            "type": "pdf_page"
        }
        
        # Try to get document metadata
        try:
            if hasattr(reader, 'metadata'):
                doc_metadata = reader.metadata
                if doc_metadata:
                    metadata["document_title"] = doc_metadata.get('/Title', '')
                    metadata["document_author"] = doc_metadata.get('/Author', '')
                    metadata["document_subject"] = doc_metadata.get('/Subject', '')
                    metadata["document_creator"] = doc_metadata.get('/Creator', '')
                    metadata["document_producer"] = doc_metadata.get('/Producer', '')
        except:
            pass
        
        return metadata
    
    def _extract_image_info(self, page) -> List[Dict[str, Any]]:
        """Extract information about images on a page."""
        image_list = page.get_images()
        image_info = []
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                bbox = img[1]  # bounding box
                image_info.append({
                    "index": img_index,
                    "xref": xref,
                    "bbox": bbox,
                    "width": bbox[2] - bbox[0],
                    "height": bbox[3] - bbox[1]
                })
            except:
                continue
        
        return image_info
    
    def _apply_text_filters(self, text: str, filters: Dict[str, Any]) -> str:
        """Apply text filtering based on content selectors."""
        filtered_text = text
        
        # Apply regex filters
        if "include_patterns" in filters:
            for pattern in filters["include_patterns"]:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    filtered_text = "\n".join(matches)
        
        # Apply exclude patterns
        if "exclude_patterns" in filters:
            for pattern in filters["exclude_patterns"]:
                filtered_text = re.sub(pattern, "", filtered_text, flags=re.IGNORECASE)
        
        # Apply length limits
        if "max_length" in filters and len(filtered_text) > filters["max_length"]:
            filtered_text = filtered_text[:filters["max_length"]] + "..."
        
        return filtered_text
    
    def get_pdf_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic information about a PDF file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        info = {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "file_name": os.path.basename(file_path)
        }
        
        try:
            engine = self._select_engine()
            if engine == "pymupdf":
                doc = fitz.open(file_path)
                info["page_count"] = len(doc)
                info["metadata"] = doc.metadata
                
                # Test text extraction on first page to check compatibility
                try:
                    first_page = doc.load_page(0)
                    sample_text = first_page.get_text()
                    if hasattr(sample_text, '__iter__') and not isinstance(sample_text, str):
                        info["text_type"] = "generator"
                        info["text_sample"] = " ".join(list(sample_text)[:100]) + "..."
                    else:
                        info["text_type"] = "string"
                        info["text_sample"] = str(sample_text)[:100] + "..."
                except Exception as text_error:
                    info["text_extraction_error"] = str(text_error)
                
                doc.close()
            elif engine in ["pypdf", "pypdf2"]:
                with open(file_path, 'rb') as file:
                    if engine == "pypdf":
                        reader = pypdf.PdfReader(file)
                    else:
                        reader = PyPDF2.PdfReader(file)
                    info["page_count"] = len(reader.pages)
                    info["metadata"] = reader.metadata if hasattr(reader, 'metadata') else {}
        except Exception as e:
            info["error"] = str(e)
        
        return info

    def _extract_text_from_page(self, page) -> str:
        """Extract text from a PyMuPDF page with fallback methods."""
        try:
            # Try the standard method first
            text = page.get_text()
            
            # Convert generator to string if needed
            if hasattr(text, '__iter__') and not isinstance(text, str):
                try:
                    text = " ".join(text)
                except Exception as join_error:
                    print(f"Warning: Error joining generator text: {join_error}")
                    # Try to convert generator to list first
                    try:
                        text_list = list(text)
                        text = " ".join(str(item) for item in text_list if item)
                    except Exception as list_error:
                        print(f"Warning: Error converting generator to list: {list_error}")
                        text = ""
            
            if text and text.strip():
                return text
            
            # Fallback: try different text extraction methods
            try:
                text = page.get_text("text")  # Explicitly request text
                if hasattr(text, '__iter__') and not isinstance(text, str):
                    text = " ".join(text)
                
                if text and text.strip():
                    return text
            except Exception as fallback_error:
                print(f"Warning: Fallback text extraction failed: {fallback_error}")
            
            # Fallback: try block extraction
            try:
                blocks = page.get_text("blocks")
                if blocks:
                    text_parts = []
                    for block in blocks:
                        if isinstance(block, (list, tuple)) and len(block) > 6:
                            # Block format: [x0, y0, x1, y1, "text", block_no, block_type]
                            if block[4]:  # text content
                                text_parts.append(str(block[4]))
                    if text_parts:
                        return " ".join(text_parts)
            except Exception as block_error:
                print(f"Warning: Block extraction failed: {block_error}")
            
            return ""
            
        except Exception as e:
            print(f"Warning: Error extracting text from page: {e}")
            return ""


# Convenience function for backward compatibility
def process_pdf_file(file_path: str, **kwargs) -> List[Document]:
    """Convenience function to process a PDF file."""
    processor = PDFContentProcessor()
    return processor.process_pdf(file_path, **kwargs)
