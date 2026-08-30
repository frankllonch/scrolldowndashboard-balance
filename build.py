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
import plotly

from render import theme
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
    """Copy plotly.min.js out of the installed package. Pinning the file we
    tested against beats trusting a CDN to still be there."""
    src = Path(plotly.__file__).parent / "package_data" / "plotly.min.js"
    if not src.exists():
        raise SystemExit(f"plotly.min.js not found at {src}")
    VENDOR.mkdir(parents=True, exist_ok=True)
    dst = VENDOR / "plotly.min.js"
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
    target = DOCS / "payload.json"
    target.write_text(json.dumps(payload, separators=(",", ":"),
                                 default=coerce))

    written = [target, vendor_plotly(), *copy_frontend()]
    for path in written:
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:,.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
