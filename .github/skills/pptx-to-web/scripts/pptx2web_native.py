#!/usr/bin/env python3
"""pptx2web_native — rebuild a .pptx as a real HTML deck (content, not screenshots).

Extracts text runs (font, size, color, bold/italic, align), pictures, tables and
embedded/online videos from each slide and lays them out as absolutely-positioned
HTML/CSS so text stays selectable and the layout adapts to the web. Emits docs/.

Usage: python3 pptx2web_native.py <input.pptx> [--out docs]
"""
import argparse, html, json, os, re, shutil, sys, zipfile
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Emu

PTW, PTH = 960.0, 540.0  # 16:9 slide in points


def pct(v, total):
    return round((v or 0) / total * 100, 3)


def color_of(font):
    try:
        if font.color and font.color.type is not None and font.color.rgb is not None:
            return "#" + str(font.color.rgb)
    except Exception:
        pass
    return None


def align_of(p):
    a = p.alignment
    return {1: "left", 2: "center", 3: "right", 4: "justify"}.get(int(a), "left") if a else "left"


def text_html(tf):
    out = []
    for p in tf.paragraphs:
        runs = []
        for r in p.runs:
            sz = r.font.size.pt if r.font.size else None
            st = f"font-size:{sz/PTH*100:.2f}cqh;" if sz else ""
            if r.font.bold:
                st += "font-weight:700;"
            if r.font.italic:
                st += "font-style:italic;"
            c = color_of(r.font)
            if c:
                st += f"color:{c};"
            runs.append(f'<span style="{st}">{html.escape(r.text)}</span>')
        if not runs:
            runs.append("<br>")
        lvl = "margin-left:%dem;" % (p.level * 1) if p.level else ""
        out.append(f'<p style="text-align:{align_of(p)};{lvl}">{"".join(runs)}</p>')
    return "".join(out)


def shape_div(sh, W, H, media):
    st = (f"left:{pct(sh.left,W)}%;top:{pct(sh.top,H)}%;"
          f"width:{pct(sh.width,W)}%;height:{pct(sh.height,H)}%;")
    if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
        try:
            img = sh.image
            name = f"img_{img.sha1[:10]}.{img.ext}"
            (media/name).write_bytes(img.blob)
            return f'<div class="s" style="{st}"><img src="media/{name}"/></div>'
        except Exception:
            return ""
    if sh.has_table:
        rows = []
        for row in sh.table.rows:
            cells = "".join(f"<td>{html.escape(c.text)}</td>" for c in row.cells)
            rows.append(f"<tr>{cells}</tr>")
        return f'<div class="s" style="{st}"><table>{"".join(rows)}</table></div>'
    if sh.has_text_frame and sh.text_frame.text.strip():
        return f'<div class="s" style="{st}">{text_html(sh.text_frame)}</div>'
    return ""


def online_videos(pptx):
    out = {}
    with zipfile.ZipFile(pptx) as z:
        for nm in z.namelist():
            m = re.match(r"ppt/slides/_rels/slide(\d+)\.xml\.rels", nm)
            if not m:
                continue
            d = z.read(nm).decode("utf8", "ignore")
            urls = [u.replace("&amp;", "&") for u in re.findall(r'Target="([^"]+)"[^>]*External', d) if u.startswith("http")]
            urls = [u for u in urls if any(k in u for k in ("youtube", "youtu.be", "vimeo", "embed"))]
            if urls:
                out[int(m.group(1))-1] = urls
    return out


def build(pptx, out):
    out = Path(out)
    media = out/"media"
    for d in (out, media):
        d.mkdir(parents=True, exist_ok=True)
    for f in media.glob("*"):
        f.unlink()
    p = Presentation(pptx)
    W, H = p.slide_width, p.slide_height
    onv = online_videos(pptx)
    slides = []
    for i, s in enumerate(p.slides):
        parts = [shape_div(sh, W, H, media) for sh in s.shapes]
        for u in onv.get(i, []):
            parts.append(f'<div class="s vid" style="left:0;top:0;width:100%;height:100%;"><iframe src="{html.escape(u)}" allow="autoplay;encrypted-media" allowfullscreen></iframe></div>')
        slides.append("".join(x for x in parts if x))
    deck = {"title": Path(pptx).stem, "aspect": W/H, "slides": slides}
    (out/"deck.json").write_text(json.dumps(deck, ensure_ascii=False))
    (out/"index.html").write_text(HTML.replace("__DECK__", json.dumps(deck, ensure_ascii=False)))
    return len(slides), len(onv)


HTML = r"""<!doctype html><html lang="ko"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/><title>Deck</title><style>
*{box-sizing:border-box}html,body{margin:0;height:100%;background:#0b0e14;font-family:'Segoe UI',system-ui,'Malgun Gothic',sans-serif;color:#1b1b1b}
#stage{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
#slide{position:relative;background:#fff;container-type:size;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,.5)}
.s{position:absolute;overflow:hidden}.s p{margin:0;font-size:3.2cqh;line-height:1.25}
.s img{width:100%;height:100%;object-fit:contain}
.s table{width:100%;height:100%;border-collapse:collapse;font-size:2.6cqh}.s td{border:1px solid #ccc;padding:.3em}
.s.vid iframe{width:100%;height:100%;border:0}
#bar{position:fixed;left:0;bottom:0;height:4px;background:#0078D4}#hud{position:fixed;right:12px;bottom:12px;color:#aaa;font-size:13px}
.nav{position:fixed;top:0;bottom:0;width:16%;cursor:pointer}#prev{left:0}#next{right:0}
</style></head><body><div id="stage"><div id="slide"></div></div>
<div id="prev" class="nav"></div><div id="next" class="nav"></div><div id="bar"></div><div id="hud"></div><script>
const D=__DECK__;let i=0;const sl=document.getElementById('slide');
function lay(){const ar=D.aspect||16/9;let w=innerWidth,h=innerHeight,cw=w,ch=w/ar;if(ch>h){ch=h;cw=h*ar}sl.style.width=cw+'px';sl.style.height=ch+'px';}
function show(n){i=Math.max(0,Math.min(D.slides.length-1,n));sl.innerHTML=D.slides[i];document.getElementById('bar').style.width=((i+1)/D.slides.length*100)+'%';document.getElementById('hud').textContent=(i+1)+' / '+D.slides.length;lay();}
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key))show(i+1);if(['ArrowLeft','PageUp'].includes(e.key))show(i-1);if(e.key=='f')document.documentElement.requestFullscreen();});
next.onclick=()=>show(i+1);prev.onclick=()=>show(i-1);addEventListener('resize',lay);document.title=D.title;show(0);
</script></body></html>"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx"); ap.add_argument("--out", default="docs")
    a = ap.parse_args()
    if not os.path.exists(a.pptx):
        sys.exit(f"Input not found: {a.pptx}")
    n, v = build(a.pptx, a.out)
    print(f"OK: {n} slides, {v} online videos -> {a.out}/")
