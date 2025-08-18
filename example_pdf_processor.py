# example_pdf_processor.py
# Example usage of the PDF content processor

from pdf_content_processor import PDFContentProcessor
from langchain.schema import Document


def example_basic_pdf_processing():
    """Basic example of processing a PDF file."""
    print("=== Basic PDF Processing Example ===")
    
    # Create PDF processor
    processor = PDFContentProcessor()
    
    # Show available engines
    engine_info = processor.get_engine_info()
    print(f"Available engines: {engine_info['available_engines']}")
    print(f"Recommended engine: {engine_info['recommended_engine']}")
    
    # Example PDF path (replace with actual PDF file)
    pdf_path = "C:\\Git\\OSHA\\1910.23 - Ladders. _ Occupational Safety and Health Administration.pdf" 
    
    try:
        # Get PDF information
        pdf_info = processor.get_pdf_info(pdf_path)
        print(f"PDF Info: {pdf_info}")
        
        # Process PDF
        docs = processor.process_pdf(pdf_path)
        print(f"Extracted {len(docs)} document chunks")
        
        # Show first few documents
        for i, doc in enumerate(docs[:3]):
            print(f"  {i+1}. Page {doc.metadata.get('page_number', 'unknown')}")
            print(f"     Content preview: {doc.page_content[:100]}...")
            print(f"     Metadata: {doc.metadata}")
            
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
        print("Please provide a valid PDF file path")
    except Exception as e:
        print(f"Error processing PDF: {e}")


def example_pdf_with_content_selectors():
    """Example with custom content selectors and filtering."""
    print("\n=== PDF Processing with Content Selectors ===")
    
    processor = PDFContentProcessor()
    
    # Custom content selectors
    content_selectors = {
        "filter_text": {
            "include_patterns": [r"OSHA", r"regulation", r"1910\.\d+"],  # Only include OSHA-related content
            "exclude_patterns": [r"page \d+", r"footer"],  # Exclude page numbers and footers
            "max_length": 1000  # Limit text length
        },
        "extract_images": True  # Also extract image information
    }
    
    pdf_path = "example.pdf"  # Change this to your PDF file
    
    try:
        docs = processor.process_pdf(pdf_path, content_selectors=content_selectors)
        print(f"Extracted {len(docs)} filtered document chunks")
        
        for i, doc in enumerate(docs[:3]):
            print(f"  {i+1}. Type: {doc.metadata.get('type', 'unknown')}")
            print(f"     Content: {doc.page_content[:150]}...")
            
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")


def example_pdf_page_limits():
    """Example of processing only specific pages."""
    print("\n=== PDF Processing with Page Limits ===")
    
    processor = PDFContentProcessor()
    
    pdf_path = "example.pdf"  # Change this to your PDF file
    
    try:
        # Process only first 3 pages
        docs = processor.process_pdf(pdf_path, max_pages=3)
        print(f"Processed first 3 pages: {len(docs)} chunks")
        
        # Process only first page
        docs_single = processor.process_pdf(pdf_path, max_pages=1)
        print(f"Processed first page only: {len(docs_single)} chunks")
        
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")


def example_osha_pdf_integration():
    """Example of using PDF processor with OSHA document storage."""
    print("\n=== OSHA PDF Integration Example ===")
    
    try:
        from OshaDocumentStorage import OSHADocumentProcessor
        
        # Create OSHA processor
        osha_processor = OSHADocumentProcessor()
        
        # Example PDF paths (replace with actual OSHA PDF files)
        pdf_paths = [
            # "osha_regulation_1910.23.pdf",
            # "osha_guidance_1910.95.pdf"
        ]
        
        if pdf_paths:
            print("Processing OSHA PDFs...")
            for pdf_path in pdf_paths:
                try:
                    docs = osha_processor.process_osha_pdf(pdf_path)
                    print(f"  - {pdf_path}: {len(docs)} chunks")
                    
                    # Show metadata
                    if docs:
                        first_doc = docs[0]
                        print(f"    Regulation: {first_doc.metadata.get('regulation_number', 'Unknown')}")
                        print(f"    Type: {first_doc.metadata.get('regulation_type', 'Unknown')}")
                        
                except Exception as e:
                    print(f"  - Error processing {pdf_path}: {e}")
        else:
            print("No PDF paths provided. Please add actual OSHA PDF file paths.")
            
    except ImportError:
        print("OSHA Document Storage not available")
    except Exception as e:
        print(f"Error: {e}")


def example_multiple_pdfs():
    """Example of processing multiple PDF files."""
    print("\n=== Multiple PDF Processing Example ===")
    
    processor = PDFContentProcessor()
    
    # Example PDF paths (replace with actual PDF files)
    pdf_paths = [
        # "document1.pdf",
        # "document2.pdf",
        # "document3.pdf"
    ]
    
    if pdf_paths:
        all_docs = []
        
        for pdf_path in pdf_paths:
            try:
                print(f"\nProcessing: {pdf_path}")
                docs = processor.process_pdf(pdf_path)
                all_docs.extend(docs)
                print(f"  Extracted {len(docs)} chunks")
                
            except Exception as e:
                print(f"  Error: {e}")
        
        print(f"\nTotal documents processed: {len(all_docs)}")
        
    else:
        print("No PDF paths provided. Please add actual PDF file paths.")


if __name__ == "__main__":
    print("PDF Content Processor Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_pdf_processing()
    # example_pdf_with_content_selectors()
    # example_pdf_page_limits()
    # example_osha_pdf_integration()
    # example_multiple_pdfs()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo use with actual PDFs:")
    print("1. Update the pdf_path variables with your PDF file paths")
    print("2. Run the examples again")
    print("3. The processor will automatically detect and use the best available PDF engine")
