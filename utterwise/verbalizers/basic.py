from __future__ import annotations

import re
from urllib.parse import urlparse

from utterwise.math import verbalize_math
from utterwise.policies.base import Policy
from utterwise.tokens import SpokenSegment, Token
from utterwise.verbalizers.numbers import (
    cardinal_to_words,
    decimal_to_words,
    digits_to_words,
    ordinal_to_words,
    year_to_words,
)


SYMBOLS = {
    "&": "and",
    "%": "percent",
    "→": "to",
    "+": "plus",
    "=": "equals",
    "×": "times",
    "÷": "divided by",
}

CURRENCY_UNITS = {
    "$": ("dollar", "dollars", "cent", "cents"),
    "€": ("euro", "euros", "cent", "cents"),
    "£": ("pound", "pounds", "penny", "pence"),
}

MONTH_ALIASES = {
    "jan": "January",
    "january": "January",
    "feb": "February",
    "february": "February",
    "mar": "March",
    "march": "March",
    "apr": "April",
    "april": "April",
    "may": "May",
    "jun": "June",
    "june": "June",
    "jul": "July",
    "july": "July",
    "aug": "August",
    "august": "August",
    "sep": "September",
    "sept": "September",
    "september": "September",
    "oct": "October",
    "october": "October",
    "nov": "November",
    "november": "November",
    "dec": "December",
    "december": "December",
}

MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

KNOWN_TERMS = {
    "openai": "open ai",
}

KNOWN_ACRONYMS = {
    "NASA": "nasa",
}

SKIP_PUNCTUATION = {".", ",", "!", "?", ":", ";", "(", ")", "[", "]", "{", "}", '"'}


def verbalize(tokens: list[Token], policy: Policy) -> list[SpokenSegment]:
    return [_verbalize_one(token, policy) for token in tokens]


def _verbalize_one(token: Token, policy: Policy) -> SpokenSegment:
    if token.type == "MATH":
        speech = verbalize_math(token.value)
        token.confidence = speech.confidence
        token.metadata["matched_rule"] = speech.rule
        token.metadata["parser"] = speech.parser
        token.metadata.update(speech.metadata)
        return _segment(token, speech.text, token)
    if token.type == "DATE":
        return _segment(token, _date_to_words(token.value), token)
    if token.type == "CURRENCY":
        return _segment(token, _currency_to_words(token.value), token)
    if token.type == "TEMPERATURE":
        return _segment(token, _temperature_to_words(token.value), token)
    if token.type == "CARDINAL":
        return _segment(token, cardinal_to_words(token.value), token)
    if token.type == "YEAR":
        return _segment(token, year_to_words(token.value), token)
    if token.type == "ORDINAL":
        return _segment(token, ordinal_to_words(token.value), token)
    if token.type == "VERSION":
        return _segment(token, _version_to_words(token.value), token)
    if token.type == "PHONE":
        return _segment(token, _phone_to_words(token.value), token)
    if token.type == "FLIGHT_NO":
        return _segment(token, _flight_no_to_words(token.value), token)
    if token.type == "PERCENTAGE":
        return _segment(token, _percentage_to_words(token.value), token)
    if token.type == "ACRONYM":
        return _segment(token, _acronym_to_words(token.value), token)
    if token.type == "URL":
        return _segment(token, _url_to_words(token.value), token)
    if token.type == "EMAIL":
        return _segment(token, _email_to_words(token.value), token)
    if token.type == "SYMBOL":
        return _segment(token, SYMBOLS.get(token.value, token.value), token)
    if token.type == "PUNCTUATION" and token.value in SKIP_PUNCTUATION:
        return _segment(token, "", token, fallback_rule="punctuation_skip")
    return _segment(token, token.value, token, fallback_rule="identity")


def _segment(
    token: Token,
    text: str,
    source: Token,
    fallback_rule: str | None = None,
) -> SpokenSegment:
    rule = source.metadata.get("matched_rule", fallback_rule or source.type.lower())
    return SpokenSegment(text=text, source=token, rule=rule, confidence=token.confidence)


def _version_to_words(value: str) -> str:
    normalized = value.lower()
    prefix = ""
    if normalized.startswith("v"):
        prefix = "v "
        normalized = normalized[1:]
    return f"{prefix}{decimal_to_words(normalized)}".strip()


def _phone_to_words(value: str) -> str:
    words = []
    if value.startswith("+"):
        words.append("plus")
    digit_words = digits_to_words(value)
    if digit_words:
        words.append(digit_words)
    return " ".join(words)


def _flight_no_to_words(value: str) -> str:
    if value.isdigit() and len(value) == 3 and value[1:] != "00":
        return f"{cardinal_to_words(value[0])} {cardinal_to_words(value[1:])}"
    return digits_to_words(value)


def _currency_to_words(value: str) -> str:
    match = re.fullmatch(r"\s*([$€£])\s?(\d+(?:,\d{3})*)(?:\.(\d{1,2}))?\s*", value)
    if not match:
        return value

    symbol, whole, cents = match.groups()
    singular, plural, cent_singular, cent_plural = CURRENCY_UNITS[symbol]
    amount = int(whole.replace(",", ""))
    unit = singular if amount == 1 else plural
    words = f"{cardinal_to_words(str(amount))} {unit}"

    if cents is not None and int(cents) > 0:
        cent_value = int(cents.ljust(2, "0"))
        cent_unit = cent_singular if cent_value == 1 else cent_plural
        words = f"{words} and {cardinal_to_words(str(cent_value))} {cent_unit}"
    return words


def _date_to_words(value: str) -> str:
    text = value.strip().replace(",", "")
    if match := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text):
        year, month, day = (int(part) for part in match.groups())
        return _dmy_date_to_words(day, month, year)

    if match := re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text):
        day, month, year = (int(part) for part in match.groups())
        return _dmy_date_to_words(day, month, year)

    if match := re.fullmatch(r"([A-Za-z.]+)\s+(\d{1,2})\s+(\d{4})", text):
        month_text, day, year = match.groups()
        month = MONTH_ALIASES.get(month_text.rstrip(".").lower())
        if month:
            return f"{month} {_day_to_words(int(day))} {year_to_words(year)}"
    return value


def _dmy_date_to_words(day: int, month: int, year: int) -> str:
    month_name = MONTH_NAMES.get(month)
    if not month_name:
        return f"{day}/{month}/{year}"
    return f"{_day_to_words(day)} of {month_name} {year_to_words(str(year))}"


def _day_to_words(day: int) -> str:
    return ordinal_to_words(f"{day}th")


def _temperature_to_words(value: str) -> str:
    match = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*(?:°\s*)?([CF])\s*", value)
    if not match:
        return value

    number, unit = match.groups()
    prefix = ""
    if number.startswith("-"):
        prefix = "minus "
        number = number[1:]

    number_words = decimal_to_words(number) if "." in number else cardinal_to_words(number)
    unit_words = "Celsius" if unit == "C" else "Fahrenheit"
    return f"{prefix}{number_words} degrees {unit_words}"


def _percentage_to_words(value: str) -> str:
    number = value.removesuffix("%")
    words = decimal_to_words(number) if "." in number else cardinal_to_words(number)
    return f"{words} percent"


def _acronym_to_words(value: str) -> str:
    if value in KNOWN_ACRONYMS:
        return KNOWN_ACRONYMS[value]
    return " ".join(value)


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
