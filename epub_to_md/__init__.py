"""EPUB to Markdown converter - A reusable module for converting EPUB files to per-chapter markdown."""

from dataclasses import dataclass
from typing import Optional

from epub_to_md.parser import parse_epub, convert_chapters_to_markdown
from epub_to_md.writer import write_chapters

__version__ = "1.0.0"

ConversionResult = None
ChapterInfo = None


def convert_epub(
    epub_path: str,
    output_dir: str = "./output",
    overwrite: bool = False,
) -> "ConversionResult":
    """Convert an EPUB file to a set of per-chapter markdown files.

    Args:
        epub_path: Path to the input EPUB file.
        output_dir: Directory to write output files. Defaults to "./output".
        overwrite: If True, overwrite existing output directory. Defaults to False.

    Returns:
        ConversionResult with book metadata and chapter information.

    Raises:
        FileNotFoundError: If the EPUB file does not exist.
        ValueError: If output directory exists and overwrite is False.
    """
    book, chapters = parse_epub(epub_path)

    markdown_chapters = convert_chapters_to_markdown(chapters)

    output_path, index_path = write_chapters(
        book=book,
        chapters=markdown_chapters,
        output_dir=output_dir,
        overwrite=overwrite,
    )

    return ConversionResult(
        book_title=book.title,
        author=book.author,
        chapters=[
            ChapterInfo(
                number=ch.number,
                title=ch.title,
                slug=ch.slug,
                filename=ch.filename,
                word_count=ch.word_count,
            )
            for ch in markdown_chapters
        ],
        output_dir=output_dir,
        index_path=index_path,
    )


@dataclass
class ChapterInfo:
    """Information about a converted chapter."""

    number: int
    title: str
    slug: str
    filename: str
    word_count: int


@dataclass
class ConversionResult:
    """Result of an EPUB to markdown conversion."""

    book_title: str
    author: Optional[str]
    chapters: list[ChapterInfo]
    output_dir: str
    index_path: str

    def __repr__(self) -> str:
        return (
            f"ConversionResult(book_title={self.book_title!r}, "
            f"chapters={len(self.chapters)}, output_dir={self.output_dir!r})"
        )