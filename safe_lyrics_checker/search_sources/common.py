from __future__ import annotations

import html
import re
from urllib.parse import quote_plus

from .models import Candidate


YEAR_RE = re.compile(r"\b(1[5-9]\d{2}|20\d{2})\b")
DEATH_RE = re.compile(r"(?:died|death)\D{0,20}(1[5-9]\d{2}|20\d{2})", re.IGNORECASE)
RENEWAL_RE = re.compile(r"\b(not renewed|renewed)\b", re.IGNORECASE)


def build_search_url(base: str, query: str) -> str:
    return f"{base}{quote_plus(query)}"


def text_from_html(raw: str) -> str:
    no_tags = re.sub(r"<[^>]+>", " ", raw)
    return html.unescape(re.sub(r"\s+", " ", no_tags)).strip()


def extract_title_candidates(raw_html: str) -> list[str]:
    anchors = re.findall(r">([^<]{4,140})<", raw_html)
    clean = [re.sub(r"\s+", " ", html.unescape(a)).strip() for a in anchors]
    return [c for c in clean if len(c.split()) >= 2][:10]


def enrich_from_page(candidate: Candidate, page_text: str, page_url: str) -> Candidate:
    if page_url not in candidate.evidence_urls:
        candidate.evidence_urls.append(page_url)

    if candidate.publication_year is None:
        years = [int(y) for y in YEAR_RE.findall(page_text)]
        if years:
            candidate.publication_year = min(years)

    if candidate.lyricist_death_year is None:
        death = DEATH_RE.search(page_text)
        if death:
            candidate.lyricist_death_year = int(death.group(1))

    if candidate.renewal_status == "unknown":
        renewal = RENEWAL_RE.search(page_text)
        if renewal:
            candidate.renewal_status = (
                "not_renewed" if renewal.group(1).lower() == "not renewed" else "renewed"
            )

    return candidate
