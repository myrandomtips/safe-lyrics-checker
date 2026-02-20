"""Rules engine for conservative lyric excerpt safety checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List
import re


WORD_RE = re.compile(r"\b\w+\b")


@dataclass(frozen=True)
class CheckResult:
    """Result of a lyric safety check."""

    is_safe: bool
    rule_hits: List[str]
    notes: List[str]


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _line_count(text: str) -> int:
    return len([line for line in text.splitlines() if line.strip()])


def _normalize(text: str) -> str:
    return " ".join(text.split()).strip().lower()


def check_lyrics_excerpt(
    excerpt: str,
    known_lyrics: Iterable[str] | None = None,
    *,
    max_words: int = 90,
    max_lines: int = 4,
) -> CheckResult:
    """Check whether a lyrics excerpt is likely safe to publish.

    The checker is intentionally conservative. It marks text unsafe if any rule
    is violated:
    1. More than ``max_words`` words.
    2. More than ``max_lines`` non-empty lines.
    3. Exact match against a known-lyrics corpus line/segment.
    """

    rule_hits: list[str] = []
    notes: list[str] = []

    words = _word_count(excerpt)
    lines = _line_count(excerpt)
    normalized = _normalize(excerpt)

    if words > max_words:
        rule_hits.append("max_words")
        notes.append(
            f"Excerpt has {words} words which exceeds the safety threshold of {max_words}."
        )

    if lines > max_lines:
        rule_hits.append("max_lines")
        notes.append(
            f"Excerpt has {lines} non-empty lines which exceeds the threshold of {max_lines}."
        )

    if normalized and known_lyrics:
        normalized_corpus = {_normalize(item) for item in known_lyrics if item.strip()}
        if normalized in normalized_corpus:
            rule_hits.append("known_lyric_match")
            notes.append(
                "Excerpt exactly matches an entry in the known-lyrics corpus."
            )

    if not rule_hits:
        notes.append("No rule violations were detected.")

    return CheckResult(is_safe=not rule_hits, rule_hits=rule_hits, notes=notes)
