# test_pdf_fix.py
# Test the fixed PDF processor

try:
    from pdf_content_processor import PDFContentProcessor
    print("✅ PDF processor imported successfully!")
    
    # Create processor
    processor = PDFContentProcessor()
    print("✅ PDF processor created successfully!")
    
    # Test with the specific PDF that was causing issues
    pdf_path = r"C:\Git\OSHA\1910.23 - Ladders. _ Occupational Safety and Health Administration.pdf"
    
    try:
        # Get PDF info first
        print(f"\n📄 Getting PDF info for: {pdf_path}")
        pdf_info = processor.get_pdf_info(pdf_path)
        print(f"✅ PDF Info: {pdf_info}")
        
        # Test processing
        print(f"\n🔄 Processing PDF...")
        docs = processor.process_pdf(pdf_path, max_pages=2)  # Just test first 2 pages
        print(f"✅ Successfully extracted {len(docs)} document chunks")
        
        # Show sample content
        for i, doc in enumerate(docs[:2]):
            print(f"\n📄 Document {i+1}:")
            print(f"   Page: {doc.metadata.get('page_number', 'unknown')}")
            print(f"   Content preview: {doc.page_content[:200]}...")
            print(f"   Metadata keys: {list(doc.metadata.keys())}")
            
    except FileNotFoundError:
        print(f"❌ PDF file not found: {pdf_path}")
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Error importing PDF processor: {e}")
    import traceback
    traceback.print_exc()
