"""EPUB parsing and chapter detection."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from ebooklib import epub
from slugify import slugify

from epub_to_md.converter import html_to_markdown


@dataclass
class BookMetadata:
    """Metadata extracted from an EPUB."""

    title: str
    author: Optional[str] = None
    language: Optional[str] = None


@dataclass
class RawChapter:
    """Raw chapter data extracted from EPUB before markdown conversion."""

    number: int
    title: str
    content: str
    spine_index: int


@dataclass
class MarkdownChapter:
    """A chapter converted to markdown format."""

    number: int
    title: str
    slug: str
    filename: str
    content: str
    word_count: int


def parse_epub(epub_path: str) -> tuple[BookMetadata, list[RawChapter]]:
    """Parse an EPUB file and extract book metadata and chapter content.

    Args:
        epub_path: Path to the EPUB file.

    Returns:
        Tuple of (BookMetadata, list of RawChapter objects).

    Raises:
        FileNotFoundError: If the EPUB file does not exist.
    """
    path = Path(epub_path)
    if not path.exists():
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")

    book = epub.read_epub(str(path))

    metadata = _extract_metadata(book)

    chapters = _extract_chapters(book)

    return metadata, chapters


def _extract_metadata(book: epub.EpubBook) -> BookMetadata:
    """Extract metadata from an EPUB book."""
    title = "Unknown Title"
    if book.metadata and book.metadata.get("DC", {}):
        dc = book.metadata["DC"]
        if dc.get("title"):
            title = dc["title"][0][0]
        author = None
        if dc.get("creator"):
            author = dc["creator"][0][0]
    else:
        title = book.title if book.title else "Unknown Title"
        author = book.author if hasattr(book, "author") else None

    return BookMetadata(title=title, author=author)


def _extract_chapters(book: epub.EpubBook) -> list[RawChapter]:
    """Extract chapters from an EPUB using spine order and TOC."""
    chapters: list[RawChapter] = []

    items_by_id = {item.get_id(): item for item in book.get_items()}

    spine = book.spine
    toc = _get_toc(book)

    spine_items = []
    if hasattr(spine, "items"):
        spine_items = list(spine.items)
    elif hasattr(spine, "get_items"):
        spine_items = spine.get_items()

    processed_ids = set()

    for idx, spine_item in enumerate(spine_items):
        item_id = spine_item
        if hasattr(spine_item, "id"):
            item_id = spine_item.id
        elif hasattr(spine_item, "get_id"):
            item_id = spine_item.get_id()

        if item_id in processed_ids:
            continue

        item = items_by_id.get(item_id)
        if not item:
            continue

        if item.get_type() != 1:
            continue

        content = item.get_content()
        if not content:
            continue

        if _is_nav_or_cover(content):
            continue

        soup = BeautifulSoup(content, "lxml")

        chapter_title = _extract_title_from_soup(soup, item.href or "")
        chapter_number = _extract_chapter_number(chapter_title, idx)

        body = soup.find("body")
        if body:
            chapter_content = str(body)
        else:
            chapter_content = content

        if len(chapter_content.strip()) < 100:
            continue

        chapters.append(
            RawChapter(
                number=chapter_number,
                title=chapter_title,
                content=chapter_content,
                spine_index=idx,
            )
        )

        processed_ids.add(item_id)

    if not chapters and toc:
        for toc_item in toc:
            item = _find_item_by_href(book, toc_item.href)
            if item and item.get_content():
                content = item.get_content()
                soup = BeautifulSoup(content, "lxml")
                chapter_title = toc_item.title
                chapters.append(
                    RawChapter(
                        number=len(chapters) + 1,
                        title=chapter_title,
                        content=str(soup.find("body") or soup),
                        spine_index=0,
                    )
                )

    for i, chapter in enumerate(chapters):
        chapter.number = i + 1

    return chapters


def _get_toc(book: epub.EpubBook) -> list:
    """Get table of contents from EPUB."""
    toc = []
    try:
        if hasattr(book, "toc") and book.toc:
            toc = _flatten_toc(book.toc)
    except Exception:
        pass
    return toc


def _flatten_toc(toc_items) -> list:
    """Flatten nested TOC structure."""
    result = []
    for item in toc_items:
        if hasattr(item, "href"):
            result.append(item)
        if hasattr(item, "toc"):
            result.extend(_flatten_toc(item.toc))
        if hasattr(item, "items"):
            result.extend(_flatten_toc(item.items))
    return result


def _find_item_by_href(book: epub.EpubBook, href: str) -> Optional:
    """Find an item in the EPUB by its href."""
    for item in book.get_items():
        if hasattr(item, "href") and item.href == href:
            return item
    return None


def _is_nav_or_cover(content: str) -> bool:
    """Check if content is navigation or cover page."""
    soup = BeautifulSoup(content, "lxml")

    if soup.find("nav", {"epub:type": ["nav", "toc"]}):
        return True

    if soup.find("nav"):
        nav = soup.find("nav")
        if nav.get("role") == "doc-toc" or "toc" in (nav.get("class") or []):
            return True

    body = soup.find("body")
    if body:
        classes = body.get("class") or []
        if any(c in classes for c in ["cover", "nav", "titlepage"]):
            return True

    return False


def _extract_title_from_soup(soup: BeautifulSoup, fallback: str = "") -> str:
    """Extract chapter title from BeautifulSoup object."""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        return title_tag.string.strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text().strip()

    h2 = soup.find("h2")
    if h2:
        return h2.get_text().strip()

    if fallback:
        fallback_name = Path(fallback).stem
        fallback_name = fallback_name.replace("_", " ").replace("-", " ")
        if fallback_name.lower() not in ["index", "toc", "nav", "cover"]:
            return fallback_name

    return f"Chapter {fallback}"


def _extract_chapter_number(title: str, fallback_idx: int) -> int:
    """Extract chapter number from title or use fallback."""
    import re

    patterns = [
        r"chapter\s+(\d+)",
        r"^\s*(\d+)\s*[-.:]",
        r"第\s*(\d+)\s*章",
        r"(\d+)\.",
    ]

    title_lower = title.lower()
    for pattern in patterns:
        match = re.search(pattern, title_lower)
        if match:
            return int(match.group(1))

    return fallback_idx + 1


def convert_chapters_to_markdown(chapters: list[RawChapter]) -> list[MarkdownChapter]:
    """Convert raw chapters to markdown format.

    Args:
        chapters: List of RawChapter objects.

    Returns:
        List of MarkdownChapter objects with converted content.
    """
    result = []
    total = len(chapters)

    for raw in chapters:
        slug = slugify(
            raw.title,
            lowercase=True,
            max_length=50,
            word_boundary=True,
            save_text=True,
        )

        filename = f"chapter_{raw.number:02d}_{slug}.md"

        content = html_to_markdown(raw.content)

        word_count = len(content.split())

        result.append(
            MarkdownChapter(
                number=raw.number,
                title=raw.title,
                slug=slug,
                filename=filename,
                content=content,
                word_count=word_count,
            )
        )

    return result