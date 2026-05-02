# EPUB to Markdown Converter

A reusable Python module for converting EPUB files into a structured set of per-chapter markdown files, designed to serve as a living knowledge base for LLM agents.

## Features

- **Per-chapter markdown output** with YAML frontmatter
- **Clean chapter boundaries** detected from EPUB spine, headings, and TOC
- **Rich metadata** including title, author, chapter number, and slug
- **Agent-ready templates** with sections for notes, questions, and cross-references
- **Both library and CLI** - import and use in code, or run from command line
- **Error resilience** - skips malformed sections instead of crashing

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### CLI

```bash
python -m epub_to_md.cli ./mybook.epub
python -m epub_to_md.cli ./mybook.epub --output ./chapters
python -m epub_to_md.cli ./mybook.epub --overwrite
```

### Library

```python
from epub_to_md import convert_epub

result = convert_epub("mybook.epub", output_dir="./output")
print(f"Converted {len(result.chapters)} chapters")
for chapter in result.chapters:
    print(f"  - {chapter.title} ({chapter.word_count} words)")
```

## Output Structure

Given `Factor Investing.epub`, produces:

```
output/
├── _index.md                  ← Book-level index with TOC and metadata
├── chapter_01_introduction.md
├── chapter_02_momentum.md
├── chapter_03_value.md
└── ...
```

### Chapter File Format

```markdown
---
title: "Chapter 3: Value Factors"
chapter: 3
slug: value-factors
book: "Factor Investing: A Practitioner's Guide"
author: "John Smith"
total_chapters: 12
---

# Chapter 3: Value Factors

## 📝 Agent Notes
<!-- Agent writes here. Format: YYYY-MM-DD: note text -->

## ❓ Open Questions
<!-- Unresolved questions about this chapter go here -->

## 🔗 Cross-References
<!-- Links to other chapters that relate to this one -->

---

## Original Text

### 3.1 Defining Value
[original content...]

### 3.2 Construction Approaches
[original content...]
```

### Index File Format

```markdown
---
book: "Factor Investing: A Practitioner's Guide"
author: "John Smith"
converted: "2024-03-12"
total_chapters: 12
---

# Factor Investing: A Practitioner's Guide

## 📝 Agent Notes
<!-- High-level notes about the whole book -->

## Chapters
| # | Title | Slug | Key Topics |
|---|-------|------|------------|
| 1 | Introduction | introduction | ... |
...

## Full Table of Contents
[Nested TOC from EPUB]
```

## API Reference

### `convert_epub(epub_path, output_dir, overwrite)`

Convert an EPUB file to markdown chapters.

**Parameters:**
- `epub_path` (str): Path to the input EPUB file
- `output_dir` (str, optional): Output directory. Defaults to `"./output"`
- `overwrite` (bool, optional): Overwrite existing output. Defaults to `False`

**Returns:** `ConversionResult`

**Raises:**
- `FileNotFoundError`: If EPUB file doesn't exist
- `ValueError`: If output directory exists and `overwrite=False`

### `ConversionResult`

```python
@dataclass
class ConversionResult:
    book_title: str           # Title of the book
    author: Optional[str]     # Author name
    chapters: list[ChapterInfo]  # List of chapter info
    output_dir: str          # Output directory path
    index_path: str           # Path to _index.md
```

### `ChapterInfo`

```python
@dataclass
class ChapterInfo:
    number: int               # Chapter number
    title: str                # Chapter title
    slug: str                 # URL-safe slug
    filename: str             # Output filename
    word_count: int           # Word count of chapter
```

## CLI Options

```
usage: epub_to_md/cli.py [-h] [--output DIR] [--overwrite] [--version] [epub_path]

Convert an EPUB file to per-chapter markdown files.

positional arguments:
  epub_path              Path to the EPUB file to convert

optional arguments:
  -o, --output DIR       Output directory (default: ./output)
  --overwrite            Overwrite existing output directory
  --version              Show program version
```

## File Structure

```
epub_to_md/
├── __init__.py       ← Public API exports
├── parser.py         ← EPUB parsing and chapter detection
├── converter.py      ← HTML to markdown conversion
├── writer.py         ← File writing and template rendering
├── cli.py            ← CLI entry point
├── README.md         ← This file
└── requirements.txt  ← Dependencies
```

## Dependencies

- `ebooklib` - EPUB parsing
- `beautifulsoup4` - HTML parsing
- `markdownify` - HTML to markdown conversion
- `lxml` - XML/HTML processing
- `python-slugify` - Slug generation

## Error Handling

- **Missing file**: Clear error message with path
- **Malformed EPUB**: Warns and skips bad sections
- **Output exists**: Prompts or returns error (unless `--overwrite`)
- **Empty chapters**: Skips and warns, doesn't write empty files

## License

MIT