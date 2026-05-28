from __future__ import annotations

from typing import Any

from utterwise.config import NormalizeConfig
from utterwise.normalizers import Normalizer


_NORMALIZER = Normalizer()


def normalize(
    text: str,
    output: str = "plain",
    policy: str = "assistant",
    explain: bool = False,
    config: NormalizeConfig | None = None,
    **config_overrides: Any,
) -> str | dict[str, Any]:
    """Normalize text into a speech-friendly string or SSML document.

    Args:
        text: Raw input text to normalize.
        output: Output format. Use ``"plain"`` for spoken text or ``"ssml"``
            for a minimal ``<speak>`` document.
        policy: Speaking style policy. ``"assistant"`` is the default.
        explain: When true, return a trace dictionary instead of only the
            rendered output.

    Returns:
        A normalized string by default. If ``explain`` is true, returns a
        dictionary containing the cleaned text, rendered output, detection
        flags, token classifications, rule names, confidence scores, and
        source spans.
    """

    result = _NORMALIZER.normalize(
        text,
        output=output,
        policy=policy,
        config=config,
        **config_overrides,
    )
    return result.explain() if explain else result.output


def normalize_ssml(
    text: str,
    policy: str = "assistant",
    config: NormalizeConfig | None = None,
    **config_overrides: Any,
) -> str:
    """Normalize text and wrap the result in a minimal SSML ``<speak>`` tag.

    Args:
        text: Raw input text to normalize.
        policy: Speaking style policy. ``"assistant"`` is the default.

    Returns:
        A valid XML string such as ``"<speak>hello at example dot com</speak>"``.
    """

    return _NORMALIZER.normalize(
        text,
        output="ssml",
        policy=policy,
        config=config,
        **config_overrides,
    ).output


def explain(
    text: str,
    policy: str = "assistant",
    config: NormalizeConfig | None = None,
    **config_overrides: Any,
) -> dict[str, Any]:
    """Return a token-level trace for how Utterwise normalized the text.

    Args:
        text: Raw input text to inspect.
        policy: Speaking style policy. ``"assistant"`` is the default.

    Returns:
        A dictionary with the final output plus per-token details including
        semantic type, spoken form, rule name, confidence, source span,
        candidates, and metadata.
    """

    return _NORMALIZER.normalize(
        text,
        output="plain",
        policy=policy,
        config=config,
        **config_overrides,
    ).explain()


def explain_pretty(
    text: str,
    policy: str = "assistant",
    config: NormalizeConfig | None = None,
    **config_overrides: Any,
) -> str:
    """Return a compact table showing token-level normalization decisions."""

    trace = explain(text, policy=policy, config=config, **config_overrides)
    rows = [("raw", "type", "spoken", "rule", "conf")]
    for token in trace["tokens"]:
        rows.append(
            (
                str(token["value"]),
                str(token["type"]),
                str(token["spoken"]),
                str(token["rule"]),
                f"{float(token['confidence']):.2f}",
            )
        )

    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]
    lines = []
    for row_index, row in enumerate(rows):
        line = "  ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        lines.append(line.rstrip())
        if row_index == 0:
            lines.append("  ".join("-" * width for width in widths))
    return "\n".join(lines)
