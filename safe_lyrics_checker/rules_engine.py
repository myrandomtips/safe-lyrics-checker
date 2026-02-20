"""Backward-compatible wrapper for quote safety checks.

Use :mod:`safe_lyrics_checker.quote_safety` for new code.
"""

from .quote_safety import CheckResult, check_quote_safety


def check_lyrics_excerpt(*args, **kwargs):
    """Alias maintained for compatibility with older integrations."""

    return check_quote_safety(*args, **kwargs)
