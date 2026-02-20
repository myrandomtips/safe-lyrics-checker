from safe_lyrics_checker.cli import main


def test_rights_check_safe_exit_code(capsys) -> None:
    code = main(["rights-check", "--jurisdiction", "US", "--publication-year", "1929"])
    captured = capsys.readouterr()
    assert code == 0
    assert "SAFE" in captured.out


def test_rights_check_unknown_exit_code(capsys) -> None:
    code = main(["rights-check", "--jurisdiction", "US", "--publication-year", "1930", "--renewal-status", "unknown"])
    captured = capsys.readouterr()
    assert code == 2
    assert "UNKNOWN" in captured.out


def test_quote_check_works_as_secondary_command(capsys) -> None:
    code = main(["quote-check", "line1\nline2\nline3\nline4\nline5", "--max-lines", "4"])
    captured = capsys.readouterr()
    assert code == 1
    assert "Result: UNSAFE" in captured.out
