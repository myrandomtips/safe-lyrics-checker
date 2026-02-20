# safe-lyrics-checker

`safe-lyrics-checker` is a conservative, metadata-only copyright safety checker for song lyrics.

> **Important:** This tool does **not** provide legal advice.
> It is designed to provide conservative status guidance from limited metadata.

## Core purpose

The primary feature is `rights-check`, which classifies lyric rights status as:

- `SAFE`
- `NOT_SAFE`
- `UNKNOWN`

using only metadata (jurisdiction, publication year, lyricist death year, and US renewal status).

The tool does **not** fetch lyric text, does **not** scrape websites, and does **not** use lyric databases.

## Conservative rules implemented

### UK / AU

- `SAFE` if lyricist death year is `<= 1954`.
- `NOT_SAFE` if lyricist death year is `>= 1955`.
- `UNKNOWN` if lyricist death year is missing.

### US

- Publication year `<= 1929` -> `SAFE`.
- Publication year `1930-1963`:
  - `SAFE` only when `renewal_status=not_renewed`.
  - `UNKNOWN` when `renewal_status=unknown` or `renewal_status=renewed`.
- Publication year `1964-1977` -> `NOT_SAFE`.
- Publication year `>= 1978`:
  - `SAFE` only if lyricist death year `<= 1954`.
  - `NOT_SAFE` if death year `>= 1955`.
  - `UNKNOWN` if death year is missing.

## CLI

## Primary command: `rights-check`

```bash
safe-lyrics-checker rights-check --jurisdiction US --publication-year 1929
```

```bash
safe-lyrics-checker rights-check --jurisdiction US --publication-year 1930 --renewal-status not_renewed
```

```bash
safe-lyrics-checker rights-check --jurisdiction UK --lyricist-death-year 1955
```

Arguments:

- `--jurisdiction [US|UK|AU]` (required)
- `--publication-year INT` (required for US)
- `--lyricist-death-year INT` (optional; required in life+70 paths)
- `--renewal-status [unknown|renewed|not_renewed]` (US 1930-1963)

Output:

- One status line: `SAFE`, `NOT_SAFE`, or `UNKNOWN`
- One short explanation line

Exit codes:

- `0` = `SAFE`
- `1` = `NOT_SAFE`
- `2` = `UNKNOWN`

## Secondary command: `quote-check`

A legacy/secondary heuristic checker for quote length and exact-match checks.
It is **not** the primary legal status engine.

## Setup

```bash
python -m pip install -e '.[dev]'
pytest
```
