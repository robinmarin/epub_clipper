"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def sample_epub_path(temp_dir):
    """Provide a path for a sample EPUB file (does not create the file)."""
    return Path(temp_dir) / "sample.epub"


@pytest.fixture
def sample_html_content():
    """Provide sample HTML content for testing."""
    return """
    <html>
    <head><title>Test Chapter</title></head>
    <body>
        <h1>Chapter 1: Introduction</h1>
        <p>This is the first paragraph.</p>
        <h2>1.1 Getting Started</h2>
        <p>Another paragraph here.</p>
        <blockquote>Important quote</blockquote>
    </body>
    </html>
    """


@pytest.fixture
def sample_markdown_content():
    """Provide expected markdown output for sample content."""
    return "# Chapter 1: Introduction\n\nThis is the first paragraph.\n\n## 1.1 Getting Started\n\nAnother paragraph here.\n\n> Important quote"