from __future__ import annotations

from .common import extract_metadata_generic
from .models import UrlMetadata


def extract_metadata(raw_html: str) -> UrlMetadata:
    return extract_metadata_generic(raw_html)
