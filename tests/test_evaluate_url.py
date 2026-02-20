from __future__ import annotations

from pathlib import Path

import requests

from safe_lyrics_checker.cli import main
from safe_lyrics_checker.http_cache import HttpCache
from safe_lyrics_checker.url_sources.evaluator import evaluate_url


class DummyResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


def test_evaluate_url_known_domain_extracts_metadata(monkeypatch, tmp_path: Path) -> None:
    body = """
    <html>
      <title>Amazing Grace - IMSLP</title>
      <body>
        Lyrics by John Newton. died 1807. Published 1920. not renewed.
      </body>
    </html>
    """

    def fake_get(url: str, timeout: int = 15, headers=None):
        return DummyResponse(body)

    monkeypatch.setattr("safe_lyrics_checker.http_cache.requests.get", fake_get)
    cache = HttpCache(db_path=tmp_path / "cache.sqlite")

    rights, evaluation = evaluate_url(
        "https://imslp.org/wiki/Amazing_Grace",
        "US",
        cache=cache,
    )

    assert rights.status.value == "SAFE"
    assert evaluation.metadata.title == "Amazing Grace - IMSLP"
    assert evaluation.metadata.lyricist_death_year == 1807
    assert evaluation.metadata.publication_year == 1920
    assert evaluation.metadata.renewal_status == "not_renewed"


def test_evaluate_url_returns_unknown_on_403(monkeypatch, tmp_path: Path, capsys) -> None:
    def fake_get(url: str, timeout: int = 15, headers=None):
        response = requests.Response()
        response.status_code = 403
        response.reason = "Forbidden"
        response.url = url
        raise requests.HTTPError(response=response)

    monkeypatch.setattr("safe_lyrics_checker.http_cache.requests.get", fake_get)
    monkeypatch.chdir(tmp_path)

    code = main([
        "evaluate-url",
        "--jurisdiction",
        "US",
        "https://loc.gov/item/test",
    ])
    captured = capsys.readouterr()

    assert code == 2
    assert "WARN: Received HTTP 403" in captured.out
    assert "Result: UNKNOWN" in captured.out


def test_evaluate_url_unknown_domain_insufficient_metadata(monkeypatch, tmp_path: Path, capsys) -> None:
    body = "<html><title>Example</title><body>No explicit metadata.</body></html>"

    def fake_get(url: str, timeout: int = 15, headers=None):
        return DummyResponse(body)

    monkeypatch.setattr("safe_lyrics_checker.http_cache.requests.get", fake_get)
    monkeypatch.chdir(tmp_path)

    code = main([
        "evaluate-url",
        "--jurisdiction",
        "UK",
        "https://example.com/work",
    ])
    captured = capsys.readouterr()

    assert code == 2
    assert "Result: UNKNOWN" in captured.out
    assert "Evidence URL: https://example.com/work" in captured.out
    assert "Publication year: UNKNOWN" in captured.out
