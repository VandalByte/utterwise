from __future__ import annotations

from utterwise.tokens import Token


def disambiguate(tokens: list[Token]) -> list[Token]:
    """Compatibility stage for future multi-token context resolution."""

    return tokens
