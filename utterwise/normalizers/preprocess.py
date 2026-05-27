from __future__ import annotations

import re


MARKDOWN_RE = re.compile(r"(\*\*|__|\*|_|`|~~)")


def has_markdown(text: str) -> bool:
    return bool(re.search(r"(^|\n)\s{0,3}(#{1,6}\s+|>\s*)|(\*\*|__|`|~~)", text))


def preprocess(text: str) -> str:
    """Strip lightweight Markdown markers and normalize whitespace."""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"(?m)^\s{0,3}>\s?", "", normalized)
    normalized = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", normalized)
    normalized = MARKDOWN_RE.sub("", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()
