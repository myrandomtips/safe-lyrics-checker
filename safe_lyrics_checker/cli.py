"""Command line interface for safe_lyrics_checker."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .quote_safety import check_quote_safety
from .rights_engine import RightsStatus, check_lyrics_rights


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="safe-lyrics-checker",
        description=(
            "Metadata-only lyric rights checker with optional quote safety heuristics."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    rights_parser = subparsers.add_parser(
        "rights-check",
        help="Primary metadata-only copyright safety check.",
    )
    rights_parser.add_argument("--jurisdiction", choices=["US", "UK", "AU"], required=True)
    rights_parser.add_argument("--publication-year", type=int)
    rights_parser.add_argument("--lyricist-death-year", type=int)
    rights_parser.add_argument(
        "--renewal-status",
        choices=["unknown", "renewed", "not_renewed"],
        default="unknown",
    )

    quote_parser = subparsers.add_parser(
        "quote-check",
        help="Secondary quote-size and exact-match heuristics.",
    )
    quote_parser.add_argument(
        "excerpt",
        nargs="?",
        default=None,
        help="Lyric excerpt text. If omitted, --file is required.",
    )
    quote_parser.add_argument("--file", type=Path, help="Read excerpt text from a file.")
    quote_parser.add_argument(
        "--known-lyrics-file",
        type=Path,
        help="Optional file with one known lyric segment per line.",
    )
    quote_parser.add_argument("--max-words", type=int, default=90)
    quote_parser.add_argument("--max-lines", type=int, default=4)

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


def _run_rights_check(args: argparse.Namespace) -> int:
    result = check_lyrics_rights(
        jurisdiction=args.jurisdiction,
        publication_year=args.publication_year,
        lyricist_death_year=args.lyricist_death_year,
        renewal_status=args.renewal_status,
    )
    print(result.status.value)
    print(result.explanation)

    if result.status is RightsStatus.SAFE:
        return 0
    if result.status is RightsStatus.NOT_SAFE:
        return 1
    return 2


def _run_quote_check(args: argparse.Namespace) -> int:
    excerpt = _resolve_excerpt(args)
    known_lyrics = _load_lines(args.known_lyrics_file)
    result = check_quote_safety(
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "rights-check":
        return _run_rights_check(args)
    if args.command == "quote-check":
        return _run_quote_check(args)

    raise SystemExit("Unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
