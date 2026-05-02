"""Command-line interface for EPUB to Markdown conversion."""

import argparse
import sys
from pathlib import Path

from epub_to_md import convert_epub, ConversionResult


def main(argv: list[str] | None = None) -> int:
    """Main entry point for CLI.

    Args:
        argv: Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = _create_parser()
    args = parser.parse_args(argv)

    if not args.epub_path:
        parser.print_help()
        return 1

    epub_path = Path(args.epub_path)
    if not epub_path.exists():
        print(f"❌ Error: EPUB file not found: {epub_path}")
        return 1

    output_dir = args.output or "./output"
    overwrite = args.overwrite or False

    print(f"📖 Parsing: {epub_path.name}")

    try:
        result = convert_epub(
            epub_path=str(epub_path),
            output_dir=output_dir,
            overwrite=overwrite,
        )
    except FileExistsError as e:
        print(f"❌ Error: {e}")
        print("   Use --overwrite to replace existing output.")
        return 1
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return 1

    print(f"📑 Found {len(result.chapters)} chapters")

    for chapter in result.chapters:
        print(f"✅ {chapter.filename} ({chapter.word_count:,} words)")

    print(f"📁 Done. {len(result.chapters)} files written to {output_dir}/")
    print(f"📋 Index written to {result.index_path}")

    return 0


def _create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="epub_to_md",
        description="Convert an EPUB file to per-chapter markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python epub_to_md/cli.py ./mybook.epub
  python epub_to_md/cli.py ./mybook.epub --output ./chapters
  python epub_to_md/cli.py ./mybook.epub --overwrite
        """,
    )

    parser.add_argument(
        "epub_path",
        nargs="?",
        help="Path to the EPUB file to convert",
    )

    parser.add_argument(
        "-o", "--output",
        metavar="DIR",
        help="Output directory (default: ./output)",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output directory",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    return parser


if __name__ == "__main__":
    sys.exit(main())