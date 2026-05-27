from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Policy:
    name: str = "assistant"


SUPPORTED_POLICIES = {
    "assistant": Policy("assistant"),
    "edu": Policy("edu"),
    "accessibility": Policy("accessibility"),
}


def get_policy(name: str = "assistant") -> Policy:
    try:
        return SUPPORTED_POLICIES[name]
    except KeyError as exc:
        supported = ", ".join(sorted(SUPPORTED_POLICIES))
        raise ValueError(f"Unknown policy '{name}'. Supported policies: {supported}.") from exc
