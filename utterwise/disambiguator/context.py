from __future__ import annotations

from utterwise.tokens import Token


YEAR_HINTS = {
    "in",
    "since",
    "during",
    "before",
    "after",
    "by",
    "from",
    "until",
    "year",
    "born",
    "founded",
}


def disambiguate(tokens: list[Token]) -> list[Token]:
    for token in tokens:
        if not token.candidates or not token.value.isdigit() or len(token.value) != 4:
            continue

        value = int(token.value)
        previous_words = set(token.context.get("previous_words", []))
        next_words = set(token.context.get("next_words", []))
        has_date_context = bool((previous_words | next_words) & YEAR_HINTS)

        # A broad modern-history range keeps year handling useful while avoiding IDs like 0007.
        if 1000 <= value <= 2099 and has_date_context:
            token.type = "YEAR"
            token.confidence = 0.92
            token.metadata["disambiguation"] = "context_year_hint"
        elif 1900 <= value <= 2099:
            token.type = "YEAR"
            token.confidence = 0.78
            token.metadata["disambiguation"] = "plausible_year_range"
        else:
            token.type = "CARDINAL"
            token.confidence = 0.82
            token.metadata["disambiguation"] = "default_cardinal"
    return tokens
