from __future__ import annotations

import argparse
import json

from utterwise.api import explain, explain_pretty, normalize, normalize_ssml
from utterwise.config import NormalizeConfig


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="utterwise", description="Normalize text for speech.")
    parser.add_argument("text", help="Text to normalize.")
    parser.add_argument("--ssml", action="store_true", help="Render a minimal SSML document.")
    parser.add_argument("--explain", action="store_true", help="Print JSON explain output.")
    parser.add_argument("--pretty", action="store_true", help="Print a compact explain table.")
    parser.add_argument("--no-math", action="store_true", help="Disable math expression normalization.")
    parser.add_argument("--no-currency", action="store_true", help="Disable currency normalization.")
    parser.add_argument("--no-dates", action="store_true", help="Disable date normalization.")
    parser.add_argument("--no-temperature", action="store_true", help="Disable temperature normalization.")
    args = parser.parse_args(argv)

    config = NormalizeConfig(
        enable_math=not args.no_math,
        enable_currency=not args.no_currency,
        enable_dates=not args.no_dates,
        enable_temperature=not args.no_temperature,
    )

    if args.pretty:
        print(explain_pretty(args.text, config=config))
    elif args.explain:
        print(json.dumps(explain(args.text, config=config), indent=2))
    elif args.ssml:
        print(normalize_ssml(args.text, config=config))
    else:
        print(normalize(args.text, config=config))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
