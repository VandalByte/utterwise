from __future__ import annotations

import re


MAX_CARDINAL = 999_999_999_999

ONES = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
}

TENS = {
    20: "twenty",
    30: "thirty",
    40: "forty",
    50: "fifty",
    60: "sixty",
    70: "seventy",
    80: "eighty",
    90: "ninety",
}

ORDINAL_ONES = {
    0: "zeroth",
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    11: "eleventh",
    12: "twelfth",
    13: "thirteenth",
    14: "fourteenth",
    15: "fifteenth",
    16: "sixteenth",
    17: "seventeenth",
    18: "eighteenth",
    19: "nineteenth",
}

ORDINAL_TENS = {
    20: "twentieth",
    30: "thirtieth",
    40: "fortieth",
    50: "fiftieth",
    60: "sixtieth",
    70: "seventieth",
    80: "eightieth",
    90: "ninetieth",
}

SCALES = (
    (1_000_000_000, "billion"),
    (1_000_000, "million"),
    (1_000, "thousand"),
)


def cardinal_to_words(value: str) -> str:
    normalized = value.replace(",", "")
    if "." in normalized:
        return decimal_to_words(normalized)
    if not normalized.isdigit():
        return value
    if _should_spell_digits(normalized):
        return digits_to_words(normalized)

    number = int(normalized)
    if number > MAX_CARDINAL:
        return digits_to_words(normalized)
    return _int_to_words(number)


def is_above_supported_cardinal(value: str) -> bool:
    normalized = value.replace(",", "")
    return normalized.isdigit() and int(normalized) > MAX_CARDINAL


def year_to_words(value: str) -> str:
    if not value.isdigit() or len(value) != 4:
        return cardinal_to_words(value)

    number = int(value)
    if 2000 <= number <= 2009:
        return f"two thousand {ONES[number - 2000]}" if number != 2000 else "two thousand"
    if 2010 <= number <= 2099:
        return f"twenty {cardinal_to_words(value[2:])}"

    first = int(value[:2])
    second = int(value[2:])
    if second == 0:
        return f"{cardinal_to_words(str(first))} hundred"
    return f"{cardinal_to_words(str(first))} {cardinal_to_words(str(second))}"


def ordinal_to_words(value: str) -> str:
    digits = re.sub(r"(st|nd|rd|th)$", "", value.lower())
    if not digits.isdigit():
        return value

    number = int(digits)
    if number < 20:
        return ORDINAL_ONES[number]
    if number < 100:
        tens, ones = divmod(number, 10)
        if ones == 0:
            return ORDINAL_TENS[tens * 10]
        return f"{TENS[tens * 10]} {ORDINAL_ONES[ones]}"

    base, remainder = divmod(number, 100)
    if remainder == 0:
        return f"{cardinal_to_words(str(base))} hundredth"
    return f"{cardinal_to_words(str(number - remainder))} {ordinal_to_words(str(remainder) + 'th')}"


def decimal_to_words(value: str) -> str:
    whole, _, fraction = value.partition(".")
    if not fraction:
        return cardinal_to_words(whole)
    return f"{cardinal_to_words(whole)} point {digits_to_words(fraction)}"


def digits_to_words(value: str) -> str:
    return " ".join(ONES[int(digit)] for digit in re.sub(r"\D", "", value))


def _int_to_words(number: int) -> str:
    if number < 20:
        return ONES[number]
    if number < 100:
        tens, ones = divmod(number, 10)
        words = TENS[tens * 10]
        return f"{words} {ONES[ones]}" if ones else words
    if number < 1000:
        hundreds, remainder = divmod(number, 100)
        words = f"{ONES[hundreds]} hundred"
        return f"{words} {_int_to_words(remainder)}" if remainder else words

    for scale, scale_name in SCALES:
        if number >= scale:
            quotient, remainder = divmod(number, scale)
            words = f"{_int_to_words(quotient)} {scale_name}"
            return f"{words} {_int_to_words(remainder)}" if remainder else words
    return str(number)


def _should_spell_digits(value: str) -> bool:
    return len(value) > 1 and value.startswith("0")
