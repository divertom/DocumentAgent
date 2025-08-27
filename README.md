# Document Agent - Refactored Architecture

This project has been refactored to separate concerns between generic web content scraping, PDF processing, and OSHA-specific document processing.

## Architecture Changes

### 0. Web Application (`web_app.py`)

A modern web interface for DocumentAgent that provides:

**Key Features:**
- **PDF Upload & Processing**: Drag-and-drop PDF upload with automatic text extraction
- **Vector Database Storage**: Documents are processed and stored in a Chroma vector database
- **AI Chat Interface**: Chat with your documents using local Ollama models
- **Modern UI**: Responsive design with Tailwind CSS and Font Awesome icons
- **Document Management**: View, search, and delete processed documents
- **Real-time Processing**: Live feedback during PDF processing and chat

**Quick Start:**
```bash
# Install dependencies
conda env create -f environment.yml
conda activate DocumentAgent

# Or use the installer script
python install_dependencies.py

# Start the web application
python web_app.py

# Open http://localhost:5000 in your browser
```

### 1. Generic Web Content Scraper (`web_content_scraper.py`)

The `osha_consumer.py` has been refactored into a generic `WebContentScraper` class that can handle any website:

**Key Features:**
- **Flexible URL handling**: Works with or without base URLs
- **Customizable content extraction**: Configurable HTML selectors for different content types
- **Enhanced metadata**: Rich metadata extraction including element IDs, classes, and types
- **Extensible**: Easy to add new content types and processing logic

**Usage Examples:**
```python
from web_content_scraper import WebContentScraper

# Basic usage with base URL
scraper = WebContentScraper(base_url="https://example.com")
docs = scraper.fetch_and_parse("/page")

# Full URL usage
scraper = WebContentScraper()
docs = scraper.fetch_and_parse("https://example.com/page")

# Custom content selectors
custom_selectors = {
    "headings": ["h1", "h2"],
    "paragraphs": ["p"],
    "tables": ["table"]
}
docs = scraper.fetch_and_parse(url, content_selectors=custom_selectors)
```

### 2. Generic PDF Content Processor (`pdf_content_processor.py`)

A new generic PDF processing module that can handle various PDF formats:

**Key Features:**
- **Multiple PDF engines**: Supports PyMuPDF (fitz), pypdf, and PyPDF2
- **Automatic engine selection**: Automatically chooses the best available engine
- **Content filtering**: Configurable text filtering and pattern matching
- **Rich metadata extraction**: Page dimensions, annotations, images, document metadata
- **Flexible processing**: Page limits, content selectors, and custom filters

**Usage Examples:**
```python
from pdf_content_processor import PDFContentProcessor

# Basic PDF processing
processor = PDFContentProcessor()
docs = processor.process_pdf("document.pdf")

# With content filtering
content_selectors = {
    "filter_text": {
        "include_patterns": [r"OSHA", r"regulation"],
        "exclude_patterns": [r"page \d+", r"footer"],
        "max_length": 1000
    },
    "extract_images": True
}
docs = processor.process_pdf("document.pdf", content_selectors=content_selectors)

# Process specific pages only
docs = processor.process_pdf("document.pdf", max_pages=5)
```

### 3. OSHA-Specific Document Storage (`OshaDocumentStorage.py`)

All OSHA-specific functionality has been moved to a dedicated class that uses both the generic scraper and PDF processor:

**Key Features:**
- **OSHA-specific metadata**: Regulation numbers, types, and agency information
- **Enhanced content processing**: OSHA-specific content selectors and headers
- **Regulation classification**: Automatic classification of regulation types (General Industry, Construction, Maritime, etc.)
- **Vector database integration**: Chroma DB storage with Ollama embeddings
- **Search functionality**: Semantic search across stored OSHA documents
- **Mixed content support**: Process both web pages and PDFs simultaneously

**Usage Examples:**
```python
from OshaDocumentStorage import OSHADocumentProcessor

# Create processor
processor = OSHADocumentProcessor()

# Process single regulation (web page)
docs = processor.process_osha_regulation("/laws-regs/regulations/standardnumber/1910/1910.23")

# Process single PDF
docs = processor.process_osha_pdf("osha_regulation_1910.23.pdf")

# Ingest multiple regulations (web pages)
web_paths = [
    "/laws-regs/regulations/standardnumber/1910/1910.23",
    "/laws-regs/regulations/standardnumber/1910/1910.95"
]
db_path = processor.ingest_osha_documents(web_paths)

# Ingest mixed content (web pages + PDFs)
pdf_paths = ["osha_regulation_1910.23.pdf", "osha_guidance_1910.95.pdf"]
db_path = processor.ingest_mixed_osha_content(
    web_paths=web_paths,
    pdf_paths=pdf_paths
)

# Search documents
results = processor.search_osha_documents("noise exposure limits", db_path)
```

## File Structure

```
DocumentAgent/
├── web_content_scraper.py          # Generic web content scraper
├── pdf_content_processor.py        # Generic PDF content processor
├── OshaDocumentStorage.py          # OSHA-specific document processing
├── example_web_scraper.py          # Usage examples for the generic scraper
├── example_pdf_processor.py        # Usage examples for the PDF processor
├── environment.yml                  # Conda environment with all dependencies
├── environment_full.yml            # Full environment with all dependencies
└── README.md                       # This file
```

## Benefits of Refactoring

1. **Separation of Concerns**: Generic scraping and PDF processing logic is separate from OSHA-specific processing
2. **Reusability**: Both modules can be used for any website or PDF, not just OSHA
3. **Maintainability**: Easier to update processing logic without affecting OSHA processing
4. **Extensibility**: Easy to add support for new document types or content sources
5. **Testing**: Generic modules can be tested independently
6. **Mixed Content Support**: Process both web pages and PDFs in the same workflow

## Migration Guide

### For Existing OSHA Users

The legacy `ingest_osha()` function is still available for backward compatibility:

```python
# Old way (still works)
from OshaDocumentStorage import ingest_osha
db_path = ingest_osha("/laws-regs/regulations/standardnumber/1910/1910.23")

# New way (recommended)
from OshaDocumentStorage import OSHADocumentProcessor
processor = OSHADocumentProcessor()
db_path = processor.ingest_osha_documents(["/laws-regs/regulations/standardnumber/1910/1910.23"])
```

### For New Web Scraping Projects

Use the generic scraper for any website:

```python
from web_content_scraper import WebContentScraper

# Scrape any website
scraper = WebContentScraper()
docs = scraper.fetch_and_parse("https://any-website.com/page")
```

### For New PDF Processing Projects

Use the generic PDF processor for any PDF:

```python
from pdf_content_processor import PDFContentProcessor

# Process any PDF
processor = PDFContentProcessor()
docs = processor.process_pdf("any-document.pdf")
```

## Dependencies

The refactored code maintains the same dependencies as before, plus new PDF processing libraries:
- `requests` for HTTP requests
- `beautifulsoup4` for HTML parsing
- `lxml` for XML/HTML processing
- **`PyMuPDF` (fitz) for advanced PDF processing**
- **`pypdf` for PDF processing**
- **`PyPDF2` for PDF processing (fallback)**
- `langchain` for document processing
- `chromadb` for vector storage
- `ollama` for embeddings

## Running Examples

```bash
# Test the generic web scraper
python example_web_scraper.py

# Test the PDF processor
python example_pdf_processor.py

# Test OSHA document processing
python OshaDocumentStorage.py
```

## Future Enhancements

The generic architecture makes it easy to add:
- Support for different content types (Word docs, Excel files, etc.)
- Custom content processors for specific websites or document types
- Advanced metadata extraction and content validation
- Content quality checks and filtering
- Rate limiting and polite scraping
- Proxy support for distributed processing
- OCR support for scanned PDFs
- Multi-language document processing
