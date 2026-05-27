from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.config import HTTP_HEADERS, REQUEST_TIMEOUT_SECONDS
from app.storage import ParsedItem, infer_category, parse_amount, save_items


def clean_text(value: str) -> str:
    return " ".join(value.split())


def node_text(node) -> str:
    return clean_text(node.get_text(" ", strip=True)) if node else ""


def page_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return clean_text(soup.title.string)
    heading = soup.find("h1")
    if heading:
        return node_text(heading)
    return "Untitled source"


def parse_items(url: str, html: str, limit: int = 5) -> list[ParsedItem]:
    soup = BeautifulSoup(html, "html.parser")
    if "books.toscrape.com" in url:
        return parse_book_cards(url, soup, limit)
    return [generic_item(url, soup, html)]


def parse_book_cards(url: str, soup: BeautifulSoup, limit: int) -> list[ParsedItem]:
    items: list[ParsedItem] = []
    category = infer_category(url)
    for card in soup.select("article.product_pod"):
        title_node = card.select_one("h3 a[title]")
        title = clean_text(title_node.get("title", "")) if title_node else ""
        if not title:
            continue
        href = title_node.get("href", "") if title_node else ""
        item_url = urljoin(url, href)
        price = node_text(card.select_one(".price_color")) or None
        availability = node_text(card.select_one(".availability"))
        rating_node = card.select_one("p.star-rating")
        rating_classes = [cls for cls in rating_node.get("class", []) if cls != "star-rating"] if rating_node else []
        meta = ", ".join(part for part in [availability, " ".join(rating_classes)] if part) or None
        items.append(
            ParsedItem(
                source_url=url,
                item_url=item_url,
                title=title,
                description=f"{title}. {availability or 'Availability unknown.'}",
                category=category,
                amount=parse_amount(price),
                meta=meta,
            )
        )
        if len(items) >= limit:
            break
    return items


def generic_item(url: str, soup: BeautifulSoup, html: str) -> ParsedItem:
    title = page_title(html)
    description = ""
    for tag in soup.select("p, article, main, div"):
        text = node_text(tag)
        if len(text) >= 40:
            description = text[:400]
            break
    description = description or title
    return ParsedItem(
        source_url=url,
        item_url=url,
        title=title,
        description=description,
        category=infer_category(url),
        amount=1.0,
        meta="Generic HTML page fallback",
    )


def parse_and_save(url: str, parsed_by: str) -> dict[str, Any]:
    response = requests.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    html = response.text
    title = page_title(html)
    items = parse_items(url, html)
    saved_count = save_items(items, parsed_by)
    return {
        "url": url,
        "title": title,
        "parsed_by": parsed_by,
        "extracted_count": len(items),
        "saved_count": saved_count,
        "status": "ok",
    }
