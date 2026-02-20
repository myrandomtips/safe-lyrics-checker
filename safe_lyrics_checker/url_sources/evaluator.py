from __future__ import annotations

from urllib.parse import urlparse

import requests

from ..http_cache import HttpCache
from ..rights_engine import RightsResult, check_lyrics_rights
from . import archive, cpdl, gutenberg, imslp, loc
from .common import extract_metadata_generic, has_sufficient_metadata
from .models import UrlEvaluation

ADAPTERS = {
    "imslp.org": imslp.extract_metadata,
    "cpdl.org": cpdl.extract_metadata,
    "gutenberg.org": gutenberg.extract_metadata,
    "archive.org": archive.extract_metadata,
    "loc.gov": loc.extract_metadata,
}

CLOUDFLARE_MARKERS = (
    "cloudflare",
    "attention required",
    "captcha",
    "access denied",
)


def _hostname(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def _find_adapter(url: str):
    host = _hostname(url)
    for domain, adapter in ADAPTERS.items():
        if host == domain or host.endswith(f".{domain}"):
            return adapter
    return extract_metadata_generic


def _is_antibot_page(raw_html: str) -> bool:
    lowered = raw_html.lower()
    return any(marker in lowered for marker in CLOUDFLARE_MARKERS)


def evaluate_url(url: str, jurisdiction: str, *, cache: HttpCache | None = None) -> tuple[RightsResult, UrlEvaluation]:
    cache = cache or HttpCache()

    try:
        raw_html = cache.get_text(url)
    except requests.Timeout:
        return (
            check_lyrics_rights(jurisdiction=jurisdiction, publication_year=None, lyricist_death_year=None, renewal_status="unknown"),
            UrlEvaluation(metadata=extract_metadata_generic(""), warning="Request timed out"),
        )
    except requests.HTTPError as exc:
        code = getattr(getattr(exc, "response", None), "status_code", None)
        if code == 403:
            warning = "Received HTTP 403 (possible anti-bot protection)"
        else:
            warning = f"HTTP error while fetching evidence URL ({code or 'unknown'})"
        return (
            check_lyrics_rights(jurisdiction=jurisdiction, publication_year=None, lyricist_death_year=None, renewal_status="unknown"),
            UrlEvaluation(metadata=extract_metadata_generic(""), warning=warning),
        )
    except requests.RequestException as exc:
        return (
            check_lyrics_rights(jurisdiction=jurisdiction, publication_year=None, lyricist_death_year=None, renewal_status="unknown"),
            UrlEvaluation(metadata=extract_metadata_generic(""), warning=f"Network error: {exc}"),
        )

    if _is_antibot_page(raw_html):
        return (
            check_lyrics_rights(jurisdiction=jurisdiction, publication_year=None, lyricist_death_year=None, renewal_status="unknown"),
            UrlEvaluation(metadata=extract_metadata_generic(""), warning="Blocked by anti-bot protection (Cloudflare/captcha)"),
        )

    adapter = _find_adapter(url)
    metadata = adapter(raw_html)

    if not has_sufficient_metadata(metadata):
        return (
            check_lyrics_rights(jurisdiction=jurisdiction, publication_year=None, lyricist_death_year=None, renewal_status="unknown"),
            UrlEvaluation(metadata=metadata),
        )

    rights = check_lyrics_rights(
        jurisdiction=jurisdiction,
        publication_year=metadata.publication_year,
        lyricist_death_year=metadata.lyricist_death_year,
        renewal_status=metadata.renewal_status,
    )
    return rights, UrlEvaluation(metadata=metadata)
