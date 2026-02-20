"""Command line interface for safe_lyrics_checker."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .rules_engine import check_lyrics_excerpt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="safe-lyrics-checker",
        description="Check a lyrics excerpt against conservative safety rules.",
    )
    parser.add_argument(
        "excerpt",
        nargs="?",
        default=None,
        help="Lyric excerpt text. If omitted, --file is required.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Read excerpt text from a file.",
    )
    parser.add_argument(
        "--known-lyrics-file",
        type=Path,
        help="Optional file with one known lyric segment per line.",
    )
    parser.add_argument("--max-words", type=int, default=90)
    parser.add_argument("--max-lines", type=int, default=4)
    return parser


def _load_lines(path: Path | None) -> list[str]:
    if path is None:
        return []
    return path.read_text(encoding="utf-8").splitlines()


def _resolve_excerpt(args: argparse.Namespace) -> str:
    if args.excerpt:
        return args.excerpt
    if args.file:
        return args.file.read_text(encoding="utf-8")
    raise SystemExit("You must provide either excerpt text or --file.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    excerpt = _resolve_excerpt(args)
    known_lyrics = _load_lines(args.known_lyrics_file)

    result = check_lyrics_excerpt(
        excerpt,
        known_lyrics=known_lyrics,
        max_words=args.max_words,
        max_lines=args.max_lines,
    )

    status = "SAFE" if result.is_safe else "UNSAFE"
    print(f"Result: {status}")
    for note in result.notes:
        print(f"- {note}")

    return 0 if result.is_safe else 1


if __name__ == "__main__":
    raise SystemExit(main())
