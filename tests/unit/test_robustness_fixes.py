from __future__ import annotations

from utterwise import NormalizeConfig, explain, normalize
from utterwise.detectors import detect
from utterwise.normalizers.preprocess import preprocess
from utterwise.tokenizer import tokenize


def test_large_numbers_are_supported_until_billion_range() -> None:
    assert normalize("9999999") == "nine million nine hundred ninety nine thousand nine hundred ninety nine"
    assert normalize("1000000000") == "one billion"


def test_numbers_above_supported_range_fall_back_to_digits() -> None:
    trace = explain("1000000000000")
    token = trace["tokens"][0]

    assert trace["output"] == "one zero zero zero zero zero zero zero zero zero zero zero zero"
    assert token["metadata"]["number_fallback"] == "above_supported_range_digit_spellout"


def test_decimal_cardinals_spell_fraction_digits() -> None:
    assert normalize("3.145") == "three point one four five"
    assert normalize("12.08") == "twelve point zero eight"
    assert normalize("0.5") == "zero point five"


def test_leading_zero_numbers_are_spelled_digit_by_digit() -> None:
    assert normalize("James bond 007") == "James bond zero zero seven"
    assert normalize("00042") == "zero zero zero four two"


def test_version_logic_keeps_multi_part_versions_and_contextual_versions() -> None:
    assert normalize("0.1.0") == "zero point one point zero"
    assert normalize("v0.1.0") == "v zero point one point zero"
    assert normalize("Python 3.12") == "Python three point twelve"
    assert normalize("3.145") == "three point one four five"


def test_bare_domain_is_url() -> None:
    trace = explain("go visit google.com")
    token = next(token for token in trace["tokens"] if token["value"] == "google.com")

    assert trace["output"] == "go visit google dot com"
    assert token["type"] == "URL"
    assert token["rule"] == "url_exact"


def test_invalid_date_is_not_date_or_math() -> None:
    text = "Call me at 99/99/2004"
    tokens = tokenize(preprocess(text))
    flags = detect(text, tokens)
    trace = explain(text)
    token = next(token for token in trace["tokens"] if token["value"] == "99/99/2004")

    assert flags.date is False
    assert token["type"] == "TEXT"
    assert token["spoken"] == "99/99/2004"
    assert token["rule"] == "identity"


def test_date_format_config_controls_slash_date_interpretation() -> None:
    assert normalize("03/04/2026") == "third of April twenty twenty six"
    assert normalize("04/03/2026", config=NormalizeConfig(date_format="MDY")) == "third of April twenty twenty six"
