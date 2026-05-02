"""Tests for epub_to_md.cli module."""

import pytest
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

from epub_to_md.cli import main, _create_parser
from epub_to_md import ConversionResult, ChapterInfo


class TestCreateParser:
    def test_creates_parser(self):
        parser = _create_parser()
        assert parser is not None

    def test_default_output_dir(self):
        parser = _create_parser()
        args = parser.parse_args(["book.epub"])
        assert args.output is None

    def test_overwrite_flag(self):
        parser = _create_parser()
        args = parser.parse_args(["book.epub", "--overwrite"])
        assert args.overwrite is True

    def test_output_flag(self):
        parser = _create_parser()
        args = parser.parse_args(["book.epub", "--output", "./mydir"])
        assert args.output == "./mydir"


class TestMain:
    def setup_method(self):
        self.temp_file = None

    def test_missing_file(self):
        result = main(["nonexistent.epub"])
        assert result == 1

    def test_shows_help_without_args(self, capsys):
        with patch("sys.stdout"):
            result = main([])
        assert result == 1

    @patch("epub_to_md.cli.convert_epub")
    def test_successful_conversion(self, mock_convert):
        temp_epub = Path(tempfile.gettempdir()) / "test.epub"
        temp_epub.touch()

        mock_result = MagicMock(spec=ConversionResult)
        mock_result.chapters = [
            ChapterInfo(number=1, title="Test", slug="test", filename="test.md", word_count=100)
        ]
        mock_result.index_path = "./output/_index.md"
        mock_convert.return_value = mock_result

        with patch("epub_to_md.cli.Path.exists", return_value=True):
            result = main([str(temp_epub), "--output", "./output"])

        temp_epub.unlink(missing_ok=True)

    def test_file_not_found_error(self, capsys):
        result = main(["/nonexistent/path/book.epub"])
        assert result == 1


class TestCliOutput:
    @patch("epub_to_md.cli.convert_epub")
    def test_reports_chapter_count(self, mock_convert, capsys):
        temp_epub = Path(tempfile.gettempdir()) / "test.epub"
        temp_epub.touch()

        mock_result = MagicMock(spec=ConversionResult)
        mock_result.chapters = [
            ChapterInfo(number=i, title=f"Chapter {i}", slug=f"chapter_{i}", filename=f"chapter_{i:02d}.md", word_count=100)
            for i in range(1, 4)
        ]
        mock_result.index_path = "./output/_index.md"
        mock_convert.return_value = mock_result

        with patch("epub_to_md.cli.Path.exists", return_value=True):
            result = main([str(temp_epub)])

        output = capsys.readouterr().out
        assert "3 chapters" in output

        temp_epub.unlink(missing_ok=True)