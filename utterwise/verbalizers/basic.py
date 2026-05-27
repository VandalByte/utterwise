from __future__ import annotations

import re
from urllib.parse import urlparse

from utterwise.policies.base import Policy
from utterwise.tokens import SpokenSegment, Token
from utterwise.verbalizers.numbers import cardinal_to_words, year_to_words


SYMBOLS = {
    "&": "and",
    "%": "percent",
    "→": "to",
    "+": "plus",
    "=": "equals",
    "×": "times",
    "÷": "divided by",
}

KNOWN_TERMS = {
    "openai": "open ai",
}

SKIP_PUNCTUATION = {".", ",", "!", "?", ":", ";", "(", ")", "[", "]", "{", "}", '"'}


def verbalize(tokens: list[Token], policy: Policy) -> list[SpokenSegment]:
    return [_verbalize_one(token, policy) for token in tokens]


def _verbalize_one(token: Token, policy: Policy) -> SpokenSegment:
    if token.type == "CARDINAL":
        return _segment(token, cardinal_to_words(token.value), "cardinal")
    if token.type == "YEAR":
        return _segment(token, year_to_words(token.value), "year")
    if token.type == "URL":
        return _segment(token, _url_to_words(token.value), "url")
    if token.type == "EMAIL":
        return _segment(token, _email_to_words(token.value), "email")
    if token.type == "SYMBOL":
        return _segment(token, SYMBOLS.get(token.value, token.value), "symbol")
    if token.type == "PUNCTUATION" and token.value in SKIP_PUNCTUATION:
        return _segment(token, "", "punctuation_skip")
    return _segment(token, token.value, "identity")


def _segment(token: Token, text: str, rule: str) -> SpokenSegment:
    return SpokenSegment(text=text, source=token, rule=rule, confidence=token.confidence)


def _url_to_words(value: str) -> str:
    parsed = urlparse(value if re.match(r"^https?://", value) else f"https://{value}")
    host = parsed.netloc or parsed.path
    host = host.removeprefix("www.")
    path = parsed.path if parsed.netloc else ""
    text = f"{host}{path}".strip("/")

    # Keep URL speech compact and deterministic for common domains.
    text = text.replace("-", " dash ").replace("_", " underscore ")
    text = re.sub(r"[/.]+", " dot ", text)
    return _spaced_identifier(text)


def _email_to_words(value: str) -> str:
    local, _, domain = value.partition("@")
    local_words = _spaced_identifier(local.replace(".", " dot "))
    domain_words = _spaced_identifier(domain.replace(".", " dot "))
    return f"{local_words} at {domain_words}".strip()


def _spaced_identifier(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", " ", value)
    words = []
    for word in re.sub(r"\s+", " ", cleaned).strip().lower().split():
        words.append(KNOWN_TERMS.get(word, word))
    return " ".join(words)
