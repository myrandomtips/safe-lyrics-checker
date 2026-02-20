from safe_lyrics_checker.cli import main


def test_cli_returns_success_for_safe_excerpt(capsys) -> None:
    code = main(["gentle humming by the sea"])
    captured = capsys.readouterr()

    assert code == 0
    assert "Result: SAFE" in captured.out


def test_cli_returns_error_for_unsafe_excerpt(capsys) -> None:
    code = main(["line1\nline2\nline3\nline4\nline5", "--max-lines", "4"])
    captured = capsys.readouterr()

    assert code == 1
    assert "Result: UNSAFE" in captured.out
