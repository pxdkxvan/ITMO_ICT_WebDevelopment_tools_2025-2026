from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, MetaData, String, Table, Text, create_engine
from sqlalchemy import select
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError

REQUEST_TIMEOUT_SECONDS = 15
MAX_PROJECTS_PER_SOURCE = 5
PACKAGE_DIR = Path(__file__).resolve().parent
ROOT_DIR = PACKAGE_DIR.parent
LR1_LAB_DIR = ROOT_DIR.parent / "lr_1"
RESULTS_DIR = ROOT_DIR / "results"
PARSER_USERNAME = "parser_bot@example.local"
PARSER_FULL_NAME = "LR2 Parser Bot"
PARSER_PASSWORD_HASH = "lr2-parser-no-login"
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ITMO-LR2-project-parser/1.0)"}

DEFAULT_URLS = [
    "https://books.toscrape.com/catalogue/page-1.html",
    "https://books.toscrape.com/catalogue/page-2.html",
    "https://books.toscrape.com/catalogue/page-3.html",
    "https://books.toscrape.com/catalogue/page-4.html",
    "https://books.toscrape.com/catalogue/page-5.html",
    "https://books.toscrape.com/catalogue/page-6.html",
]

metadata = MetaData()

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("full_name", String, nullable=False),
    Column("is_active", Boolean, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

category_table = Table(
    "category",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
)

tag_table = Table(
    "tag",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
)

transaction_table = Table(
    "transaction",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("amount", Float, nullable=False),
    Column("description", String, nullable=False),
    Column("transaction_date", Date, nullable=False),
    Column("kind", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.id"), nullable=False),
)

transaction_tag_link_table = Table(
    "transactiontaglink",
    metadata,
    Column("transaction_id", Integer, ForeignKey("transaction.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
    Column("importance", Integer, nullable=False),
    Column("note", Text, nullable=False),
)


@dataclass(frozen=True)
class ProjectItem:
    source_url: str
    project_url: str
    title: str
    description: str
    category: str
    budget: str | None = None
    meta: str | None = None


@dataclass(frozen=True)
class ParseResult:
    url: str
    title: str | None
    parsed_by: str
    status: str
    extracted_count: int = 0
    saved_count: int = 0
    error: str | None = None


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url and "+psycopg2" not in url:
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def get_database_url() -> str:
    candidates = [
        os.getenv("DATABASE_URL"),
        read_env_file(ROOT_DIR / ".env").get("DATABASE_URL"),
        read_env_file(LR1_LAB_DIR / ".env").get("DATABASE_URL"),
        read_env_file(LR1_LAB_DIR / ".env.example").get("DATABASE_URL"),
    ]

    for candidate in candidates:
        if candidate:
            return normalize_database_url(candidate)

    return "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"


def create_db_engine() -> Engine:
    return create_engine(get_database_url(), pool_pre_ping=True)


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


def source_category(url: str) -> str:
    path = urlparse(url).path.lower()
    if "books.toscrape.com" in url:
        match = re.search(r"page-(\d+)\.html", path)
        page = match.group(1) if match else "1"
        return f"Books to Scrape Page {page}"
    if "news.ycombinator.com" in url:
        match = re.search(r"[?&]p=(\d+)", url)
        page = match.group(1) if match else "1"
        return f"Hacker News Page {page}"
    if "peopleperhour.com" in url:
        if "programming-coding" in path:
            return "PeoplePerHour Programming"
        if "website-development" in path:
            return "PeoplePerHour Website Development"
        if "e-commerce-cms-development" in path:
            return "PeoplePerHour E-Commerce"
        if "artificial-intelligence-agent-development" in path:
            return "PeoplePerHour AI Agents"
        if "artificial-intelligence-website-development" in path:
            return "PeoplePerHour AI Websites"
        return "PeoplePerHour Technology"
    return "Parsed Freelance Projects"


def parse_project_items(url: str, html: str, limit: int = MAX_PROJECTS_PER_SOURCE) -> list[ProjectItem]:
    soup = BeautifulSoup(html, "html.parser")
    if "books.toscrape.com" in url:
        return parse_books_items(url, soup, limit)
    if "news.ycombinator.com" in url:
        return parse_hackernews_items(url, soup, limit)
    if "peopleperhour.com" in url:
        return parse_peopleperhour_projects(url, soup, limit)
    return []


def parse_books_items(url: str, soup: BeautifulSoup, limit: int) -> list[ProjectItem]:
    items: list[ProjectItem] = []
    category = source_category(url)
    for card in soup.select("article.product_pod"):
        title_node = card.select_one("h3 a[title]")
        title = clean_text(title_node.get("title", "")) if title_node else ""
        if not title:
            continue

        href = title_node.get("href", "") if title_node else ""
        project_url = urljoin(url, href)
        price = node_text(card.select_one(".price_color")) or None
        availability = node_text(card.select_one(".availability"))
        rating_node = card.select_one("p.star-rating")
        rating = ""
        if rating_node:
            rating_classes = [cls for cls in rating_node.get("class", []) if cls != "star-rating"]
            rating = " ".join(rating_classes)
        meta = ", ".join(part for part in [availability, rating] if part) or None
        items.append(
            ProjectItem(
                source_url=url,
                project_url=project_url,
                title=title,
                description=f"{title}. {availability or 'Availability unknown.'}",
                category=category,
                budget=price,
                meta=meta or "Books to Scrape product card",
            )
        )
        if len(items) >= limit:
            break
    return items


def parse_hackernews_items(url: str, soup: BeautifulSoup, limit: int) -> list[ProjectItem]:
    items: list[ProjectItem] = []
    category = source_category(url)
    for row in soup.select("tr.athing"):
        title_link = row.select_one("span.titleline a[href]")
        title = node_text(title_link)
        if not title:
            continue

        project_url = urljoin(url, title_link.get("href", "")) if title_link else url
        subtext_row = row.find_next_sibling("tr")
        subtext = node_text(subtext_row)
        items.append(
            ProjectItem(
                source_url=url,
                project_url=project_url,
                title=title,
                description=subtext or title,
                category=category,
                budget=None,
                meta="Hacker News listing item",
            )
        )
        if len(items) >= limit:
            break
    return items


def parse_peopleperhour_projects(url: str, soup: BeautifulSoup, limit: int) -> list[ProjectItem]:
    items: list[ProjectItem] = []
    seen_urls: set[str] = set()
    category = source_category(url)
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        title = node_text(link)
        if len(title) < 25 or "freelance-jobs" not in href:
            continue
        if href.startswith("/freelance-jobs/"):
            continue

        project_url = urljoin(url, href)
        if project_url in seen_urls:
            continue
        seen_urls.add(project_url)

        container = link
        for _ in range(4):
            if container.parent is None:
                break
            container = container.parent
        container_text = node_text(container)
        description = container_text if len(container_text) > len(title) else title
        budget = extract_budget(container_text)
        items.append(
            ProjectItem(
                source_url=url,
                project_url=project_url,
                title=title,
                description=description,
                category=category,
                budget=budget,
                meta="PeoplePerHour public project card",
            )
        )
        if len(items) >= limit:
            break
    return items


def extract_budget(text_value: str) -> str | None:
    match = re.search(r"([$€£]\s?\d+(?:[.,]\d+)?)", text_value)
    return match.group(1) if match else None


def parse_budget_amount(raw_budget: str | None) -> float:
    if not raw_budget:
        return 1.0
    normalized = raw_budget.replace(" ", "").replace(",", ".")
    match = re.search(r"(\d+(?:\.\d+)?)", normalized)
    if not match:
        return 1.0
    value = float(match.group(1))
    return value if value > 0 else 1.0


def save_projects(projects: list[ProjectItem], parsed_by: str, engine: Engine | None = None) -> int:
    if not projects:
        return 0

    own_engine = engine is None
    engine = engine or create_db_engine()
    saved_count = 0

    try:
        with engine.begin() as connection:
            owner_id = ensure_parser_user(connection)
            category_ids: dict[str, int] = {}
            parser_tag_id = ensure_tag(connection, owner_id, f"parsed:{parsed_by}")

            for project in projects:
                category_id = category_ids.get(project.category)
                if category_id is None:
                    category_id = ensure_category(connection, owner_id, project.category)
                    category_ids[project.category] = category_id

                transaction_id = upsert_transaction(connection, owner_id, category_id, project, parsed_by)
                ensure_transaction_tag(connection, transaction_id, parser_tag_id, project)
                saved_count += 1
    finally:
        if own_engine:
            engine.dispose()
    return saved_count


def ensure_parser_user(connection: Connection) -> int:
    user_id = connection.scalar(select(user_table.c.id).where(user_table.c.email == PARSER_USERNAME))
    if user_id is not None:
        return int(user_id)

    try:
        return int(
            connection.execute(
                user_table.insert().values(
                    email=PARSER_USERNAME,
                    full_name=PARSER_FULL_NAME,
                    hashed_password=PARSER_PASSWORD_HASH,
                    is_active=True,
                    created_at=datetime.utcnow(),
                )
            ).inserted_primary_key[0]
        )
    except IntegrityError:
        user_id = connection.scalar(select(user_table.c.id).where(user_table.c.email == PARSER_USERNAME))
        if user_id is None:
            raise
        return int(user_id)


def ensure_category(connection: Connection, user_id: int, name: str) -> int:
    trimmed_name = name[:255]
    category_id = connection.scalar(
        select(category_table.c.id).where(
            category_table.c.user_id == user_id,
            category_table.c.name == trimmed_name,
            category_table.c.kind == "expense",
        )
    )
    if category_id is not None:
        return int(category_id)

    try:
        return int(
            connection.execute(
                category_table.insert().values(name=trimmed_name, kind="expense", user_id=user_id)
            ).inserted_primary_key[0]
        )
    except IntegrityError:
        category_id = connection.scalar(
            select(category_table.c.id).where(
                category_table.c.user_id == user_id,
                category_table.c.name == trimmed_name,
                category_table.c.kind == "expense",
            )
        )
        if category_id is None:
            raise
        return int(category_id)


def ensure_tag(connection: Connection, user_id: int, name: str) -> int:
    trimmed_name = name[:255]
    tag_id = connection.scalar(
        select(tag_table.c.id).where(tag_table.c.user_id == user_id, tag_table.c.name == trimmed_name)
    )
    if tag_id is not None:
        return int(tag_id)

    try:
        return int(connection.execute(tag_table.insert().values(name=trimmed_name, user_id=user_id)).inserted_primary_key[0])
    except IntegrityError:
        tag_id = connection.scalar(
            select(tag_table.c.id).where(tag_table.c.user_id == user_id, tag_table.c.name == trimmed_name)
        )
        if tag_id is None:
            raise
        return int(tag_id)


def upsert_transaction(
    connection: Connection,
    user_id: int,
    category_id: int,
    project: ProjectItem,
    parsed_by: str,
) -> int:
    source_id = build_source_id(project, parsed_by)
    description = build_transaction_description(project, parsed_by, source_id)
    existing_transaction_id = connection.scalar(
        select(transaction_table.c.id).where(
            transaction_table.c.user_id == user_id,
            transaction_table.c.description.like(f"%Source ID: {source_id}%"),
        )
    )

    values = {
        "amount": parse_budget_amount(project.budget),
        "description": description[:1000],
        "transaction_date": date.today(),
        "kind": "expense",
        "user_id": user_id,
        "category_id": category_id,
    }

    if existing_transaction_id is None:
        return int(connection.execute(transaction_table.insert().values(**values)).inserted_primary_key[0])

    connection.execute(
        transaction_table.update().where(transaction_table.c.id == existing_transaction_id).values(**values)
    )
    return int(existing_transaction_id)


def ensure_transaction_tag(connection: Connection, transaction_id: int, tag_id: int, project: ProjectItem) -> None:
    link_id = connection.scalar(
        select(transaction_tag_link_table.c.transaction_id).where(
            transaction_tag_link_table.c.transaction_id == transaction_id,
            transaction_tag_link_table.c.tag_id == tag_id,
        )
    )
    if link_id is not None:
        return

    note = f"{project.title[:120]} | {project.project_url}"
    connection.execute(
        transaction_tag_link_table.insert().values(
            transaction_id=transaction_id,
            tag_id=tag_id,
            importance=5,
            note=note[:255],
        )
    )


def build_source_id(project: ProjectItem, parsed_by: str) -> str:
    return f"lr2:{parsed_by}:{project.project_url}"


def build_transaction_description(project: ProjectItem, parsed_by: str, source_id: str) -> str:
    parts = [
        "LR2 parser source: freelance project card",
        f"Source ID: {source_id}",
        f"Parser: {parsed_by}",
        f"Source page: {project.source_url}",
        f"Project URL: {project.project_url}",
    ]
    if project.budget:
        parts.append(f"Budget: {project.budget}")
    if project.meta:
        parts.append(f"Meta: {project.meta}")
    if project.description:
        parts.extend(["", "Parsed description:", project.description])
    return "\n".join(parts)


def chunk_urls(urls: list[str], chunk_count: int) -> list[list[str]]:
    if chunk_count < 1:
        raise ValueError("chunk_count must be positive")
    if not urls:
        return []

    actual_chunks = min(chunk_count, len(urls))
    chunks = [[] for _ in range(actual_chunks)]
    for index, url in enumerate(urls):
        chunks[index % actual_chunks].append(url)
    return chunks


def print_parse_result(result: ParseResult) -> None:
    if result.status == "ok":
        print(
            f"[{result.parsed_by}] OK {result.url} -> extracted={result.extracted_count}, saved_tasks={result.saved_count}",
            flush=True,
        )
    else:
        print(f"[{result.parsed_by}] ERROR {result.url} -> {result.error}", flush=True)


def print_benchmark_table(results: list[dict[str, object]]) -> None:
    print("| Approach | URLs | Saved tasks | Errors | Time, seconds |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for row in results:
        print(
            "| {method} | {urls} | {saved} | {errors} | {elapsed:.6f} |".format(
                method=row["method"],
                urls=row["urls"],
                saved=row["saved"],
                errors=row["errors"],
                elapsed=row["elapsed_seconds"],
            )
        )


def write_task2_results(results: Iterable[dict[str, object]], output_dir: Path = RESULTS_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = list(results)

    markdown_lines = [
        "# Task 2 Benchmark Results",
        "",
        "| Approach | URLs | Saved tasks | Errors | Time, seconds |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        markdown_lines.append(
            "| {method} | {urls} | {saved} | {errors} | {elapsed:.6f} |".format(
                method=row["method"],
                urls=row["urls"],
                saved=row["saved"],
                errors=row["errors"],
                elapsed=row["elapsed_seconds"],
            )
        )

    (output_dir / "task2_benchmark.md").write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    (output_dir / "task2_benchmark.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def summarize_results(method: str, started_at: float, elapsed_seconds: float, results: list[ParseResult]) -> dict[str, object]:
    return {
        "method": method,
        "started_at": started_at,
        "urls": len(results),
        "saved": sum(result.saved_count for result in results),
        "extracted": sum(result.extracted_count for result in results),
        "ok": sum(1 for result in results if result.status == "ok"),
        "errors": sum(1 for result in results if result.status != "ok"),
        "elapsed_seconds": elapsed_seconds,
        "items": [asdict(result) for result in results],
    }
