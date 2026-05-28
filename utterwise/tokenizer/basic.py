from __future__ import annotations

import re

from utterwise.math import find_math_spans
from utterwise.tokens import Token


TOKEN_RE = re.compile(
    r"""
    (?P<url>https?://[^\s]+|www\.[^\s]+)
    |(?P<email>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})
    |(?P<phone>\+?\d[\d().-]{6,}\d)
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


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    cursor = 0
    for start, end in find_math_spans(text):
        if cursor < start:
            tokens.extend(_tokenize_plain(text[cursor:start], cursor))
        tokens.append(Token(type="MATH", value=text[start:end], start=start, end=end))
        cursor = end

    if cursor < len(text):
        tokens.extend(_tokenize_plain(text[cursor:], cursor))
    return tokens


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
