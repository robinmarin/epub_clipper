"""Tests for epub_to_md.parser module."""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from epub_to_md.parser import (
    BookMetadata,
    RawChapter,
    MarkdownChapter,
    parse_epub,
    _extract_metadata,
    _extract_chapters,
    _is_nav_or_cover,
    _extract_title_from_soup,
    _extract_chapter_number,
    convert_chapters_to_markdown,
)


class TestBookMetadata:
    def test_creation(self):
        meta = BookMetadata(title="Test Book", author="John Doe")
        assert meta.title == "Test Book"
        assert meta.author == "John Doe"

    def test_defaults(self):
        meta = BookMetadata(title="Test Book")
        assert meta.author is None


class TestRawChapter:
    def test_creation(self):
        chapter = RawChapter(
            number=1,
            title="Introduction",
            content="<p>Test content</p>",
            spine_index=0,
        )
        assert chapter.number == 1
        assert chapter.title == "Introduction"


class TestMarkdownChapter:
    def test_creation(self):
        chapter = MarkdownChapter(
            number=1,
            title="Introduction",
            slug="introduction",
            filename="chapter_01_introduction.md",
            content="# Introduction\n\nTest",
            word_count=5,
        )
        assert chapter.slug == "introduction"
        assert chapter.word_count == 5


class TestExtractChapterNumber:
    def test_chapter_prefix(self):
        num = _extract_chapter_number("Chapter 3: Testing", 0)
        assert num == 3

    def test_number_only(self):
        num = _extract_chapter_number("3. Testing", 0)
        assert num == 3

    def test_chinese_chapter(self):
        num = _extract_chapter_number("第3章测试", 0)
        assert num == 3

    def test_no_number(self):
        num = _extract_chapter_number("Introduction", 5)
        assert num == 6

    def test_roman_not_matched(self):
        num = _extract_chapter_number("Chapter III", 0)
        assert num == 1


class TestIsNavOrCover:
    def test_nav_element(self):
        html = '<nav epub:type="toc"><ol><li>Chapter 1</li></ol></nav>'
        assert _is_nav_or_cover(html) is True

    def test_cover_class(self):
        html = '<body class="cover"><h1>Cover</h1></body>'
        assert _is_nav_or_cover(html) is True

    def test_regular_content(self):
        html = '<body><h1>Chapter 1</h1><p>Content here</p></body>'
        assert _is_nav_or_cover(html) is False


class TestConvertChaptersToMarkdown:
    def test_converts_raw_chapters(self):
        raw = RawChapter(
            number=1,
            title="Introduction",
            content="<h1>Introduction</h1><p>Hello world</p>",
            spine_index=0,
        )
        result = convert_chapters_to_markdown([raw])
        assert len(result) == 1
        assert isinstance(result[0], MarkdownChapter)

    def test_filename_generation(self):
        raw = RawChapter(
            number=1,
            title="Getting Started",
            content="<h1>Getting Started</h1>",
            spine_index=0,
        )
        result = convert_chapters_to_markdown([raw])
        assert "getting-started.md" in result[0].filename

    def test_word_count(self):
        raw = RawChapter(
            number=1,
            title="Test",
            content="<p>One two three four five</p>",
            spine_index=0,
        )
        result = convert_chapters_to_markdown([raw])
        assert result[0].word_count == 5

    def test_slug_generation(self):
        raw = RawChapter(
            number=2,
            title="Chapter 2: What's New?",
            content="<h1>Chapter 2: What's New?</h1>",
            spine_index=0,
        )
        result = convert_chapters_to_markdown([raw])
        assert "what" in result[0].slug and "new" in result[0].slug