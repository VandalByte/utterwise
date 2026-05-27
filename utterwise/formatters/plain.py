from __future__ import annotations

import re

from utterwise.tokens import SpokenSegment


def format_plain(segments: list[SpokenSegment]) -> str:
    text = " ".join(segment.text for segment in segments if segment.text)
    return re.sub(r"\s+", " ", text).strip()
