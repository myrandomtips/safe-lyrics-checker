from __future__ import annotations

import html
import re
from typing import Optional

from .models import UrlMetadata

PUBLICATION_RE = re.compile(r"(?:published|publication|release date|copyright)\D{0,25}(1[5-9]\d{2}|20\d{2})", re.IGNORECASE)
DEATH_RE = re.compile(r"(?:died|death|d\.)\D{0,20}(1[5-9]\d{2}|20\d{2})", re.IGNORECASE)
RENEWAL_RE = re.compile(r"\b(not renewed|renewed)\b", re.IGNORECASE)
BY_RE = re.compile(r"\b(?:lyrics?\s+by|text\s+by|words\s+by|composer|by)\s+([A-Z][A-Za-z'\- ]{2,80}?)(?:[.,;]|\s{2,}|$)")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def html_to_text(raw_html: str) -> str:
    no_tags = re.sub(r"<[^>]+>", " ", raw_html)
    return html.unescape(re.sub(r"\s+", " ", no_tags)).strip()


def extract_title(raw_html: str) -> Optional[str]:
    match = TITLE_RE.search(raw_html)
    if not match:
        return None
    title = html.unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    return title or None


def extract_metadata_generic(raw_html: str) -> UrlMetadata:
    text = html_to_text(raw_html)
    publication = PUBLICATION_RE.search(text)

    death = DEATH_RE.search(text)
    renewal = RENEWAL_RE.search(text)
    lyricist = BY_RE.search(text)

    return UrlMetadata(
        title=extract_title(raw_html),
        lyricist_or_composer=lyricist.group(1).strip() if lyricist else None,
        publication_year=int(publication.group(1)) if publication else None,
        lyricist_death_year=int(death.group(1)) if death else None,
        renewal_status=("not_renewed" if renewal and renewal.group(1).lower() == "not renewed" else "renewed" if renewal else "unknown"),
    )


def has_sufficient_metadata(metadata: UrlMetadata) -> bool:
    return any(
        value is not None
        for value in [
            metadata.title,
            metadata.lyricist_or_composer,
            metadata.publication_year,
            metadata.lyricist_death_year,
        ]
    ) or metadata.renewal_status != "unknown"
