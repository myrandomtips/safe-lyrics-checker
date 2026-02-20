from __future__ import annotations

from typing import Callable

from .http_cache import HttpCache
from .rights_engine import RightsResult, check_lyrics_rights
from .search_sources.models import Candidate
from .search_sources import archive, copyright_office, cpdl, gutenberg, imslp, loc, worldcat

SearchFn = Callable[[str, HttpCache | None], list[Candidate]]
EnrichFn = Callable[[Candidate, HttpCache | None], Candidate]


SOURCES: dict[str, tuple[SearchFn, EnrichFn]] = {
    "gutenberg": (gutenberg.search, gutenberg.enrich),
    "imslp": (imslp.search, imslp.enrich),
    "cpdl": (cpdl.search, cpdl.enrich),
    "loc": (loc.search, loc.enrich),
    "archive": (archive.search, archive.enrich),
    "worldcat": (worldcat.search, worldcat.enrich),
    "copyright": (copyright_office.search, copyright_office.enrich),
}


def search_candidates(
    query: str,
    *,
    sources: list[str],
    max_results: int,
    cache: HttpCache | None = None,
) -> list[Candidate]:
    cache = cache or HttpCache()
    results: list[Candidate] = []
    seen: set[tuple[str, str]] = set()

    for source in sources:
        search_fn, enrich_fn = SOURCES[source]
        for candidate in search_fn(query, cache):
            key = (candidate.source, candidate.work_url)
            if key in seen:
                continue
            seen.add(key)
            enriched = enrich_fn(candidate, cache)
            results.append(enriched)
            if len(results) >= max_results:
                return results

    return results


def evaluate_candidate(candidate: Candidate, jurisdiction: str) -> RightsResult:
    return check_lyrics_rights(
        jurisdiction=jurisdiction,
        publication_year=candidate.publication_year,
        lyricist_death_year=candidate.lyricist_death_year,
        renewal_status=candidate.renewal_status,
    )
