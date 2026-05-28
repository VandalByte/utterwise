from __future__ import annotations

import re
from dataclasses import dataclass, field

from utterwise.math.latex import match_frac, match_sqrt, match_sum
from utterwise.math.sympy_adapter import try_parse_sympy
from utterwise.math.vocabulary import LATEX_WORDS, POWER_WORDS, SYMBOL_WORDS
from utterwise.verbalizers.numbers import cardinal_to_words


@dataclass(slots=True)
class MathSpeech:
    text: str
    parser: str
    rule: str
    confidence: float
    metadata: dict[str, str] = field(default_factory=dict)


def verbalize_math(value: str) -> MathSpeech:
    value = value.strip()
    try:
        if speech := _latex_rule(value):
            return speech
        if speech := _fast_rule(value):
            return speech

        _, parse_error = try_parse_sympy(value)
        if parse_error:
            return _fallback(value, parse_error)
        return MathSpeech(
            text=_speak_expression(value),
            parser="sympy",
            rule="sympy_expression",
            confidence=0.78,
            metadata={"math_source": value},
        )
    except Exception as exc:
        return _fallback(value, str(exc))


def _latex_rule(value: str) -> MathSpeech | None:
    if value in LATEX_WORDS:
        return MathSpeech(LATEX_WORDS[value], "latex", "latex_ellipsis", 0.98, {"math_source": value})

    if match := match_frac(value):
        numerator, denominator = match.groups()
        return MathSpeech(
            f"{_speak_expression(numerator)} over {_speak_expression(denominator)}",
            "latex",
            "latex_fraction",
            0.96,
            {"math_source": value},
        )

    if match := match_sqrt(value):
        return MathSpeech(
            f"square root of {_speak_expression(match.group(1))}",
            "latex",
            "latex_square_root",
            0.96,
            {"math_source": value},
        )

    if match := match_sum(value):
        lower, upper, body = match.groups()
        return MathSpeech(
            f"sum from {_speak_expression(lower)} to {_speak_expression(upper)} of {_speak_expression(body)}",
            "latex",
            "latex_sum",
            0.94,
            {"math_source": value},
        )

    if value.startswith("\\"):
        return _fallback(value, "unsupported LaTeX command")

    return None


def _fast_rule(value: str) -> MathSpeech | None:
    if any(signal in value for signal in ("^", "_", "/", "=", "+", "-", "*", "×", "÷", ",")):
        return MathSpeech(
            _speak_expression(value),
            "fast_rule",
            "inline_math_expression",
            0.9,
            {"math_source": value},
        )
    return None


def _speak_expression(value: str) -> str:
    value = value.strip()
    if not value:
        return ""

    if value in LATEX_WORDS:
        return LATEX_WORDS[value]

    if "," in value:
        return ", ".join(_speak_expression(part) for part in _split_top_level(value, ",") if part.strip())

    for operator, word in (("=", "equals"), ("+", "plus"), ("-", "minus")):
        parts = _split_top_level(value, operator)
        if len(parts) > 1:
            return f" {word} ".join(_speak_expression(part) for part in parts)

    parts = _split_top_level(value, "/")
    if len(parts) > 1:
        return f" {SYMBOL_WORDS['/']} ".join(_speak_expression(part) for part in parts)

    for operator in ("×", "*", "÷"):
        parts = _split_top_level(value, operator)
        if len(parts) > 1:
            return f" {SYMBOL_WORDS.get(operator, 'times')} ".join(_speak_expression(part) for part in parts)

    if match := re.fullmatch(r"\((.+)\)\^(\d+)", value):
        inner, power = match.groups()
        return f"open parenthesis {_speak_expression(inner)} close parenthesis {_power_to_words(power)}"

    if match := re.fullmatch(r"([A-Za-z0-9]+)\^(\d+)", value):
        base, power = match.groups()
        return f"{_speak_atom(base)} {_power_to_words(power)}"

    if match := re.fullmatch(r"([A-Za-z]+)_(\d+)", value):
        base, subscript = match.groups()
        return f"{_speak_atom(base)} sub {cardinal_to_words(subscript)}"

    return _speak_atom(value)


def _split_top_level(value: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(value):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(depth - 1, 0)
        elif char == delimiter and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    return parts


def _speak_atom(value: str) -> str:
    cleaned = value.strip()
    if cleaned.isdigit():
        return cardinal_to_words(cleaned)
    if re.fullmatch(r"[A-Za-z]{2,}", cleaned):
        return " ".join(cleaned)
    return cleaned


def _power_to_words(value: str) -> str:
    return POWER_WORDS.get(value, f"to the power of {cardinal_to_words(value)}")


def _fallback(value: str, parse_error: str) -> MathSpeech:
    return MathSpeech(
        text=value,
        parser="fallback",
        rule="math_safe_passthrough",
        confidence=0.35,
        metadata={"math_source": value, "parse_error": parse_error},
    )
