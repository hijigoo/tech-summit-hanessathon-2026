#!/usr/bin/env python3
"""Step 1 of the screenshot->note->html pipeline.
Render every slide of a .pptx to PNG so the agent can VIEW each slide and
reinterpret it into content.json. Uses soffice (PDF) + PyMuPDF (raster)."""
import argparse, os, subprocess, sys, glob
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--out", default="/tmp/shots")
    ap.add_argument("--dpi", type=int, default=110)
    a = ap.parse_args()
    if not os.path.exists(a.pptx):
        sys.exit(f"not found: {a.pptx}")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/_p2w_pdf"); tmp.mkdir(exist_ok=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf",
                    a.pptx, "--outdir", str(tmp)], check=True)
    pdf = sorted(tmp.glob("*.pdf"), key=os.path.getmtime)[-1]
    import fitz
    d = fitz.open(pdf)
    for i, p in enumerate(d):
        p.get_pixmap(dpi=a.dpi).save(str(out / f"s{i+1:02d}.png"))
    print(f"OK: {len(d)} PNGs -> {out}/  (view each, then write content.json)")


if __name__ == "__main__":
    main()
