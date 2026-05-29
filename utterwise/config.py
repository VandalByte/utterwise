from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


DEFAULT_POLICY = "assistant"
DEFAULT_OUTPUT = "plain"


@dataclass(frozen=True, slots=True)
class NormalizeConfig:
    enable_math: bool = True
    enable_currency: bool = True
    enable_dates: bool = True
    enable_temperature: bool = True
    date_format: str = "DMY"


def resolve_config(
    config: NormalizeConfig | None = None,
    **overrides: Any,
) -> NormalizeConfig:
    active = config or NormalizeConfig()
    clean_overrides = {key: value for key, value in overrides.items() if value is not None}
    return replace(active, **clean_overrides) if clean_overrides else active
