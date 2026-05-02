"""Tests for epub_to_md.converter module."""

import pytest
from bs4 import BeautifulSoup

from epub_to_md.converter import (
    html_to_markdown,
    count_words,
    extract_excerpt,
    _clean_soup,
    _post_process_markdown,
)


class TestHtmlToMarkdown:
    def test_converts_paragraphs(self):
        html = "<p>Hello world</p>"
        result = html_to_markdown(html)
        assert "Hello world" in result

    def test_converts_headings(self):
        html = "<h1>Title</h1><h2>Subtitle</h2>"
        result = html_to_markdown(html)
        assert "# Title" in result
        assert "## Subtitle" in result

    def test_converts_bold(self):
        html = "<p><strong>bold text</strong></p>"
        result = html_to_markdown(html)
        assert "**bold text**" in result

    def test_converts_italic(self):
        html = "<p><em>italic text</em></p>"
        result = html_to_markdown(html)
        assert "italic text" in result

    def test_converts_lists(self):
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = html_to_markdown(html)
        assert "Item 1" in result
        assert "Item 2" in result

    def test_converts_blockquote(self):
        html = "<blockquote><p>Quoted text</p></blockquote>"
        result = html_to_markdown(html)
        assert ">" in result

    def test_converts_code_block(self):
        html = "<pre><code>code here</code></pre>"
        result = html_to_markdown(html)
        assert "```" in result

    def test_removes_scripts(self):
        html = "<script>alert('bad')</script><p>Good content</p>"
        result = html_to_markdown(html)
        assert "alert" not in result
        assert "Good content" in result

    def test_removes_styles(self):
        html = "<style>.hidden{display:none}</style><p>Visible</p>"
        result = html_to_markdown(html)
        assert "display:none" not in result
        assert "Visible" in result


class TestCountWords:
    def test_counts_words(self):
        assert count_words("one two three") == 3

    def test_empty_string(self):
        assert count_words("") == 0

    def test_single_word(self):
        assert count_words("hello") == 1

    def test_with_punctuation(self):
        assert count_words("Hello, world!") == 2


class TestExtractExcerpt:
    def test_short_text(self):
        text = "Short text"
        result = extract_excerpt(text, max_length=50)
        assert result == "Short text"

    def test_truncates_long_text(self):
        text = " ".join(["word"] * 100)
        result = extract_excerpt(text, max_length=20)
        assert "..." in result
        assert len(result.split()) <= 21

    def test_preserves_intact_words(self):
        text = "one two three four five six seven eight nine ten"
        result = extract_excerpt(text, max_length=5)
        words = result.replace("...", "").split()
        assert len(words) <= 5


class TestPostProcessMarkdown:
    def test_removes_extra_blank_lines(self):
        md = "Paragraph 1\n\n\n\n\nParagraph 2"
        result = _post_process_markdown(md)
        assert "\n\n\n" not in result

    def test_preserves_code_blocks(self):
        md = "```\ncode\n```"
        result = _post_process_markdown(md)
        assert "```" in result