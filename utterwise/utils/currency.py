from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


AMOUNT_PATTERN = r"\d+(?:,\d{3})*(?:\.\d{1,2})?"


@dataclass(frozen=True, slots=True)
class CurrencySpec:
    code: str
    major_singular: str
    major_plural: str
    minor_singular: str | None = None
    minor_plural: str | None = None
    decimal_mode: str = "minor"


CURRENCY_SPECS: dict[str, CurrencySpec] = {
    "USD": CurrencySpec("USD", "dollar", "dollars", "cent", "cents"),
    "CAD": CurrencySpec("CAD", "Canadian dollar", "Canadian dollars", "cent", "cents"),
    "AUD": CurrencySpec("AUD", "Australian dollar", "Australian dollars", "cent", "cents"),
    "EUR": CurrencySpec("EUR", "euro", "euros", "cent", "cents"),
    "GBP": CurrencySpec("GBP", "pound", "pounds", "penny", "pence"),
    "INR": CurrencySpec("INR", "rupee", "rupees", "paisa", "paise"),
    "JPY": CurrencySpec("JPY", "yen", "yen", decimal_mode="point"),
    "KRW": CurrencySpec("KRW", "won", "won", decimal_mode="point"),
    "RUB": CurrencySpec("RUB", "ruble", "rubles", "kopek", "kopeks"),
    "TRY": CurrencySpec("TRY", "Turkish lira", "Turkish lira", "kurus", "kurus"),
    "NGN": CurrencySpec("NGN", "naira", "naira", "kobo", "kobo"),
    "PHP": CurrencySpec("PHP", "peso", "pesos", "centavo", "centavos"),
    "THB": CurrencySpec("THB", "baht", "baht", "satang", "satang"),
    "VND": CurrencySpec("VND", "dong", "dong", decimal_mode="point"),
    "BRL": CurrencySpec("BRL", "Brazilian real", "Brazilian reais", "centavo", "centavos"),
    "CNY": CurrencySpec("CNY", "yuan", "yuan", decimal_mode="point"),
}


SYMBOL_TO_CODE = {
    "R$": "BRL",
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₹": "INR",
    "¥": "JPY",
    "₩": "KRW",
    "₽": "RUB",
    "₺": "TRY",
    "₦": "NGN",
    "₱": "PHP",
    "฿": "THB",
    "₫": "VND",
}


CODE_ALIASES = {
    "USD": "USD",
    "EUR": "EUR",
    "GBP": "GBP",
    "INR": "INR",
    "JPY": "JPY",
    "KRW": "KRW",
    "RUB": "RUB",
    "TRY": "TRY",
    "NGN": "NGN",
    "PHP": "PHP",
    "THB": "THB",
    "VND": "VND",
    "BRL": "BRL",
    "CNY": "CNY",
    "RMB": "CNY",
    "CAD": "CAD",
    "AUD": "AUD",
}


SYMBOL_PATTERN = "|".join(re.escape(symbol) for symbol in sorted(SYMBOL_TO_CODE, key=len, reverse=True))
CODE_PATTERN = "|".join(sorted(CODE_ALIASES, key=len, reverse=True))

CURRENCY_RE = re.compile(
    rf"""
    (?<!\w)
    (?:
        (?P<symbol>{SYMBOL_PATTERN})\s?(?P<symbol_amount>{AMOUNT_PATTERN})
        |
        (?P<prefix_code>{CODE_PATTERN})\s+(?P<prefix_amount>{AMOUNT_PATTERN})
        |
        (?P<suffix_amount>{AMOUNT_PATTERN})\s+(?P<suffix_code>{CODE_PATTERN})
    )
    (?!\w)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def find_currency_spans(text: str) -> list[tuple[int, int, dict[str, Any]]]:
    spans = []
    for match in CURRENCY_RE.finditer(text):
        metadata = currency_metadata(match.group())
        if metadata:
            spans.append((match.start(), match.end(), metadata))
    return spans


def currency_metadata(value: str) -> dict[str, Any] | None:
    match = CURRENCY_RE.fullmatch(value.strip())
    if not match:
        return None

    raw_code_or_symbol = ""
    amount = ""
    form = ""
    if match.group("symbol"):
        raw_code_or_symbol = match.group("symbol")
        amount = match.group("symbol_amount")
        code = SYMBOL_TO_CODE.get(raw_code_or_symbol)
        form = "symbol"
    elif match.group("prefix_code"):
        raw_code_or_symbol = match.group("prefix_code").upper()
        amount = match.group("prefix_amount")
        code = CODE_ALIASES.get(raw_code_or_symbol)
        form = "code_prefix"
    else:
        raw_code_or_symbol = match.group("suffix_code").upper()
        amount = match.group("suffix_amount")
        code = CODE_ALIASES.get(raw_code_or_symbol)
        form = "code_suffix"

    if not code or code not in CURRENCY_SPECS:
        return None

    spec = CURRENCY_SPECS[code]
    whole, _, fraction = amount.replace(",", "").partition(".")
    return {
        "currency_code": code,
        "currency_display": raw_code_or_symbol,
        "currency_form": form,
        "currency_amount": amount,
        "currency_whole": whole,
        "currency_fraction": fraction,
        "currency_major_singular": spec.major_singular,
        "currency_major_plural": spec.major_plural,
        "currency_minor_singular": spec.minor_singular,
        "currency_minor_plural": spec.minor_plural,
        "currency_decimal_mode": spec.decimal_mode,
    }
