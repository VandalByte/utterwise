from __future__ import annotations

import re
from datetime import date
from typing import Any

from utterwise.config import NormalizeConfig
from utterwise.math import find_math_spans
from utterwise.tokens import Token


CURRENCY_RE = re.compile(r"[$€£]\s?\d+(?:,\d{3})*(?:\.\d{1,2})?")
DATE_RE = re.compile(
    r"""
    \b\d{4}-\d{1,2}-\d{1,2}\b
    |\b\d{1,2}/\d{1,2}/\d{4}\b
    |\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+\d{1,2},?\s+\d{4}\b
    """,
    re.IGNORECASE | re.VERBOSE,
)
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
    (?P<url>https?://[^\s]+|www\.[^\s]+|(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,})
    |(?P<email>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})
    |(?P<phone>\+?\d[\d().-]*[-().]\d[\d().-]{4,}\d|\+\d{7,15})
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
    "percentage": "PERCENTAGE",
    "version": "VERSION",
    "ordinal": "ORDINAL",
    "number": "CARDINAL",
    "acronym": "ACRONYM",
    "word": "WORD",
    "symbol": "SYMBOL",
    "punctuation": "PUNCTUATION",
}

MONTH_ALIASES = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def tokenize(text: str, config: NormalizeConfig | None = None) -> list[Token]:
    active_config = config or NormalizeConfig()
    tokens: list[Token] = []
    cursor = 0
    for token_type, start, end, metadata in _semantic_spans(text, active_config):
        if cursor < start:
            tokens.extend(_tokenize_plain(text[cursor:start], cursor))
        tokens.append(
            Token(
                type=token_type,
                value=text[start:end],
                start=start,
                end=end,
                metadata=metadata,
            )
        )
        cursor = end

    if cursor < len(text):
        tokens.extend(_tokenize_plain(text[cursor:], cursor))
    return tokens


def _semantic_spans(text: str, config: NormalizeConfig) -> list[tuple[str, int, int, dict[str, Any]]]:
    spans: list[tuple[str, int, int, int, dict[str, Any]]] = []
    if config.enable_dates:
        spans.extend(
            ("DATE", start, end, 100, metadata)
            for start, end, metadata in _find_date_spans(text, config)
        )
        spans.extend(
            ("TEXT", start, end, 99, metadata)
            for start, end, metadata in _find_invalid_date_spans(text, config)
        )
    if config.enable_currency:
        spans.extend(("CURRENCY", start, end, 90, {}) for start, end in _find_regex_spans(CURRENCY_RE, text))
    if config.enable_temperature:
        spans.extend(("TEMPERATURE", start, end, 80, {}) for start, end in _find_temperature_spans(text))
    if config.enable_math:
        spans.extend(("MATH", start, end, 10, {}) for start, end in find_math_spans(text))
    return _merge_semantic_spans(spans)


def _find_regex_spans(pattern: re.Pattern[str], text: str) -> list[tuple[int, int]]:
    return [(match.start(), match.end()) for match in pattern.finditer(text)]


def _find_date_spans(text: str, config: NormalizeConfig) -> list[tuple[int, int, dict[str, Any]]]:
    spans = []
    for match in DATE_RE.finditer(text):
        metadata = _date_metadata(match.group(), config.date_format)
        if metadata:
            spans.append((match.start(), match.end(), metadata))
    return spans


def _find_invalid_date_spans(text: str, config: NormalizeConfig) -> list[tuple[int, int, dict[str, Any]]]:
    spans = []
    for match in DATE_RE.finditer(text):
        if _date_metadata(match.group(), config.date_format) is None:
            spans.append((match.start(), match.end(), {"date_parse_error": "invalid_date"}))
    return spans


def _date_metadata(value: str, date_format: str) -> dict[str, Any] | None:
    text = value.strip().replace(",", "")
    if match := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text):
        year, month, day = (int(part) for part in match.groups())
        return _validated_date(day, month, year, "ISO")

    if match := re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text):
        first, second, year = (int(part) for part in match.groups())
        if date_format.upper() == "MDY":
            month, day = first, second
        else:
            day, month = first, second
        return _validated_date(day, month, year, date_format.upper())

    if match := re.fullmatch(r"([A-Za-z.]+)\s+(\d{1,2})\s+(\d{4})", text):
        month_text, day_text, year_text = match.groups()
        month = MONTH_ALIASES.get(month_text.rstrip(".").lower())
        if not month:
            return None
        return _validated_date(int(day_text), month, int(year_text), "MONTH_NAME")
    return None


def _validated_date(day: int, month: int, year: int, date_format: str) -> dict[str, Any] | None:
    try:
        date(year, month, day)
    except ValueError:
        return None
    return {
        "date_day": day,
        "date_month": month,
        "date_year": year,
        "date_format": date_format,
    }


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


def _merge_semantic_spans(
    spans: list[tuple[str, int, int, int, dict[str, Any]]],
) -> list[tuple[str, int, int, dict[str, Any]]]:
    kept: list[tuple[str, int, int, dict[str, Any]]] = []
    for token_type, start, end, priority, metadata in sorted(
        spans,
        key=lambda span: (span[1], -span[3], -(span[2] - span[1])),
    ):
        if kept and start < kept[-1][2]:
            continue
        kept.append((token_type, start, end, metadata))
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
