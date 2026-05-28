from __future__ import annotations

from dataclasses import dataclass

from utterwise.config import NormalizeConfig
from utterwise.math import has_math
from utterwise.normalizers.preprocess import has_markdown
from utterwise.tokens import Token


@dataclass(frozen=True, slots=True)
class DetectionFlags:
    url: bool = False
    email: bool = False
    number: bool = False
    year: bool = False
    ordinal: bool = False
    version: bool = False
    phone: bool = False
    acronym: bool = False
    percentage: bool = False
    currency: bool = False
    date: bool = False
    temperature: bool = False
    math: bool = False
    symbol: bool = False
    punctuation: bool = False
    markdown: bool = False


def detect(
    text: str,
    tokens: list[Token] | None = None,
    config: NormalizeConfig | None = None,
) -> DetectionFlags:
    active_config = config or NormalizeConfig()
    values = tokens or []
    return DetectionFlags(
        url=any(token.type == "URL" for token in values) or "http://" in text or "https://" in text,
        email=any(token.type == "EMAIL" for token in values) or "@" in text,
        number=any(token.type == "CARDINAL" for token in values),
        year=any(token.value.isdigit() and len(token.value) == 4 for token in values),
        ordinal=any(token.type == "ORDINAL" for token in values),
        version=any(token.type == "VERSION" for token in values),
        phone=any(token.type == "PHONE" for token in values),
        acronym=any(token.type == "ACRONYM" for token in values),
        percentage=any(token.type == "PERCENTAGE" for token in values),
        currency=any(token.type == "CURRENCY" for token in values),
        date=any(token.type == "DATE" for token in values),
        temperature=any(token.type == "TEMPERATURE" for token in values),
        math=active_config.enable_math and (any(token.type == "MATH" for token in values) or has_math(text)),
        symbol=any(token.type == "SYMBOL" for token in values),
        punctuation=any(token.type == "PUNCTUATION" for token in values),
        markdown=has_markdown(text),
    )
