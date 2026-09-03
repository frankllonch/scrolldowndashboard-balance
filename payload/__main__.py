"""`python -m emit` writes the document."""

from __future__ import annotations

import json
from pathlib import Path

from . import payload

OUT = Path("docs/data.json")


def main() -> None:
    text = json.dumps(payload(), allow_nan=False, separators=(",", ":"))
    OUT.write_text(text)
    print(f"{OUT}  {len(text) / 1024:,.0f} KB")


if __name__ == "__main__":
    main()
