from __future__ import annotations

from utterwise.detectors.basic import DetectionFlags
from utterwise.tokens import Token


def classify(tokens: list[Token], flags: DetectionFlags) -> list[Token]:
    for index, token in enumerate(tokens):
        token.context = _context_for(tokens, index)

        if (
            flags.year
            and token.type == "CARDINAL"
            and _is_four_digit_number(token.value)
        ):
            # Four-digit numbers are intentionally left ambiguous for the disambiguator.
            token.candidates = [("YEAR", 0.72), ("CARDINAL", 0.58)]
            token.confidence = 0.72
        elif token.type in {"URL", "EMAIL"}:
            token.confidence = 0.98
        elif token.type == "SYMBOL":
            token.confidence = 0.95
        elif token.type == "PUNCTUATION":
            token.confidence = 0.7
    return tokens


def _is_four_digit_number(value: str) -> bool:
    return value.isdigit() and len(value) == 4


def _context_for(tokens: list[Token], index: int) -> dict[str, list[str]]:
    previous_tokens = tokens[max(0, index - 3) : index]
    next_tokens = tokens[index + 1 : index + 4]
    return {
        "previous_words": [
            token.value.lower() for token in previous_tokens if token.type == "WORD"
        ],
        "next_words": [
            token.value.lower() for token in next_tokens if token.type == "WORD"
        ],
    }
