from __future__ import annotations

from html import escape

from utterwise.formatters.plain import format_plain
from utterwise.tokens import SpokenSegment


def format_ssml(segments: list[SpokenSegment]) -> str:
    return f"<speak>{escape(format_plain(segments))}</speak>"
