from __future__ import annotations

import re

from ..http_cache import HttpCache
from .common import build_search_url, enrich_from_page, extract_title_candidates
from .models import Candidate

DOMAIN = "https://archive.org"


def search(query: str, cache: HttpCache | None = None) -> list[Candidate]:
    cache = cache or HttpCache()
    url = build_search_url(f"{DOMAIN}/search?query=", query)
    body = cache.get_text(url)
    links = re.findall(r"href=['\"](/details/[^'\"]+)['\"]", body)
    titles = extract_title_candidates(body)
    candidates: list[Candidate] = []
    for idx, link in enumerate(links[:5]):
        title = titles[idx] if idx < len(titles) else f"{query} ({idx + 1})"
        work_url = f"{DOMAIN}{link}"
        candidates.append(Candidate(title=title, source="archive", work_url=work_url, evidence_urls=[url, work_url]))
    return candidates


def enrich(candidate: Candidate, cache: HttpCache | None = None) -> Candidate:
    cache = cache or HttpCache()
    body = cache.get_text(candidate.work_url)
    return enrich_from_page(candidate, body, candidate.work_url)
