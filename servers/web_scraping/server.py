from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

mcp = FastMCP("web_scraping", log_level="ERROR")


@mcp.tool()
def scrape_url(url: str, selector: Optional[str] = None) -> str:
    """
    Fetch HTML from a URL and extract text. If a CSS selector is provided,
    extract only the elements matching the selector.

    Args:
        url: The URL to scrape.
        selector: Optional CSS selector to filter elements.

    Returns:
        Extracted text or error message.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        if selector:
            elements = soup.select(selector)
            texts = [elem.get_text(strip=True) for elem in elements]
            result = "\n".join(texts)
            return f"Found {len(elements)} element(s). Extracted text:\n{result}"
        else:
            # Extract all text
            text = soup.get_text(strip=True)
            return f"Page text (first 5000 chars):\n{text[:5000]}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error parsing HTML: {str(e)}"


@mcp.tool()
def extract_links(url: str, base_url: Optional[str] = None) -> str:
    """
    Extract all hyperlinks from a webpage.

    Args:
        url: The URL to scrape.
        base_url: Optional base URL to resolve relative links.
                  If not provided, the original URL is used.

    Returns:
        List of links as a formatted string.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # Resolve relative URLs
            if base_url:
                resolved = urljoin(base_url, href)
            else:
                resolved = urljoin(url, href)
            links.append(resolved)

        unique_links = list(set(links))
        return f"Found {len(unique_links)} unique links:\n" + "\n".join(
            unique_links[:50]
        )
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error extracting links: {str(e)}"


@mcp.tool()
def find_elements(html: str, selector: str) -> str:
    """
    Find elements matching a CSS selector within HTML content.

    Args:
        html: HTML string to parse.
        selector: CSS selector.

    Returns:
        Extracted text from matched elements.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.select(selector)
        texts = [elem.get_text(strip=True) for elem in elements]
        if not texts:
            return "No elements found."
        return f"Found {len(elements)} element(s). Texts:\n" + "\n".join(texts)
    except Exception as e:
        return f"Error parsing HTML: {str(e)}"


@mcp.tool()
def scrape_with_selenium(
    url: str, selector: Optional[str] = None, wait_time: int = 10
) -> str:
    """
    Fetch dynamically rendered HTML using Selenium WebDriver (Chrome).

    Args:
        url: The URL to scrape.
        selector: Optional CSS selector to filter elements after page load.
        wait_time: Maximum time to wait for page load (seconds).

    Returns:
        Extracted text or error message.
    """
    try:
        options = Options()
        options.add_argument("--headless")  # Run in background
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.get(url)
        # Wait for page to load
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        if selector:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            texts = [elem.text for elem in elements]
            result = "\n".join(texts)
            driver.quit()
            return f"Found {len(elements)} element(s). Extracted text:\n{result}"
        else:
            # Extract all text from body
            body = driver.find_element(By.TAG_NAME, "body")
            text = body.text[:5000]
            driver.quit()
            return f"Page text (first 5000 chars):\n{text}"
    except Exception as e:
        return f"Error with Selenium scraping: {str(e)}"


@mcp.tool()
def extract_tables(url: str, output_path: Optional[str] = None) -> str:
    """
    Extract HTML tables from a webpage and optionally save as CSV.

    Args:
        url: The URL to scrape.
        output_path: Optional path to save tables as CSV (multiple files).

    Returns:
        Summary of extracted tables.
    """
    try:
        import pandas as pd

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")
        if not tables:
            return "No tables found."
        result = []
        for i, table in enumerate(tables):
            df = pd.read_html(str(table))[0]
            if output_path:
                # Save each table as separate CSV
                if len(tables) > 1:
                    base = Path(output_path).stem
                    ext = Path(output_path).suffix
                    table_path = f"{base}_table{i+1}{ext}"
                else:
                    table_path = output_path
                df.to_csv(table_path, index=False)
                result.append(f"Table {i+1} saved to {table_path}")
            else:
                result.append(f"Table {i+1} shape: {df.shape}")
        return "\n".join(result)
    except Exception as e:
        return f"Error extracting tables: {str(e)}"


if __name__ == "__main__":
    mcp.run()
