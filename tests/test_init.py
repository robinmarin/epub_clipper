"""Tests for epub_to_md package and convert_epub function."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from epub_to_md import convert_epub, ConversionResult, ChapterInfo


class TestConvertEpub:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            convert_epub("nonexistent.epub")


class TestConversionResult:
    def test_repr(self):
        result = ConversionResult(
            book_title="Test Book",
            author="Author",
            chapters=[],
            output_dir="./output",
            index_path="./output/_index.md",
        )
        assert "Test Book" in repr(result)
        assert "0" in repr(result) or "chapters=" in repr(result)


class TestChapterInfo:
    def test_creation(self):
        info = ChapterInfo(
            number=1,
            title="Test",
            slug="test",
            filename="test.md",
            word_count=100,
        )
        assert info.number == 1
        assert info.word_count == 100