from __future__ import annotations

from typing import Any


def try_parse_sympy(value: str) -> tuple[Any | None, str | None]:
    try:
        from sympy.parsing.sympy_parser import parse_expr
    except ImportError:
        return None, "sympy is not installed"

    try:
        return parse_expr(value.replace("^", "**"), evaluate=False), None
    except Exception as exc:  # pragma: no cover - exact parser errors vary by SymPy version.
        return None, str(exc)
