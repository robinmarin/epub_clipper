"""Tests for epub_to_md.writer module."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path

from epub_to_md.writer import (
    write_chapters,
    render_chapter,
    get_output_dir,
    _escape_yaml,
    _extract_topics,
    _render_toc,
)
from epub_to_md.parser import BookMetadata, MarkdownChapter


class TestWriteChapters:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_creates_output_directory(self):
        book = BookMetadata(title="Test Book", author="Author")
        chapters = []
        write_chapters(book, chapters, self.temp_dir, overwrite=True)
        assert Path(self.temp_dir).exists()

    def test_writes_index_file(self):
        book = BookMetadata(title="Test Book", author="Author")
        chapters = []
        write_chapters(book, chapters, self.temp_dir, overwrite=True)
        index_path = Path(self.temp_dir) / "_index.md"
        assert index_path.exists()

    def test_writes_chapter_files(self):
        book = BookMetadata(title="Test Book", author="Author")
        chapters = [
            MarkdownChapter(
                number=1,
                title="Chapter One",
                slug="chapter_one",
                filename="chapter_01_chapter_one.md",
                content="# Chapter One\n\nContent",
                word_count=5,
            )
        ]
        write_chapters(book, chapters, self.temp_dir, overwrite=True)
        chapter_path = Path(self.temp_dir) / "chapter_01_chapter_one.md"
        assert chapter_path.exists()

    def test_raises_if_exists_and_no_overwrite(self):
        book = BookMetadata(title="Test Book", author="Author")
        chapters = []
        os.makedirs(self.temp_dir, exist_ok=True)
        with pytest.raises(FileExistsError):
            write_chapters(book, chapters, self.temp_dir, overwrite=False)

    def test_overwrites_when_flag(self):
        book = BookMetadata(title="Test Book", author="Author")
        chapters = []
        os.makedirs(self.temp_dir, exist_ok=True)
        write_chapters(book, chapters, self.temp_dir, overwrite=True)
        assert Path(self.temp_dir).exists()


class TestRenderChapter:
    def test_includes_yaml_frontmatter(self):
        chapter = MarkdownChapter(
            number=1,
            title="Introduction",
            slug="introduction",
            filename="chapter_01_introduction.md",
            content="Test content",
            word_count=1,
        )
        result = render_chapter(chapter, "Test Book", "Author", 10)
        assert result.startswith("---")
        assert 'title: "Introduction"' in result
        assert "chapter: 1" in result

    def test_includes_agent_sections(self):
        chapter = MarkdownChapter(
            number=1,
            title="Test",
            slug="test",
            filename="test.md",
            content="Test",
            word_count=1,
        )
        result = render_chapter(chapter, "Book", "Author", 5)
        assert "## 📝 Agent Notes" in result
        assert "## ❓ Open Questions" in result
        assert "## 🔗 Cross-References" in result

    def test_includes_original_text_header(self):
        chapter = MarkdownChapter(
            number=1,
            title="Test",
            slug="test",
            filename="test.md",
            content="Some content",
            word_count=1,
        )
        result = render_chapter(chapter, "Book", "Author", 5)
        assert "## Original Text" in result

    def test_includes_chapter_content(self):
        chapter = MarkdownChapter(
            number=1,
            title="Test",
            slug="test",
            filename="test.md",
            content="# Main Title\n\nParagraph text",
            word_count=4,
        )
        result = render_chapter(chapter, "Book", "Author", 5)
        assert "Main Title" in result
        assert "Paragraph text" in result


class TestEscapeYaml:
    def test_escapes_quotes(self):
        result = _escape_yaml('Hello "World"')
        assert '\\"' in result

    def test_handles_empty_string(self):
        result = _escape_yaml("")
        assert result == ""

    def test_preserves_regular_text(self):
        result = _escape_yaml("Hello World")
        assert result == "Hello World"


class TestExtractTopics:
    def test_extracts_h2_headings(self):
        content = "# Chapter\n\n## First Topic\n\n## Second Topic\n\nSome text"
        result = _extract_topics(content)
        assert "First Topic" in result
        assert "Second Topic" in result

    def test_limits_topics(self):
        content = "\n".join([f"## Topic {i}" for i in range(10)])
        result = _extract_topics(content, max_topics=3)
        topics = result.split("; ")
        assert len(topics) == 3

    def test_handles_missing_headings(self):
        result = _extract_topics("No headings here")
        assert result == "..."


class TestRenderToc:
    def test_renders_toc_entries(self):
        chapters = [
            MarkdownChapter(
                number=1,
                title="Chapter One",
                slug="chapter_one",
                filename="chapter_01.md",
                content="",
                word_count=0,
            )
        ]
        result = _render_toc(chapters)
        assert "- [Chapter One]" in result
        assert "chapter_01.md" in result


class TestGetOutputDir:
    def test_creates_directory(self):
        base = tempfile.mkdtemp()
        result = get_output_dir(base, "test-book")
        assert result.exists()
        shutil.rmtree(base, ignore_errors=True)

    def test_returns_pathlib_path(self):
        base = tempfile.mkdtemp()
        result = get_output_dir(base, "test-book")
        assert isinstance(result, Path)
        shutil.rmtree(base, ignore_errors=True)