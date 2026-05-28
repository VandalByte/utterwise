from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utterwise import explain, explain_pretty, normalize  # noqa: E402

# Test sample text:
# Born in 1998, the value is 1998, call 911 immediately, Flight 911 departs at 6, Python 3.12 supports v3.12, NASA and HTTP, 21st place, 12.5%, 25°C, 98.6°F, $12.50, €45, £9.99, Jan 3, 2026, 03/04/2026, x^2, a/b, (x+1)^2, \frac{a+b}{c}, E = mc^4, \sqrt{x+1}, \sum_{i=1}^{n} i, and x_1, x_2, \ldots; email hello@example.com or visit https://openai.com.

def main() -> None:
    while True:
        print("\nUtterwise test menu")
        print("1. Run all pytest tests")
        print("2. Run golden tests only")
        print("3. Normalize custom input")
        print("4. Show explain output")
        print("5. Show pretty explain output")
        print("6. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            run_pytest(["-vv"])
        elif choice == "2":
            run_pytest(["tests/unit/test_golden.py", "-vv"])
        elif choice == "3":
            text = input("Text: ")
            print("\nOutput:\n", normalize(text))
        elif choice == "4":
            text = input("Text: ")
            print("\nOutput:\n", json.dumps(explain(text), indent=2))
        elif choice == "5":
            text = input("Text: ")
            print("\nOutput:\n", explain_pretty(text))
        elif choice == "6":
            return
        else:
            print("Unknown choice.")


def run_pytest(args: list[str]) -> None:
    command = [sys.executable, "-m", "pytest", *args]
    subprocess.run(command, cwd=ROOT, check=False)


if __name__ == "__main__":
    main()
