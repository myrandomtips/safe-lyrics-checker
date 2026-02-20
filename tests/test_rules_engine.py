from safe_lyrics_checker.rules_engine import check_lyrics_excerpt


def test_safe_excerpt_has_no_rule_hits() -> None:
    result = check_lyrics_excerpt("sunrise over quiet water")
    assert result.is_safe is True
    assert result.rule_hits == []


def test_word_limit_violation() -> None:
    excerpt = "word " * 20
    result = check_lyrics_excerpt(excerpt, max_words=10)
    assert result.is_safe is False
    assert "max_words" in result.rule_hits


def test_line_limit_violation() -> None:
    excerpt = "a\nb\nc\nd\ne"
    result = check_lyrics_excerpt(excerpt, max_lines=4)
    assert result.is_safe is False
    assert "max_lines" in result.rule_hits


def test_known_lyrics_match_violation() -> None:
    result = check_lyrics_excerpt(
        "Hello from the other side",
        known_lyrics=["hello from the other side", "another line"],
    )
    assert result.is_safe is False
    assert "known_lyric_match" in result.rule_hits
