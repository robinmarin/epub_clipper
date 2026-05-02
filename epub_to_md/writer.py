"""File writing and template rendering for EPUB to markdown conversion."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from epub_to_md.parser import BookMetadata, MarkdownChapter


def write_chapters(
    book: BookMetadata,
    chapters: list[MarkdownChapter],
    output_dir: str = "./output",
    overwrite: bool = False,
) -> tuple[str, str]:
    """Write chapters to markdown files.

    Args:
        book: Book metadata.
        chapters: List of markdown chapters.
        output_dir: Output directory path.
        overwrite: Whether to overwrite existing files.

    Returns:
        Tuple of (chapters_dir, index_path).

    Raises:
        FileExistsError: If output directory exists and overwrite is False.
    """
    output_path = Path(output_dir)

    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"Output directory exists: {output_dir}. Use --overwrite to replace."
        )

    output_path.mkdir(parents=True, exist_ok=True)

    for chapter in chapters:
        chapter_path = output_path / chapter.filename
        full_content = render_chapter(
            chapter=chapter,
            book_title=book.title,
            book_author=book.author,
            total_chapters=len(chapters),
        )
        chapter_path.write_text(full_content, encoding="utf-8")

    index_path = output_path / "_index.md"
    index_content = _render_index(book, chapters)
    index_path.write_text(index_content, encoding="utf-8")

    return str(output_path), str(index_path)


def _render_index(book: BookMetadata, chapters: list[MarkdownChapter]) -> str:
    """Render the index markdown file."""
    total_chapters = len(chapters)
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        "---",
        f'book: "{_escape_yaml(book.title)}"',
        f'author: "{_escape_yaml(book.author or "Unknown")}"',
        f'converted: "{today}"',
        f"total_chapters: {total_chapters}",
        "---",
        "",
        f"# {book.title}",
        "",
        "## 📝 Agent Notes",
        "<!-- High-level notes about the whole book -->",
        "",
        "## Chapters",
        "| # | Title | Slug | Key Topics |",
        "|---|-------|------|------------|",
    ]

    for chapter in chapters:
        topics = _extract_topics(chapter.content)
        lines.append(
            f"| {chapter.number} | {chapter.title} | {chapter.slug} | {topics} |"
        )

    lines.append("")
    lines.append("## Full Table of Contents")
    lines.append(_render_toc(chapters))

    return "\n".join(lines)


def _render_toc(chapters: list[MarkdownChapter]) -> str:
    """Render table of contents from chapters."""
    lines = []
    for chapter in chapters:
        indent = "  "
        lines.append(f"{indent}- [{chapter.title}]({chapter.filename})")
    return "\n".join(lines)


def _extract_topics(content: str, max_topics: int = 3) -> str:
    """Extract key topics from chapter content for the index."""
    h2_headings = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## ") and not line.startswith("### "):
            topic = line[3:].strip().lstrip("0123456789. ")
            if topic and len(topic) < 40:
                h2_headings.append(topic)

    topics = h2_headings[:max_topics]
    if not topics:
        return "..."
    return "; ".join(topics)


def _escape_yaml(text: str) -> str:
    """Escape special characters for YAML strings."""
    if not text:
        return ""
    text = text.replace('"', '\\"')
    return text


def render_chapter(
    chapter: MarkdownChapter,
    book_title: str,
    book_author: Optional[str],
    total_chapters: int,
) -> str:
    """Render a single chapter markdown file with full template.

    Args:
        chapter: The markdown chapter.
        book_title: Title of the book.
        book_author: Author of the book.
        total_chapters: Total number of chapters.

    Returns:
        Rendered markdown content.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        "---",
        f'title: "{_escape_yaml(chapter.title)}"',
        f"chapter: {chapter.number}",
        f'slug: {chapter.slug}',
        f'book: "{_escape_yaml(book_title)}"',
        f'author: "{_escape_yaml(book_author or "Unknown")}"',
        f"total_chapters: {total_chapters}",
        "---",
        "",
        f"# {chapter.title}",
        "",
        "## 📝 Agent Notes",
        f"<!-- Agent writes here. Format: YYYY-MM-DD: note text -->",
        "",
        "## ❓ Open Questions",
        "<!-- Unresolved questions about this chapter go here -->",
        "",
        "## 🔗 Cross-References",
        "<!-- Links to other chapters that relate to this one -->",
        "",
        "---",
        "",
        "## Original Text",
        "",
    ]

    content_lines = chapter.content.split("\n")
    for line in content_lines:
        lines.append(line)

    return "\n".join(lines)


def get_output_dir(base_dir: str, book_slug: str) -> Path:
    """Get or create output directory for a specific book.

    Args:
        base_dir: Base output directory.
        book_slug: Slugified book title.

    Returns:
        Path to the output directory.
    """
    output_path = Path(base_dir) / book_slug
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path