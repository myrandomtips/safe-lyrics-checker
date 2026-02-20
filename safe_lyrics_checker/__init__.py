"""safe_lyrics_checker package."""

from .quote_safety import CheckResult, check_quote_safety
from .rights_engine import RightsResult, RightsStatus, check_lyrics_rights

__all__ = [
    "CheckResult",
    "RightsResult",
    "RightsStatus",
    "check_quote_safety",
    "check_lyrics_rights",
]
