from __future__ import annotations

from pathlib import Path

import requests

from safe_lyrics_checker.cli import main
from safe_lyrics_checker.http_cache import HttpCache
from safe_lyrics_checker.search_engine import search_candidates


class DummyResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


def test_http_cache_reuses_cached_response(monkeypatch, tmp_path: Path) -> None:
    calls = {"count": 0}

    def fake_get(url: str, timeout: int = 15):
        calls["count"] += 1
        return DummyResponse("<html><a href='/ebooks/1'>Sample Title</a></html>")

    monkeypatch.setattr("safe_lyrics_checker.http_cache.requests.get", fake_get)
    cache = HttpCache(db_path=tmp_path / "cache.sqlite")

    url = "https://www.gutenberg.org/ebooks/search/?query=test"
    first = cache.get_text(url)
    second = cache.get_text(url)

    assert first == second
    assert calls["count"] == 1


def test_search_candidates_parses_and_enriches(monkeypatch, tmp_path: Path) -> None:
    responses = {
        "https://www.gutenberg.org/ebooks/search/?query=amazing+grace": (
            "<a href='/ebooks/123'>Amazing Grace</a>"
        ),
        "https://www.gutenberg.org/ebooks/123": (
            "Published 1929. lyricist died 1950. not renewed."
        ),
    }

    def fake_get(url: str, timeout: int = 15):
        return DummyResponse(responses[url])

    monkeypatch.setattr("safe_lyrics_checker.http_cache.requests.get", fake_get)
    cache = HttpCache(db_path=tmp_path / "cache.sqlite")

    candidates = search_candidates(
        "amazing grace",
        sources=["gutenberg"],
        max_results=5,
        cache=cache,
    )

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.title == "Amazing Grace"
    assert candidate.publication_year == 1929
    assert candidate.lyricist_death_year == 1950
    assert candidate.renewal_status == "not_renewed"
    assert candidate.evidence_urls


def test_cli_search_outputs_rights_status(monkeypatch, tmp_path: Path) -> None:
    responses = {
        "https://www.gutenberg.org/ebooks/search/?query=amazing+grace": (
            "<a href='/ebooks/123'>Amazing Grace</a>"
        ),
        "https://www.gutenberg.org/ebooks/123": "Published 1929. not renewed.",
    }

    def fake_get(url: str, timeout: int = 15):
        return DummyResponse(responses[url])

    monkeypatch.setattr("safe_lyrics_checker.http_cache.requests.get", fake_get)
    monkeypatch.chdir(tmp_path)

    exit_code = main([
        "search",
        "amazing grace",
        "--jurisdiction",
        "US",
        "--sources",
        "gutenberg",
        "--max-results",
        "1",
    ])

    assert exit_code == 0


def test_search_skips_worldcat_http_error_by_default(monkeypatch, tmp_path: Path, capsys) -> None:
    responses = {
        "https://www.gutenberg.org/ebooks/search/?query=amazing+grace": (
            "<a href='/ebooks/123'>Amazing Grace</a>"
        ),
        "https://www.gutenberg.org/ebooks/123": "Published 1929. not renewed.",
    }

    def fake_get(url: str, timeout: int = 15):
        if url.startswith("https://www.worldcat.org/search"):
            response = requests.Response()
            response.status_code = 403
            response.reason = "Forbidden"
            response.url = url
            raise requests.HTTPError(response=response)
        return DummyResponse(responses[url])

    monkeypatch.setattr("safe_lyrics_checker.http_cache.requests.get", fake_get)
    monkeypatch.chdir(tmp_path)

    exit_code = main([
        "search",
        "amazing grace",
        "--jurisdiction",
        "US",
        "--sources",
        "worldcat,gutenberg",
        "--max-results",
        "1",
    ])

    stderr = capsys.readouterr().err
    assert exit_code == 0
    assert "WARN: worldcat search failed (403 Forbidden) — skipping." in stderr


def test_search_with_only_failing_source_returns_unknown(monkeypatch, tmp_path: Path, capsys) -> None:
    def fake_get(url: str, timeout: int = 15):
        response = requests.Response()
        response.status_code = 403
        response.reason = "Forbidden"
        response.url = url
        raise requests.HTTPError(response=response)

    monkeypatch.setattr("safe_lyrics_checker.http_cache.requests.get", fake_get)
    monkeypatch.chdir(tmp_path)

    exit_code = main([
        "search",
        "amazing grace",
        "--jurisdiction",
        "US",
        "--sources",
        "worldcat",
    ])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "WARN: worldcat search failed (403 Forbidden) — skipping." in captured.err
    assert "No candidates found from selected sources." in captured.out


def test_search_strict_mode_raises_http_error(monkeypatch, tmp_path: Path) -> None:
    def fake_get(url: str, timeout: int = 15):
        response = requests.Response()
        response.status_code = 403
        response.reason = "Forbidden"
        response.url = url
        raise requests.HTTPError(response=response)

    monkeypatch.setattr("safe_lyrics_checker.http_cache.requests.get", fake_get)
    monkeypatch.chdir(tmp_path)

    import pytest

    with pytest.raises(requests.HTTPError):
        main([
            "search",
            "amazing grace",
            "--jurisdiction",
            "US",
            "--sources",
            "worldcat",
            "--strict",
        ])
