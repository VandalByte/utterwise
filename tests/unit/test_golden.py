from __future__ import annotations

import json
from pathlib import Path

import pytest

from utterwise import normalize


GOLDEN_DIR = Path(__file__).resolve().parents[1] / "golden"


def load_cases() -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    for path in sorted(GOLDEN_DIR.glob("*.json")):
        cases.extend(json.loads(path.read_text(encoding="utf-8")))
    return cases


@pytest.mark.parametrize("case", load_cases(), ids=lambda case: case["name"])
def test_golden_plain_outputs(case: dict[str, str]) -> None:
    assert normalize(case["input"]) == case["plain"]
