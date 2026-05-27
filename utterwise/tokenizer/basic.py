from __future__ import annotations

import re

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
    for match in TOKEN_RE.finditer(text):
        kind = match.lastgroup or "word"
        tokens.append(
            Token(
                type=RAW_TO_TYPE[kind],
                value=match.group(),
                start=match.start(),
                end=match.end(),
            )
        )
    return tokens
