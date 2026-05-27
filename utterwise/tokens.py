from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Candidate:
    """A possible semantic classification considered by the rule engine."""

    type: str
    confidence: float
    rule: str
    reason: str


@dataclass(slots=True)
class Token:
    """A source-aligned unit that moves through every normalization stage."""

    type: str
    value: str
    start: int
    end: int
    confidence: float = 1.0
    candidates: list[Candidate] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SpokenSegment:
    """A verbalized token plus trace data for explain mode."""

    text: str
    source: Token
    rule: str
    confidence: float
