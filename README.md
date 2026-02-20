# safe-lyrics-checker

A Python CLI project for running conservative checks on lyric excerpts before publishing them.

## What this project includes

- A packaged CLI app named `safe_lyrics_checker`.
- A reusable rules engine module for excerpt checks.
- Unit tests for both rules logic and CLI behavior.

## Safety rules in this initial version

The rules engine flags an excerpt as **unsafe** when any of these are true:

1. The excerpt exceeds a configurable maximum word count (`--max-words`, default `90`).
2. The excerpt exceeds a configurable maximum number of non-empty lines (`--max-lines`, default `4`).
3. The excerpt exactly matches a known lyric segment in an optional corpus file.

## Project structure

```text
safe_lyrics_checker/
  __init__.py
  cli.py
  rules_engine.py
tests/
  test_cli.py
  test_rules_engine.py
pyproject.toml
README.md
```

## Initial setup

```bash
python -m pip install -e '.[dev]'
```

## Run tests

```bash
pytest
```

## CLI usage

### 1) Pass excerpt directly

```bash
safe-lyrics-checker "gentle humming by the sea"
```

### 2) Read excerpt from a file

```bash
safe-lyrics-checker --file excerpt.txt
```

### 3) Include a known-lyrics corpus file

Provide one known lyric segment per line.

```bash
safe-lyrics-checker --file excerpt.txt --known-lyrics-file known_lyrics.txt
```

### Exit codes

- `0`: excerpt considered safe by current rule set.
- `1`: one or more rules were violated.
