"""HTML to Markdown conversion utilities."""

import re
from typing import Optional

from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import MarkdownConverter


class CustomMarkdownConverter(MarkdownConverter):
    """Custom markdown converter with support for tables, blockquotes, and code blocks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def convert_table(self, el: Tag, text: str, **kwargs) -> str:
        """Convert HTML table to markdown table."""
        rows = []
        headers = []
        header_row = el.find("thead")
        if header_row:
            header_cells = header_row.find_all(["th", "td"])
            headers = [cell.get_text().strip() for cell in header_cells]
            if headers:
                rows.append("| " + " | ".join(headers) + " |")
                rows.append("|" + "|".join([" --- " for _ in headers]) + "|")

        tbody = el.find("tbody")
        if tbody:
            table_rows = tbody.find_all("tr")
        else:
            table_rows = el.find_all("tr")

        for row in table_rows:
            cells = row.find_all(["td", "th"])
            if cells:
                row_text = "| " + " | ".join(cell.get_text().strip() for cell in cells) + " |"
                rows.append(row_text)

        if rows:
            return "\n".join(rows) + "\n"
        return text

    def convert_pre(self, el: Tag, text: str, **kwargs) -> str:
        """Convert pre/code blocks to markdown code blocks."""
        code = el.find("code")
        if code:
            lang = code.get("class", [])
            if lang:
                for cls in lang:
                    if cls.startswith("language-"):
                        lang = cls.split("-", 1)[1]
                        break
                else:
                    lang = ""
            else:
                lang = ""
            return f"\n```{lang}\n{code.get_text()}\n```\n"
        return f"\n```\n{text}\n```\n"

    def convert_blockquote(self, el: Tag, text: str, **kwargs) -> str:
        """Convert blockquotes to markdown format."""
        lines = text.strip().split("\n")
        return "\n".join(f"> {line}" for line in lines) + "\n"


def html_to_markdown(html: str) -> str:
    """Convert HTML content to markdown format.

    Args:
        html: HTML string content.

    Returns:
        Markdown formatted string.
    """
    soup = BeautifulSoup(html, "lxml")

    _clean_soup(soup)

    _process_headings(soup)

    _process_lists(soup)

    _unwrap_elements(soup, ["span", "div", "section", "article", "main"])
    _unwrap_navigation(soup)

    content = soup.find("body")
    if content is None:
        content = soup

    converter = CustomMarkdownConverter(
        bold="**",
        italic="_",
        code="`",
        heading_style="ATX",
    )

    markdown = converter.convert(str(soup))

    markdown = _post_process_markdown(markdown)

    return markdown.strip()


def _clean_soup(soup: BeautifulSoup) -> None:
    """Remove unwanted elements from soup."""
    elements_to_remove = [
        "script",
        "style",
        "meta",
        "link",
        "head",
    ]

    for tag in elements_to_remove:
        for element in soup.find_all(tag):
            element.decompose()

    for element in soup.find_all(
        "div", {"class": lambda x: x and any(c in str(x) for c in ["footer", "header", "nav", "sidebar", "margin"])}
    ):
        element.decompose()

    for element in soup.find_all(
        "span", {"class": lambda x: x and any(c in str(x) for c in ["page-number", "pagebreak", "pb"])}
    ):
        element.decompose()

    for element in soup.find_all("br"):
        if element.find_next_sibling():
            pass
        else:
            element.decompose()


def _process_headings(soup: BeautifulSoup) -> None:
    """Ensure headings have proper hierarchy."""
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

    for heading in headings:
        text = heading.get_text().strip()
        if text:
            heading.string = text


def _process_lists(soup: BeautifulSoup) -> None:
    """Clean up list formatting."""
    for ul in soup.find_all("ul"):
        for li in ul.find_all("li", recursive=False):
            li["class"] = "list-item"

    for ol in soup.find_all("ol"):
        for li in ol.find_all("li", recursive=False):
            li["class"] = "list-item"


def _unwrap_elements(soup: BeautifulSoup, tags: list[str]) -> None:
    """Unwrap specific elements, preserving their children."""
    for tag in tags:
        for element in soup.find_all(tag):
            element.unwrap()


def _unwrap_navigation(soup: BeautifulSoup) -> None:
    """Remove navigation elements."""
    for nav in soup.find_all("nav"):
        nav.decompose()

    for aside in soup.find_all("aside"):
        aside.decompose()


def _post_process_markdown(markdown: str) -> str:
    """Post-process markdown to fix common issues."""
    lines = markdown.split("\n")
    result = []

    prev_line = ""

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("#") and len(stripped) > 1:
            pass

        if stripped.startswith("```") and stripped.endswith("```") and len(stripped) > 6:
            result.append(line)
        elif stripped.startswith("|") or stripped.startswith("+---|"):
            result.append(line)
        else:
            if prev_line.strip().startswith("---") and line.strip() == "":
                continue

            result.append(line)

        prev_line = line

    markdown = "\n".join(result)

    markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    markdown = re.sub(r"\*\*(.+?)\*\*", r"**\1**", markdown)
    markdown = re.sub(r"__(.+?)__", r"**\1**", markdown)

    return markdown


def count_words(text: str) -> int:
    """Count words in text.

    Args:
        text: Input text.

    Returns:
        Number of words.
    """
    return len(text.split())


def extract_excerpt(text: str, max_length: int = 200) -> str:
    """Extract a short excerpt from text.

    Args:
        text: Input text.
        max_length: Maximum length of excerpt.

    Returns:
        Truncated excerpt with ellipsis.
    """
    words = text.split()
    if len(words) <= max_length:
        return text

    excerpt = " ".join(words[:max_length])
    return excerpt + "..."