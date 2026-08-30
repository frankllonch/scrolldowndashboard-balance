"""Build the static site into `docs/`.

    python build.py

Runs the pipeline once, writes the payload the page reads, and copies the
hand-written frontend over. No node, no bundler, no CI.
"""

from __future__ import annotations

import datetime as dt
import json
import shutil
import sys
from pathlib import Path

import numpy as np

from render import theme
from render.page import render
from render.payload import assemble

ROOT = Path(__file__).parent
SITE = ROOT / "site"
DOCS = ROOT / "docs"
VENDOR = DOCS / "vendor"


def coerce(o):
    """pandas hands back numpy scalars and dates; JSON takes neither."""
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, (dt.date, dt.datetime)):
        return o.isoformat()
    raise TypeError(f"not serialisable: {type(o).__name__}")


def vendor_plotly() -> Path:
    """The cartesian build, committed rather than fetched. The page draws bar,
    scatter and heatmap, so the full bundle would ship 2.7 MB of traces it
    never uses: 483 KB over the wire instead of 1,287 KB."""
    src = SITE / "vendor" / "plotly-cartesian.min.js"
    if not src.exists():
        raise SystemExit(f"vendored plotly not found at {src}")
    VENDOR.mkdir(parents=True, exist_ok=True)
    dst = VENDOR / src.name
    shutil.copyfile(src, dst)
    return dst


def copy_frontend() -> list[Path]:
    out = []
    for name in ("style.css", "app.js"):
        src = SITE / name
        if src.exists():
            shutil.copyfile(src, DOCS / name)
            out.append(DOCS / name)
    return out


def main() -> int:
    theme.register_template()
    DOCS.mkdir(exist_ok=True)

    payload, bundles = assemble()
    page = DOCS / "index.html"
    page.write_text(render(payload, bundles))

    target = DOCS / "payload.json"
    target.write_text(json.dumps(payload, separators=(",", ":"),
                                 allow_nan=False, default=coerce))

    written = [page, target, vendor_plotly(), *copy_frontend()]
    for path in written:
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:,.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
