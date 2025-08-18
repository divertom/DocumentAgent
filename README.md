# Document Agent - Refactored Architecture

This project has been refactored to separate concerns between generic web content scraping and OSHA-specific document processing.

## Architecture Changes

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

### 2. OSHA-Specific Document Storage (`OshaDocumentStorage.py`)

All OSHA-specific functionality has been moved to a dedicated class that uses the generic scraper:

**Key Features:**
- **OSHA-specific metadata**: Regulation numbers, types, and agency information
- **Enhanced content processing**: OSHA-specific content selectors and headers
- **Regulation classification**: Automatic classification of regulation types (General Industry, Construction, Maritime, etc.)
- **Vector database integration**: Chroma DB storage with Ollama embeddings
- **Search functionality**: Semantic search across stored OSHA documents

**Usage Examples:**
```python
from OshaDocumentStorage import OSHADocumentProcessor

# Create processor
processor = OSHADocumentProcessor()

# Process single regulation
docs = processor.process_osha_regulation("/laws-regs/regulations/standardnumber/1910/1910.23")

# Ingest multiple regulations
paths = [
    "/laws-regs/regulations/standardnumber/1910/1910.23",
    "/laws-regs/regulations/standardnumber/1910/1910.95"
]
db_path = processor.ingest_osha_documents(paths)

# Search documents
results = processor.search_osha_documents("noise exposure limits", db_path)
```

## File Structure

```
DocumentAgent/
├── web_content_scraper.py          # Generic web content scraper
├── OshaDocumentStorage.py          # OSHA-specific document processing
├── example_web_scraper.py          # Usage examples for the generic scraper
├── environment.yml                  # Conda environment
├── environment_full.yml            # Full environment with all dependencies
└── README.md                       # This file
```

## Benefits of Refactoring

1. **Separation of Concerns**: Generic scraping logic is separate from OSHA-specific processing
2. **Reusability**: The web scraper can be used for any website, not just OSHA
3. **Maintainability**: Easier to update scraping logic without affecting OSHA processing
4. **Extensibility**: Easy to add support for new document types or websites
5. **Testing**: Generic scraper can be tested independently

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

# Customize content extraction
docs = scraper.fetch_and_parse(
    "https://any-website.com/page",
    content_selectors={"headings": ["h1"], "content": ["div.content"]}
)
```

## Dependencies

The refactored code maintains the same dependencies as before:
- `requests` for HTTP requests
- `beautifulsoup4` for HTML parsing
- `langchain` for document processing
- `chromadb` for vector storage
- `ollama` for embeddings

## Running Examples

```bash
# Test the generic web scraper
python example_web_scraper.py

# Test OSHA document processing
python OshaDocumentStorage.py
```

## Future Enhancements

The generic architecture makes it easy to add:
- Support for different content types (PDFs, APIs, etc.)
- Custom content processors for specific websites
- Advanced metadata extraction
- Content validation and quality checks
- Rate limiting and polite scraping
- Proxy support for distributed scraping
