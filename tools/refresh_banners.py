"""Rewrite the generated lock banner in each dated document under Outputs/.

Run after every re-lock:

    python tools/refresh_banners.py

`build_results.py` asserts that each banner matches the current lock and fails
the run if any does not, naming this script. The banner text lives in
`src/banners.py`; the values come from `build_results.current_lock()`, the same
`EXPECTED_*` constants the run asserts. Nothing outside the banner markers is
touched.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build_results  # noqa: E402  (imports only; main() is guarded)
from src.banners import DATED_DOCUMENTS, stale_banners, write_banners  # noqa: E402


def main() -> None:
    lock = build_results.current_lock()
    changed = write_banners(ROOT, lock)
    for rel in DATED_DOCUMENTS:
        print(f"  {rel}: {'rewritten' if rel in changed else 'already current'}")
    remaining = stale_banners(ROOT, lock)
    assert not remaining, remaining
    print(f"{len(changed)} banner(s) rewritten; all {len(DATED_DOCUMENTS)} match the lock")


if __name__ == "__main__":
    main()
