# example_web_scraper.py
# Example usage of the generic web content scraper

from web_content_scraper import WebContentScraper
from langchain.schema import Document


def example_basic_scraping():
    """Basic example of scraping a website."""
    print("=== Basic Web Scraping Example ===")
    
    # Create scraper with base URL
    scraper = WebContentScraper(base_url="https://example.com")
    
    # Fetch and parse a page
    docs = scraper.fetch_and_parse("/")
    
    print(f"Extracted {len(docs)} document chunks")
    for i, doc in enumerate(docs[:3]):  # Show first 3
        print(f"  {i+1}. {doc.page_content[:100]}...")
        print(f"     Metadata: {doc.metadata}")


def example_custom_selectors():
    """Example with custom content selectors."""
    print("\n=== Custom Selectors Example ===")
    
    # Create scraper without base URL (for full URLs)
    scraper = WebContentScraper()
    
    # Custom selectors for specific content
    custom_selectors = {
        "headings": ["h1", "h2"],  # Only main headings
        "paragraphs": ["p"],       # Only paragraphs
        "tables": ["table"],       # Only tables
        # Skip lists and links for this example
    }
    
    # Scrape a specific page
    docs = scraper.fetch_and_parse(
        "https://httpbin.org/html",
        content_selectors=custom_selectors
    )
    
    print(f"Extracted {len(docs)} document chunks with custom selectors")
    for i, doc in enumerate(docs[:3]):
        print(f"  {i+1}. {doc.page_content[:100]}...")
        print(f"     Type: {doc.metadata.get('tag', 'unknown')}")


def example_osha_scraping():
    """Example of using the generic scraper for OSHA content."""
    print("\n=== OSHA Scraping Example ===")
    
    # Create scraper for OSHA
    osha_scraper = WebContentScraper(base_url="https://www.osha.gov")
    
    # OSHA-specific content selectors
    osha_selectors = {
        "headings": ["h1", "h2", "h3", "h4"],
        "paragraphs": ["p"],
        "lists": ["ul", "ol"],
        "tables": ["table"],
        "links": ["a"]
    }
    
    # Scrape an OSHA regulation page
    try:
        docs = osha_scraper.fetch_and_parse(
            "/laws-regs/regulations/standardnumber/1910/1910.23",
            content_selectors=osha_selectors
        )
        
        print(f"Extracted {len(docs)} document chunks from OSHA")
        for i, doc in enumerate(docs[:3]):
            print(f"  {i+1}. {doc.page_content[:100]}...")
            print(f"     Source: {doc.metadata.get('source', 'unknown')}")
            
    except Exception as e:
        print(f"Error scraping OSHA page: {e}")


def example_multiple_sites():
    """Example of scraping multiple different websites."""
    print("\n=== Multiple Sites Example ===")
    
    # Create generic scraper
    scraper = WebContentScraper()
    
    # Different websites to scrape
    sites = [
        "https://httpbin.org/json",
        "https://httpbin.org/xml",
        "https://httpbin.org/robots.txt"
    ]
    
    for site in sites:
        try:
            print(f"\nScraping: {site}")
            docs = scraper.fetch_and_parse(site)
            print(f"  Extracted {len(docs)} chunks")
            
            # Show first chunk if available
            if docs:
                first_doc = docs[0]
                print(f"  First chunk: {first_doc.page_content[:100]}...")
                
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    print("Generic Web Content Scraper Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_scraping()
    example_custom_selectors()
    example_osha_scraping()
    example_multiple_sites()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
