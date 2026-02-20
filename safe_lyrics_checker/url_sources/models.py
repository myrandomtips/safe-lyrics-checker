from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class UrlMetadata:
    title: Optional[str] = None
    lyricist_or_composer: Optional[str] = None
    publication_year: Optional[int] = None
    lyricist_death_year: Optional[int] = None
    renewal_status: str = "unknown"


@dataclass
class UrlEvaluation:
    metadata: UrlMetadata
    warning: Optional[str] = None
