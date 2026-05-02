# epub-to-md

Convert EPUB files to per-chapter markdown — designed for LLM knowledge bases.

## Features

- **Per-chapter output** with YAML frontmatter (`title`, `chapter`, `slug`, `book`, `author`, `total_chapters`)
- **Agent-ready templates** with sections for notes, open questions, and cross-references
- **Clean chapter detection** via EPUB spine, TOC (NCX/NAV), and heading analysis
- **HTML → Markdown** conversion: headings, bold/italic, lists, tables, blockquotes, code blocks
- **Both library and CLI**: import `convert_epub()` or run from terminal
- **Error resilient**: skips malformed sections, warns on empty chapters

## Quick Start

### CLI

```bash
pip install -e .
epub-to-md ./mybook.epub
epub-to-md ./mybook.epub --output ./chapters --overwrite
```

### Library

```python
from epub_to_md import convert_epub

result = convert_epub("mybook.epub", output_dir="./output")
print(f"Converted {len(result.chapters)} chapters")
for ch in result.chapters:
    print(f"  {ch.filename} ({ch.word_count} words)")
```

## Output Structure

```
output/
├── _index.md                    ← Book metadata, chapter table, TOC
├── chapter_01_introduction.md
├── chapter_02_momentum.md
└── ...
```

### Chapter Format

```markdown
---
title: "Chapter 1: Introduction"
chapter: 1
slug: introduction
book: "Factor Investing"
author: "John Smith"
total_chapters: 12
---

# Chapter 1: Introduction

## 📝 Agent Notes
<!-- YYYY-MM-DD: note text -->

## ❓ Open Questions
<!-- Unresolved questions -->

## 🔗 Cross-References
<!-- Links to related chapters -->

---

## Original Text

### 1.1 Getting Started
[content...]
```

## API

### `convert_epub(epub_path, output_dir, overwrite) → ConversionResult`

| Parameter    | Type    | Default   | Description                     |
|--------------|---------|-----------|---------------------------------|
| `epub_path`  | `str`   | required  | Path to input EPUB file         |
| `output_dir` | `str`   | `"./output"` | Output directory             |
| `overwrite`  | `bool`  | `False`   | Replace existing output         |

### Returns: `ConversionResult`

```python
@dataclass
class ConversionResult:
    book_title: str
    author: Optional[str]
    chapters: list[ChapterInfo]
    output_dir: str
    index_path: str

@dataclass
class ChapterInfo:
    number: int
    title: str
    slug: str
    filename: str
    word_count: int
```

## File Structure

```
epub_to_md/
├── __init__.py       ← Public API: convert_epub, ConversionResult, ChapterInfo
├── parser.py         ← EPUB parsing, spine/TOC-based chapter detection
├── converter.py      ← HTML → markdown with table/code/blockquote support
├── writer.py         ← File I/O with YAML frontmatter templates
├── cli.py            ← CLI entry point
└── README.md

tests/
├── test_parser.py
├── test_converter.py
├── test_writer.py
├── test_cli.py
└── test_init.py
```

## Installation

```bash
pip install -r requirements.txt
```

Or for development:

```bash
pip install -e ".[dev]"
pytest tests/
```

## Dependencies

- `ebooklib` — EPUB parsing
- `beautifulsoup4` — HTML parsing
- `markdownify` — HTML → markdown
- `lxml` — XML/HTML processing
- `python-slugify` — Slug generation

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing EPUB file | `FileNotFoundError` with path |
| Output exists | `FileExistsError` (use `--overwrite`) |
| Malformed EPUB | Warning + skip bad sections |
| Empty chapter | Warning + skip (no empty files) |