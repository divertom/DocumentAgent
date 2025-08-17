# osha_consumer.py
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document


class OSHAConsumer:
    def __init__(self, base_url="https://www.osha.gov"):
        self.base_url = base_url
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def fetch_page(self, path: str) -> tuple[str, str]:
        """Download HTML content from an OSHA page."""
        url = f"{self.base_url}{path}" if path.startswith("/") else path
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.text, url

    def parse_to_documents(self, html: str, source_url: str) -> list[Document]:
        """Extract OSHA page sections into LangChain Documents."""
        soup = BeautifulSoup(html, "html.parser")
        documents = []

        # Headings and paragraphs
        for section in soup.find_all(["h1", "h2", "h3", "p"]):
            text = section.get_text(strip=True)
            if text:
                documents.append(
                    Document(
                        page_content=text,
                        metadata={"source": source_url, "tag": section.name},
                    )
                )

        # Tables
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

        return documents

    def fetch_and_parse(self, path: str) -> list[Document]:
        """Fetch OSHA page and return LangChain Documents."""
        html, url = self.fetch_page(path)
        return self.parse_to_documents(html, url)

