from __future__ import annotations

from xml.etree import ElementTree

from utterwise import explain, normalize, normalize_ssml


def test_normalize_plain_text() -> None:
    assert normalize("I have 42 apples") == "I have forty two apples"


def test_normalize_ssml_is_valid_xml() -> None:
    ssml = normalize_ssml("A & B")

    root = ElementTree.fromstring(ssml)

    assert root.tag == "speak"
    assert root.text == "A and B"


def test_explain_contains_token_trace() -> None:
    trace = explain("in 2024")

    year_token = next(token for token in trace["tokens"] if token["value"] == "2024")

    assert trace["output"] == "in twenty twenty four"
    assert year_token["type"] == "YEAR"
    assert year_token["rule"] == "year_context"
    assert year_token["confidence"] > 0
    assert year_token["start"] >= 0
    assert year_token["end"] > year_token["start"]
    assert year_token["candidates"]


def test_unknown_policy_raises() -> None:
    try:
        normalize("hello", policy="unknown")
    except ValueError as exc:
        assert "Unknown policy" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown policy")
