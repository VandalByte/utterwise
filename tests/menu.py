from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utterwise import explain, normalize  # noqa: E402

# Test sample text:
# In the year **2026**, our user support team (contact@example.com) found that 15% of traffic went to https://example.com!

def main() -> None:
    while True:
        print("\nUtterwise test menu")
        print("1. Run all pytest tests")
        print("2. Run golden tests only")
        print("3. Normalize custom input")
        print("4. Show explain output")
        print("5. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            run_pytest(["-vv"])
        elif choice == "2":
            run_pytest(["tests/unit/test_golden.py", "-vv"])
        elif choice == "3":
            text = input("Text: ")
            print(normalize(text))
        elif choice == "4":
            text = input("Text: ")
            print(json.dumps(explain(text), indent=2))
        elif choice == "5":
            return
        else:
            print("Unknown choice.")


def run_pytest(args: list[str]) -> None:
    command = [sys.executable, "-m", "pytest", *args]
    subprocess.run(command, cwd=ROOT, check=False)


if __name__ == "__main__":
    main()
