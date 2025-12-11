#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple
from urllib.parse import urljoin, urldefrag

import requests
from bs4 import BeautifulSoup

# Simple spider that fetches the starting page, follows every link on it once,
# and writes the text content of each linked page to a single file.

USER_AGENT = "WebSpider/1.0 (+https://example.com)"
REQUEST_TIMEOUT = 10


def extract_links(base_url: str, html: bytes) -> List[str]:
    """Return unique, absolute http/https links from the provided HTML."""
    soup = BeautifulSoup(html, "html.parser")
    seen: Set[str] = set()
    links: List[str] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        href, _ = urldefrag(href)  # drop #fragment anchors
        if not href:
            continue
        absolute = urljoin(base_url, href)
        if not absolute.startswith(("http://", "https://")):
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        links.append(absolute)

    return links


def extract_text(html: bytes) -> str:
    """Return visible text from HTML bytes, with scripts/styles removed."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())


def fetch_html(session: requests.Session, url: str) -> Tuple[bytes, str]:
    """Fetch a URL and return (raw_body_bytes, content_type)."""
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "")
    return response.content, content_type


def write_section(file_handle, title: str, body: str) -> None:
    file_handle.write(f"{title}\n")
    file_handle.write(f"{body}\n\n")


def crawl_once(base_url: str, output_path: Path) -> None:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    base_html, _ = fetch_html(session, base_url)
    links = extract_links(base_url, base_html)

    if not links:
        raise SystemExit("No links found on the starting page.")

    with output_path.open("w", encoding="utf-8") as file_handle:
        for link in links:
            try:
                html, content_type = fetch_html(session, link)
                if "html" not in content_type.lower():
                    write_section(file_handle, link, "[Skipped: non-HTML content]")
                    continue
                text = extract_text(html)
                write_section(file_handle, link, text or "[No readable text]")
            except Exception as exc:  # Requests exceptions are noisy enough
                write_section(file_handle, link, f"[Error fetching link: {exc}]")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch all links on a page (one level deep) and write the text of "
            "each linked page into a single file."
        )
    )
    parser.add_argument("url", help="Starting URL to crawl.")
    parser.add_argument(
        "-o",
        "--output",
        default="web_spider_output.txt",
        help="Path to the output text file (default: web_spider_output.txt).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    output_path = Path(args.output).expanduser().resolve()
    crawl_once(args.url, output_path)
    print(f"Wrote link texts to {output_path}")


if __name__ == "__main__":
    main()
