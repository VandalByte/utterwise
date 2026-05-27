from __future__ import annotations

from utterwise import explain, normalize


def test_exact_rule_priority_for_phone() -> None:
    trace = explain("Call 9876543210")
    phone_token = next(token for token in trace["tokens"] if token["value"] == "9876543210")

    assert phone_token["type"] == "PHONE"
    assert phone_token["rule"] == "phone_exact"
    assert normalize("Call 9876543210") == "Call nine eight seven six five four three two one zero"


def test_ambiguous_year_uses_context_candidates() -> None:
    trace = explain("Born in 1998")
    year_token = next(token for token in trace["tokens"] if token["value"] == "1998")

    assert year_token["type"] == "YEAR"
    assert year_token["rule"] == "year_context"
    assert [candidate["type"] for candidate in year_token["candidates"]] == ["YEAR", "CARDINAL"]


def test_ambiguous_cardinal_uses_context_candidates() -> None:
    trace = explain("The value is 1998")
    number_token = next(token for token in trace["tokens"] if token["value"] == "1998")

    assert number_token["type"] == "CARDINAL"
    assert number_token["rule"] == "cardinal_context"
    assert normalize("The value is 1998") == "The value is one thousand nine hundred ninety eight"


def test_contextual_version_rule() -> None:
    trace = explain("Python 3.12")
    version_token = next(token for token in trace["tokens"] if token["value"] == "3.12")

    assert version_token["type"] == "VERSION"
    assert version_token["rule"] == "version_context"
    assert normalize("Python 3.12") == "Python three point twelve"
