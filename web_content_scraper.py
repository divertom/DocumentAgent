# web_content_scraper.py
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document
from typing import Optional, Dict, Any


class WebContentScraper:
    def __init__(self, base_url: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def fetch_page(self, url: str) -> tuple[str, str]:
        """Download HTML content from a web page."""
        if self.base_url and not url.startswith(('http://', 'https://')):
            full_url = f"{self.base_url}{url}" if url.startswith("/") else f"{self.base_url}/{url}"
        else:
            full_url = url
            
        response = requests.get(full_url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.text, full_url

    def parse_to_documents(self, html: str, source_url: str, 
                          content_selectors: Optional[Dict[str, Any]] = None) -> list[Document]:
        """Extract web page content into LangChain Documents."""
        soup = BeautifulSoup(html, "html.parser")
        documents = []
        
        # Default content selectors if none provided
        if content_selectors is None:
            content_selectors = {
                "headings": ["h1", "h2", "h3", "h4", "h5", "h6"],
                "paragraphs": ["p"],
                "lists": ["ul", "ol"],
                "tables": ["table"],
                "links": ["a"],
                "divs": ["div"]
            }

        # Process headings and paragraphs
        for tag in content_selectors.get("headings", []) + content_selectors.get("paragraphs", []):
            for element in soup.find_all(tag):
                text = element.get_text(strip=True)
                if text:
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": source_url, 
                                "tag": element.name,
                                "element_id": element.get("id", ""),
                                "element_class": " ".join(element.get("class", []))
                            },
                        )
                    )

        # Process lists
        for list_type in content_selectors.get("lists", []):
            for idx, list_elem in enumerate(soup.find_all(list_type)):
                list_items = [li.get_text(strip=True) for li in list_elem.find_all("li")]
                if list_items:
                    list_text = " | ".join(list_items)
                    documents.append(
                        Document(
                            page_content=list_text,
                            metadata={
                                "source": source_url,
                                "type": "list",
                                "list_index": idx,
                                "list_type": list_type
                            },
                        )
                    )

        # Process tables
        for idx, table in enumerate(soup.find_all("table")):
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                if cells:
                    row_text = " | ".join(cells)
                    documents.append(
                        Document(
                            page_content=row_text,
                            metadata={
                                "source": source_url,
                                "type": "table",
                                "table_index": idx,
                                "headers": headers,
                            },
                        )
                    )

        # Process links
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            if link_text:
                documents.append(
                    Document(
                        page_content=f"Link: {link_text} -> {link['href']}",
                        metadata={
                            "source": source_url,
                            "type": "link",
                            "href": link['href'],
                            "link_text": link_text
                        },
                    )
                )

        return documents

    def fetch_and_parse(self, url: str, content_selectors: Optional[Dict[str, Any]] = None) -> list[Document]:
        """Fetch web page and return LangChain Documents."""
        html, full_url = self.fetch_page(url)
        return self.parse_to_documents(html, full_url, content_selectors)

    def set_custom_headers(self, headers: Dict[str, str]):
        """Set custom headers for requests."""
        self.headers.update(headers)

    def set_base_url(self, base_url: str):
        """Set or change the base URL."""
        self.base_url = base_url

