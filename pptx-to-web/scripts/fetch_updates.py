#!/usr/bin/env python3
"""fetch_updates — pull latest Microsoft Foundry / Azure updates from the official
docs site and write updates.json (category -> bullet list). pptx2web_native.py
can append these as "최신 업데이트" slides so a deck stays current.

Usage: python3 fetch_updates.py [--url <whats-new url>] [--out updates.json] [--per 6]
"""
import argparse, json, re, urllib.request
from datetime import date

DEFAULT_URL = "https://raw.githubusercontent.com/MicrosoftDocs/azure-ai-docs/main/articles/foundry/whats-new-foundry.md"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf8", "ignore")


def parse(md):
    """Group bullet titles under '## New articles' / 'Updated articles' by category."""
    cats, cat, sec = {}, None, None
    for ln in md.splitlines():
        if ln.startswith("## "):
            sec, cat = ln[3:].strip(), None
            continue
        m = re.search(r"\[([^\]]+)\]", ln)
        if re.match(r"^\s*-\s", ln) and not m:                 # category bullet, no link
            cat = ln.strip("- ").strip(); cats.setdefault((sec, cat), [])
        elif m and sec and cat:                                # item bullet with link
            cats[(sec, cat)].append(m.group(1))
    return cats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL); ap.add_argument("--out", default="updates.json")
    ap.add_argument("--per", type=int, default=7)
    a = ap.parse_args()
    cats = parse(fetch(a.url))
    slides = []
    for (sec, cat), items in cats.items():
        if sec and "New" in sec and items:
            slides.append({"category": cat, "items": items[:a.per]})
    out = {"source": a.url, "fetched": str(date.today()), "groups": slides}
    open(a.out, "w").write(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"OK: {len(slides)} update groups from {a.url} -> {a.out}")


if __name__ == "__main__":
    main()
