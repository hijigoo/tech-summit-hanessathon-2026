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
            if c and c.lower() not in ("#000000", "#1b1b1b", "#212121"):
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
<meta name="viewport" content="width=device-width,initial-scale=1"/><title>Deck</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
html,body{margin:0;height:100%;font-family:'Noto Sans KR','Poppins',system-ui,sans-serif;overflow:hidden}
body{background:#070a16;background-image:radial-gradient(1200px 600px at 15% -10%,#1b2a6b55,transparent),radial-gradient(900px 500px at 110% 120%,#7b2ff733,transparent)}
#stage{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:2vmin}
#slide{position:relative;container-type:size;overflow:hidden;border-radius:18px;color:#fff;
  box-shadow:0 24px 80px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.06);transition:opacity .35s}
#slide::before{content:"";position:absolute;inset:0;background:var(--bg);z-index:-2}
#slide::after{content:"";position:absolute;inset:0;z-index:-1;
  background:radial-gradient(60cqw 60cqw at 100% 0%,var(--a)55,transparent),radial-gradient(50cqw 50cqw at 0% 100%,var(--b)44,transparent)}
.s{position:absolute;overflow:hidden;display:flex;flex-direction:column;justify-content:center}
.s p{margin:0 0 .25em;font-size:3.4cqh;line-height:1.3;text-shadow:0 2px 12px rgba(0,0,0,.35)}
.s p:first-child:last-child{font-size:5cqh}
.s img{width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 8px 24px rgba(0,0,0,.4));border-radius:10px}
.s table{width:100%;border-collapse:separate;border-spacing:0;font-size:2.6cqh;border-radius:10px;overflow:hidden;backdrop-filter:blur(4px)}
.s td{border:1px solid rgba(255,255,255,.18);padding:.4em .6em;background:rgba(255,255,255,.06)}
.s tr:first-child td{background:rgba(255,255,255,.16);font-weight:700}
.s.vid iframe{width:100%;height:100%;border:0;border-radius:12px}
#bar{position:fixed;left:0;bottom:0;height:5px;background:linear-gradient(90deg,#22d3ee,#7b2ff7,#ff5ea0);transition:width .25s;z-index:5}
#hud{position:fixed;right:16px;bottom:14px;color:#cbd5e1;font-family:Poppins;font-size:13px;letter-spacing:1px;background:rgba(0,0,0,.35);padding:4px 12px;border-radius:20px}
.nav{position:fixed;top:0;bottom:0;width:16%;cursor:pointer;z-index:4}#prev{left:0}#next{right:0}
</style></head><body><div id="stage"><div id="slide"></div></div>
<div id="prev" class="nav"></div><div id="next" class="nav"></div><div id="bar"></div><div id="hud"></div><script>
const D=__DECK__;let i=0;const sl=document.getElementById('slide');
const TH=[['#0f2027','#22d3ee','#2c5364'],['#3a1c71','#ff5ea0','#d76d77'],['#0b486b','#3bb78f','#0f2027'],['#42275a','#ff5ea0','#734b6d'],['#1f1c2c','#22d3ee','#928dab'],['#16222a','#a6ed5d','#3a6073']];
function lay(){const ar=D.aspect||16/9;let w=innerWidth,h=innerHeight,cw=w,ch=w/ar;if(ch>h){ch=h;cw=h*ar}sl.style.width=cw+'px';sl.style.height=ch+'px';}
function show(n){i=Math.max(0,Math.min(D.slides.length-1,n));const t=TH[i%TH.length];sl.style.setProperty('--bg','linear-gradient(135deg,'+t[0]+','+t[2]+')');sl.style.setProperty('--a',t[1]);sl.style.setProperty('--b',t[2]);sl.style.opacity=0;setTimeout(()=>{sl.innerHTML=D.slides[i];sl.style.opacity=1;},120);bar.style.width=((i+1)/D.slides.length*100)+'%';hud.textContent=(i+1)+' / '+D.slides.length;lay();}
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
