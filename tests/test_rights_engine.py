from safe_lyrics_checker.rights_engine import RightsStatus, check_lyrics_rights


def test_us_1929_vs_1930_boundary() -> None:
    safe = check_lyrics_rights(jurisdiction="US", publication_year=1929)
    unknown = check_lyrics_rights(jurisdiction="US", publication_year=1930)
    assert safe.status is RightsStatus.SAFE
    assert unknown.status is RightsStatus.UNKNOWN


def test_us_1963_vs_1964_boundary() -> None:
    unknown = check_lyrics_rights(jurisdiction="US", publication_year=1963, renewal_status="renewed")
    not_safe = check_lyrics_rights(jurisdiction="US", publication_year=1964)
    assert unknown.status is RightsStatus.UNKNOWN
    assert not_safe.status is RightsStatus.NOT_SAFE


def test_us_1977_vs_1978_boundary() -> None:
    not_safe_1977 = check_lyrics_rights(jurisdiction="US", publication_year=1977)
    unknown_1978 = check_lyrics_rights(jurisdiction="US", publication_year=1978)
    assert not_safe_1977.status is RightsStatus.NOT_SAFE
    assert unknown_1978.status is RightsStatus.UNKNOWN


def test_uk_au_1954_vs_1955_boundary() -> None:
    uk_safe = check_lyrics_rights(jurisdiction="UK", lyricist_death_year=1954)
    uk_not_safe = check_lyrics_rights(jurisdiction="UK", lyricist_death_year=1955)
    au_safe = check_lyrics_rights(jurisdiction="AU", lyricist_death_year=1954)
    au_not_safe = check_lyrics_rights(jurisdiction="AU", lyricist_death_year=1955)
    assert uk_safe.status is RightsStatus.SAFE
    assert uk_not_safe.status is RightsStatus.NOT_SAFE
    assert au_safe.status is RightsStatus.SAFE
    assert au_not_safe.status is RightsStatus.NOT_SAFE


def test_missing_metadata_unknown() -> None:
    us_missing_pub = check_lyrics_rights(jurisdiction="US")
    uk_missing_death = check_lyrics_rights(jurisdiction="UK")
    us_1930_unknown_renewal = check_lyrics_rights(jurisdiction="US", publication_year=1930, renewal_status="unknown")
    assert us_missing_pub.status is RightsStatus.UNKNOWN
    assert uk_missing_death.status is RightsStatus.UNKNOWN
    assert us_1930_unknown_renewal.status is RightsStatus.UNKNOWN
