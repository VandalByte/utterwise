from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from utterwise.tokens import Candidate, Token


Condition = Callable[[Token], bool]


@dataclass(frozen=True, slots=True)
class Rule:
    name: str
    priority: int
    token_type: str
    confidence: float
    reason: str
    condition: Condition

    def matches(self, token: Token) -> bool:
        return self.condition(token)


YEAR_HINTS = {
    "after",
    "before",
    "born",
    "by",
    "during",
    "died",
    "established",
    "founded",
    "from",
    "in",
    "since",
    "until",
    "year",
}

CARDINAL_HINTS = {
    "amount",
    "code",
    "count",
    "equals",
    "id",
    "is",
    "number",
    "quantity",
    "score",
    "total",
    "value",
}

VERSION_HINTS = {
    "api",
    "django",
    "node",
    "npm",
    "python",
    "release",
    "version",
}


EXACT_RULES = [
    Rule("math_exact", 110, "MATH", 0.98, "math expression span detected", lambda token: token.type == "MATH"),
    Rule("date_exact", 108, "DATE", 0.96, "date pattern matched", lambda token: token.type == "DATE"),
    Rule("currency_exact", 107, "CURRENCY", 0.96, "currency pattern matched", lambda token: token.type == "CURRENCY"),
    Rule("temperature_exact", 105, "TEMPERATURE", 0.96, "temperature pattern matched", lambda token: token.type == "TEMPERATURE"),
    Rule("url_exact", 100, "URL", 0.98, "URL pattern matched", lambda token: token.type == "URL"),
    Rule("email_exact", 100, "EMAIL", 0.98, "email pattern matched", lambda token: token.type == "EMAIL"),
    Rule("phone_exact", 95, "PHONE", 0.96, "phone-like digit pattern matched", lambda token: token.type == "PHONE" or _is_phone_number(token.value)),
    Rule("percentage_exact", 90, "PERCENTAGE", 0.97, "percentage pattern matched", lambda token: token.type == "PERCENTAGE"),
    Rule("version_prefixed", 88, "VERSION", 0.97, "prefixed version pattern matched", lambda token: token.type == "VERSION"),
    Rule("version_context", 86, "VERSION", 0.9, "decimal number in version context", lambda token: _is_contextual_version(token)),
    Rule("ordinal_exact", 84, "ORDINAL", 0.97, "ordinal suffix pattern matched", lambda token: token.type == "ORDINAL"),
    Rule("acronym_exact", 80, "ACRONYM", 0.94, "uppercase acronym pattern matched", lambda token: token.type == "ACRONYM"),
    Rule("symbol_exact", 70, "SYMBOL", 0.95, "symbol pattern matched", lambda token: token.type == "SYMBOL"),
    Rule("punctuation_exact", 60, "PUNCTUATION", 0.7, "punctuation pattern matched", lambda token: token.type == "PUNCTUATION"),
]


def exact_rules() -> list[Rule]:
    return sorted(EXACT_RULES, key=lambda rule: rule.priority, reverse=True)


def numeric_candidates(token: Token) -> list[Candidate]:
    if token.type != "CARDINAL":
        return []

    if token.value.isdigit() and len(token.value) == 4:
        return _year_or_cardinal_candidates(token)

    if token.value.isdigit() and len(token.value) == 3:
        return [
            Candidate("PHONE", 0.42, "phone_possible_short_code", "three-digit number can be a short phone or emergency number"),
            Candidate("FLIGHT_NO", 0.2, "flight_possible_number", "three-digit number can be a flight or route number"),
            Candidate("CARDINAL", 0.7, "cardinal_possible_number", "three-digit number can be read as a cardinal"),
        ]

    return [
        Candidate("CARDINAL", 0.9, "cardinal_default", "numeric token without a stronger semantic context"),
    ]


def _year_or_cardinal_candidates(token: Token) -> list[Candidate]:
    value = int(token.value)
    previous_words = set(token.context.get("previous_words", []))
    next_words = set(token.context.get("next_words", []))
    context_words = previous_words | next_words

    if context_words & YEAR_HINTS and 1000 <= value <= 2099:
        return [
            Candidate("YEAR", 0.92, "year_context", "nearby word suggests a calendar year"),
            Candidate("CARDINAL", 0.6, "cardinal_fallback", "four-digit number can be read as a cardinal"),
        ]

    if context_words & CARDINAL_HINTS:
        return [
            Candidate("CARDINAL", 0.88, "cardinal_context", "nearby word suggests a quantity or value"),
            Candidate("YEAR", 0.45, "year_weak", "four-digit number is in a possible year shape"),
        ]

    if 1900 <= value <= 2099:
        return [
            Candidate("YEAR", 0.72, "year_range", "number is in a common modern year range"),
            Candidate("CARDINAL", 0.62, "cardinal_fallback", "four-digit number can be read as a cardinal"),
        ]

    return [
        Candidate("CARDINAL", 0.86, "cardinal_default", "number has no year context"),
    ]


def _is_phone_number(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    return value.isdigit() and len(digits) == 10


def _is_contextual_version(token: Token) -> bool:
    if token.type != "CARDINAL" or "." not in token.value:
        return False
    previous_words = set(token.context.get("previous_words", []))
    return bool(previous_words & VERSION_HINTS)
