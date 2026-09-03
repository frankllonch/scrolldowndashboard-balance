"""Build the static site into `docs/`.

    python build.py

Two halves, one command. Python turns the event logs into one typed JSON
document; the TypeScript in `web/` turns that into the page — every section
rendered at build time, so what ships reads without script.

    python -m emit          data/*.json  →  docs/data.json
    npm run typecheck       the document against web/types/
    prerender               docs/data.json + site/index.html  →  docs/index.html
    npm run bundle          web/main.ts  →  docs/app.js
                            site/css/*   →  docs/style.css
                            vendored plotly, copied

Node is required. `npm install` once, then this.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "site"
DOCS = ROOT / "docs"
CACHE = ROOT / "node_modules" / ".cache"


def run(*command: str) -> str:
    """A build step. Its output is the build's output, failure and all."""
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if done.returncode:
        sys.stderr.write(done.stdout + done.stderr)
        raise SystemExit(f"{command[0]} failed: {' '.join(command)}")
    return done.stdout


def emit() -> Path:
    """The document. Everything the page is given, and nothing else."""
    run(sys.executable, "-m", "emit")
    return DOCS / "data.json"


def typecheck() -> None:
    """The contract, compiled. A field the page reads and `emit` no longer
    sends fails here rather than at a blank chart."""
    run("npm", "run", "--silent", "typecheck")


def prerender() -> Path:
    """The page, with every section already in it."""
    run("npm", "run", "--silent", "prerender")
    html = run("node", str(CACHE / "prerender.cjs"), str(SITE / "index.html"))
    page = DOCS / "index.html"
    page.write_text(html)
    return page


def bundle() -> Path:
    """The one script the page loads."""
    run("npm", "run", "--silent", "bundle")
    return DOCS / "app.js"


def stylesheet() -> Path:
    """One stylesheet out of many. The sections exist so the source is
    readable; the page still gets one file and one request."""
    parts = sorted((SITE / "css").glob("*.css"))
    css = DOCS / "style.css"
    css.write_text("\n".join(p.read_text().rstrip("\n") for p in parts) + "\n")
    return css


def vendor_plotly() -> Path:
    """The cartesian build, committed rather than fetched. The page draws bar,
    scatter and heatmap, so the full bundle would ship 2.7 MB of traces it
    never uses."""
    src = SITE / "vendor" / "plotly-cartesian.min.js"
    if not src.exists():
        raise SystemExit(f"vendored plotly not found at {src}")
    (DOCS / "vendor").mkdir(parents=True, exist_ok=True)
    dst = DOCS / "vendor" / src.name
    shutil.copyfile(src, dst)
    return dst


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    data = emit()
    typecheck()
    written = [data, prerender(), bundle(), stylesheet(), vendor_plotly()]
    for path in written:
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:,.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
