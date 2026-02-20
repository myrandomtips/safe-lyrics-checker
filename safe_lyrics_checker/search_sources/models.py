from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Candidate:
    title: str
    source: str
    work_url: str
    lyricist: Optional[str] = None
    composer: Optional[str] = None
    publication_year: Optional[int] = None
    lyricist_death_year: Optional[int] = None
    renewal_status: str = "unknown"
    evidence_urls: list[str] = field(default_factory=list)


@dataclass
class Fact:
    value: str
    source_url: str
