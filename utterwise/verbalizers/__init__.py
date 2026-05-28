from __future__ import annotations

from utterwise.policies.base import Policy
from utterwise.tokens import SpokenSegment, Token


def verbalize(tokens: list[Token], policy: Policy) -> list[SpokenSegment]:
    from utterwise.verbalizers.basic import verbalize as _verbalize

    return _verbalize(tokens, policy)


__all__ = ["verbalize"]
