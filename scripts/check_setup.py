"""Command-line wrapper for pi-basics runtime checks."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pi_basics import configure_python_runtime


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the local pi-basics Python setup."
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress setup details and only print a final status line.",
    )
    args = parser.parse_args()

    result = configure_python_runtime(start_path=PROJECT_ROOT, verbose=not args.quiet)

    if result.missing_packages:
        print("Setup check failed: missing core dependencies.")
        return 1

    print("Setup check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
