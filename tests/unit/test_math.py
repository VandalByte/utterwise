from __future__ import annotations

from utterwise import explain, normalize
from utterwise.detectors import detect
from utterwise.math import find_math_spans, has_math
from utterwise.math.fast_rules import verbalize_math
from utterwise.normalizers.preprocess import preprocess
from utterwise.tokenizer import tokenize


def test_math_detection_gate() -> None:
    assert has_math("x^2") is True
    assert has_math("plain prose only") is False

    tokens = tokenize(preprocess("E = mc^2"))
    flags = detect("E = mc^2", tokens)

    assert flags.math is True
    assert [(token.type, token.value) for token in tokens] == [("MATH", "E = mc^2")]


def test_math_span_detection_ignores_plain_text() -> None:
    assert find_math_spans("Call 911 immediately") == []


def test_fast_rule_does_not_need_sympy(monkeypatch) -> None:
    def fail_sympy_import(value: str) -> tuple[None, str | None]:
        raise AssertionError("SymPy should not be called for fast power rules")

    monkeypatch.setattr("utterwise.math.fast_rules.try_parse_sympy", fail_sympy_import)

    speech = verbalize_math("x^2")

    assert speech.text == "x squared"
    assert speech.parser == "fast_rule"


def test_latex_command_verbalization() -> None:
    assert normalize(r"\sqrt{x+1}") == "square root of x plus one"
    assert normalize(r"\frac{a+b}{c}") == "a plus b over c"


def test_safe_passthrough_on_invalid_math() -> None:
    trace = explain(r"\unknown{x}")
    token = trace["tokens"][0]

    assert trace["output"] == r"\unknown{x}"
    assert token["type"] == "MATH"
    assert token["parser"] == "fallback"
    assert token["confidence"] == 0.35
    assert token["metadata"]["parse_error"]


def test_explain_metadata_for_math_token() -> None:
    trace = explain("x^2")
    token = trace["tokens"][0]

    assert token["type"] == "MATH"
    assert token["spoken"] == "x squared"
    assert token["parser"] == "fast_rule"
    assert token["rule"] == "inline_math_expression"
    assert token["metadata"]["math_source"] == "x^2"
