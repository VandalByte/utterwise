from __future__ import annotations

import re


LATEX_COMMAND_RE = re.compile(r"\\[A-Za-z]+\b")
MATH_SIGNAL_RE = re.compile(
    r"""
    \\[A-Za-z]+\b
    |[A-Za-z0-9]+\^[A-Za-z0-9]+
    |[A-Za-z]+_\d+
    |\([A-Za-z0-9+\-*/\s]+\)\^\d+
    |[A-Za-z0-9]+\s*/\s*[A-Za-z0-9]+
    |[A-Za-z]\s*=\s*[A-Za-z0-9^+\-*/()]+
    """,
    re.VERBOSE,
)

INLINE_MATH_RE = re.compile(
    r"""
    \\frac\{[^{}]+\}\{[^{}]+\}
    |\\sqrt\{[^{}]+\}
    |\\sum_\{[^{}]+\}\^\{[^{}]+\}\s*[A-Za-z0-9_]+
    |\\[A-Za-z]+(?:\{[^{}]*\})?
    |[A-Za-z]+_\d+(?:\s*,\s*[A-Za-z]+_\d+)*(?:\s*,\s*\\(?:ldots|cdots))?
    |\([A-Za-z0-9+\-*/\s]+\)\^\d+
    |[A-Za-z]\s*=\s*[A-Za-z0-9^+\-*/()]+
    |[A-Za-z0-9]+\^[A-Za-z0-9]+
    |[A-Za-z0-9]+\s*/\s*[A-Za-z0-9]+
    """,
    re.VERBOSE,
)


def has_math(text: str) -> bool:
    return bool(MATH_SIGNAL_RE.search(text))


def find_math_spans(text: str) -> list[tuple[int, int]]:
    spans = [(match.start(), match.end()) for match in INLINE_MATH_RE.finditer(text)]
    return _merge_overlapping(spans)


def _merge_overlapping(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []

    merged = [spans[0]]
    for start, end in spans[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged
