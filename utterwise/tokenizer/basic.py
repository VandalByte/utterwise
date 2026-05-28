from __future__ import annotations

import re

from utterwise.math import find_math_spans
from utterwise.tokens import Token


TEMPERATURE_RE = re.compile(r"-?\d+(?:\.\d+)?\s*(?:°\s*)?[CF]\b")
TEMPERATURE_CONTEXT_WORDS = {
    "celsius",
    "degrees",
    "fahrenheit",
    "forecast",
    "high",
    "low",
    "outside",
    "temperature",
    "temp",
    "weather",
}

TOKEN_RE = re.compile(
    r"""
    (?P<url>https?://[^\s]+|www\.[^\s]+)
    |(?P<email>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})
    |(?P<phone>\+?\d[\d().-]{6,}\d)
    |(?P<temperature>-?\d+(?:\.\d+)?\s*°\s*[CF]\b)
    |(?P<percentage>\d+(?:\.\d+)?%)
    |(?P<version>v\d+(?:\.\d+)+)
    |(?P<ordinal>\d+(?:st|nd|rd|th))
    |(?P<number>\d+(?:[.,]\d+)*)
    |(?P<acronym>[A-Z]{2,})
    |(?P<word>[A-Za-z]+(?:'[A-Za-z]+)?)
    |(?P<symbol>[&%+→=×÷])
    |(?P<punctuation>[^\w\s])
    """,
    re.VERBOSE,
)


RAW_TO_TYPE = {
    "url": "URL",
    "email": "EMAIL",
    "phone": "PHONE",
    "temperature": "TEMPERATURE",
    "percentage": "PERCENTAGE",
    "version": "VERSION",
    "ordinal": "ORDINAL",
    "number": "CARDINAL",
    "acronym": "ACRONYM",
    "word": "WORD",
    "symbol": "SYMBOL",
    "punctuation": "PUNCTUATION",
}


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    cursor = 0
    for token_type, start, end in _semantic_spans(text):
        if cursor < start:
            tokens.extend(_tokenize_plain(text[cursor:start], cursor))
        tokens.append(Token(type=token_type, value=text[start:end], start=start, end=end))
        cursor = end

    if cursor < len(text):
        tokens.extend(_tokenize_plain(text[cursor:], cursor))
    return tokens


def _semantic_spans(text: str) -> list[tuple[str, int, int]]:
    spans = [("TEMPERATURE", start, end) for start, end in _find_temperature_spans(text)]
    spans.extend(("MATH", start, end) for start, end in find_math_spans(text))
    return _merge_semantic_spans(spans)


def _find_temperature_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    for match in TEMPERATURE_RE.finditer(text):
        value = match.group()
        if "°" in value or _has_temperature_context(text, match.start(), match.end()):
            spans.append((match.start(), match.end()))
    return spans


def _has_temperature_context(text: str, start: int, end: int) -> bool:
    window = f"{text[max(0, start - 40):start]} {text[end:end + 40]}".lower()
    return any(word in window for word in TEMPERATURE_CONTEXT_WORDS)


def _merge_semantic_spans(spans: list[tuple[str, int, int]]) -> list[tuple[str, int, int]]:
    kept: list[tuple[str, int, int]] = []
    for token_type, start, end in sorted(spans, key=lambda span: (span[1], span[2])):
        if kept and start < kept[-1][2]:
            continue
        kept.append((token_type, start, end))
    return kept


def _tokenize_plain(text: str, offset: int) -> list[Token]:
    tokens: list[Token] = []
    for match in TOKEN_RE.finditer(text):
        kind = match.lastgroup or "word"
        tokens.append(
            Token(
                type=RAW_TO_TYPE[kind],
                value=match.group(),
                start=offset + match.start(),
                end=offset + match.end(),
            )
        )
    return tokens
