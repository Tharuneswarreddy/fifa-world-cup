"""Download the martj42 international-results dataset (CC0) used for ingestion.

Usage (from repo root, or anywhere):
    python scripts/download_data.py

Downloads into data/raw/martj42/. Safe to re-run (overwrites). No dependencies
beyond the standard library.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/martj42/international_results/master"
FILES = ["results.csv", "shootouts.csv", "goalscorers.csv", "former_names.csv"]

REPO_ROOT = Path(__file__).resolve().parents[1]
DEST = REPO_ROOT / "data" / "raw" / "martj42"


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    print(f"Downloading martj42 dataset (CC0) into {DEST}")
    for name in FILES:
        url = f"{BASE}/{name}"
        target = DEST / name
        try:
            urllib.request.urlretrieve(url, target)  # noqa: S310 (trusted GitHub host)
            size_kb = target.stat().st_size / 1024
            print(f"  OK  {name}  ({size_kb:,.0f} KB)")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {name}: {exc}")
            return 1
    print("Done. Next: python -m app.ingestion.cli import-history")
    return 0


if __name__ == "__main__":
    sys.exit(main())
