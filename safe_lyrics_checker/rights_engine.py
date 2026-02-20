"""Primary metadata-only rights status engine for song lyrics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RightsStatus(str, Enum):
    SAFE = "SAFE"
    NOT_SAFE = "NOT_SAFE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RightsResult:
    status: RightsStatus
    explanation: str


def check_lyrics_rights(
    *,
    jurisdiction: str,
    publication_year: Optional[int] = None,
    lyricist_death_year: Optional[int] = None,
    renewal_status: str = "unknown",
) -> RightsResult:
    """Determine rights status using metadata only.

    Jurisdictions: US, UK, AU.
    """

    code = jurisdiction.upper()
    if code not in {"US", "UK", "AU"}:
        return RightsResult(
            status=RightsStatus.UNKNOWN,
            explanation="Unsupported jurisdiction; supported values are US, UK, AU.",
        )

    if code in {"UK", "AU"}:
        if lyricist_death_year is None:
            return RightsResult(
                status=RightsStatus.UNKNOWN,
                explanation=(
                    f"{code}: lyricist death year is required for life+70 analysis."
                ),
            )
        if lyricist_death_year <= 1954:
            return RightsResult(
                status=RightsStatus.SAFE,
                explanation=(
                    f"{code}: lyricist died in {lyricist_death_year} (<=1954), treated as public domain."
                ),
            )
        return RightsResult(
            status=RightsStatus.NOT_SAFE,
            explanation=(
                f"{code}: lyricist died in {lyricist_death_year} (>1954), conservatively treated as not public domain."
            ),
        )

    # US rules
    if publication_year is None:
        return RightsResult(
            status=RightsStatus.UNKNOWN,
            explanation="US: publication year is required.",
        )

    if publication_year <= 1929:
        return RightsResult(
            status=RightsStatus.SAFE,
            explanation=f"US: first publication year {publication_year} is <= 1929.",
        )

    if 1930 <= publication_year <= 1963:
        normalized_renewal = renewal_status.lower()
        if normalized_renewal == "not_renewed":
            return RightsResult(
                status=RightsStatus.SAFE,
                explanation=(
                    "US: publication in 1930-1963 with renewal status not_renewed."
                ),
            )
        if normalized_renewal in {"unknown", "renewed"}:
            return RightsResult(
                status=RightsStatus.UNKNOWN,
                explanation=(
                    f"US: publication in 1930-1963 with renewal status {normalized_renewal}."
                ),
            )
        return RightsResult(
            status=RightsStatus.UNKNOWN,
            explanation="US: invalid renewal status; use unknown|renewed|not_renewed.",
        )

    if 1964 <= publication_year <= 1977:
        return RightsResult(
            status=RightsStatus.NOT_SAFE,
            explanation="US: publication in 1964-1977 is conservatively not safe (95-year term).",
        )

    # publication_year >= 1978
    if lyricist_death_year is None:
        return RightsResult(
            status=RightsStatus.UNKNOWN,
            explanation="US: lyricist death year is required for post-1977 life+70 analysis.",
        )

    if lyricist_death_year <= 1954:
        return RightsResult(
            status=RightsStatus.SAFE,
            explanation=(
                "US: publication >=1978 and lyricist death year <=1954 (conservative life+70 safe)."
            ),
        )

    return RightsResult(
        status=RightsStatus.NOT_SAFE,
        explanation=(
            "US: publication >=1978 and lyricist death year >1954 (conservative not safe)."
        ),
    )
