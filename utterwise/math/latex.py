from __future__ import annotations

import re


def optional_latex_text(value: str) -> str | None:
    try:
        from pylatexenc.latex2text import LatexNodes2Text
    except ImportError:
        return None

    return LatexNodes2Text().latex_to_text(value)


def match_frac(value: str) -> re.Match[str] | None:
    return re.fullmatch(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", value.strip())


def match_sqrt(value: str) -> re.Match[str] | None:
    return re.fullmatch(r"\\sqrt\{([^{}]+)\}", value.strip())


def match_sum(value: str) -> re.Match[str] | None:
    return re.fullmatch(r"\\sum_\{([^{}]+)\}\^\{([^{}]+)\}\s*(.+)", value.strip())
