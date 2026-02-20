from __future__ import annotations

import re

from .common import extract_metadata_generic
from .models import UrlMetadata

EBOOK_RELEASE_RE = re.compile(r"(?:release date|published)\D{0,20}(1[5-9]\d{2}|20\d{2})", re.IGNORECASE)


def extract_metadata(raw_html: str) -> UrlMetadata:
    metadata = extract_metadata_generic(raw_html)
    match = EBOOK_RELEASE_RE.search(raw_html)
    if match:
        metadata.publication_year = int(match.group(1))
    return metadata
