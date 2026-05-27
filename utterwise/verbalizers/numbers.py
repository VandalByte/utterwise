from __future__ import annotations

import re


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


def cardinal_to_words(value: str) -> str:
    normalized = value.replace(",", "")
    if not normalized.isdigit():
        return value

    number = int(normalized)
    if number < 20:
        return ONES[number]
    if number < 100:
        tens, ones = divmod(number, 10)
        words = TENS[tens * 10]
        return f"{words} {ONES[ones]}" if ones else words
    if number < 1000:
        hundreds, remainder = divmod(number, 100)
        words = f"{ONES[hundreds]} hundred"
        return f"{words} {cardinal_to_words(str(remainder))}" if remainder else words
    if number < 1_000_000:
        thousands, remainder = divmod(number, 1000)
        words = f"{cardinal_to_words(str(thousands))} thousand"
        return f"{words} {cardinal_to_words(str(remainder))}" if remainder else words
    return value


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

    if len(fraction) > 1 and fraction.startswith("0"):
        fraction_words = digits_to_words(fraction)
    else:
        fraction_words = cardinal_to_words(fraction)
    return f"{cardinal_to_words(whole)} point {fraction_words}"


def digits_to_words(value: str) -> str:
    return " ".join(ONES[int(digit)] for digit in re.sub(r"\D", "", value))
