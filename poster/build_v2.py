#!/usr/bin/env python3
import math
import os

import build_art as ba
from build_art import (T50, T100, T200, T300, T400, T500, T600, T700, T800, T900, INK, INK2, LINE, RED, GREEN,
                       text, icon, chip, tracks, Route, window, doc, defs, wrap_map, inject, built_html, header_art)

HERE = ba.HERE
OUT = os.path.join(HERE, "poster_v2.html")
OUT_PLAIN = os.path.join(HERE, "poster_v2_no_credits.html")

ba.SYMBOLS.update({
    "grid": '<rect x="3" y="3" width="8" height="10" rx="1.8"/><rect x="13" y="3" width="8" height="6" rx="1.8"/><rect x="13" y="11" width="8" height="10" rx="1.8"/><rect x="3" y="15" width="8" height="6" rx="1.8"/>',
    "layers": '<path d="M12 2.5l9.5 5.5-9.5 5.5L2.5 8z"/><path d="M2.5 12.5L12 18l9.5-5.5M2.5 16.5L12 22l9.5-5.5"/>',
})

CSS = """
  /* ===== v2: dark hero, goals strip, three-panel flow, statement band ===== */
  .hero2 { position: relative; overflow: hidden; color: #fff; padding: 62px 100px 118px; display: grid; grid-template-columns: 1fr 930px; gap: 20px; align-items: center;
    background: radial-gradient(1100px 760px at 78% 40%, rgba(45,212,191,.38), transparent 62%), radial-gradient(900px 600px at 0% 100%, rgba(20,184,166,.18), transparent 70%),
                linear-gradient(135deg, #021a18 0%, #05332f 55%, #0a5a53 100%); }
  .hero2 > .art { position: absolute; left: 0; top: 0; width: 100%; height: 100%; z-index: 0; opacity: .9; }
  .hero2 > .h2l, .hero2 > .tablet { position: relative; z-index: 1; }
  .hero2 h1 { font-size: 138px; line-height: .97; letter-spacing: -4.8px; font-weight: 800; margin: 28px 0 22px; }
  .hero2 h1 span { background: linear-gradient(90deg, #86efdc, #2dd4bf); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .hero2 .sub { font-size: 54px; font-weight: 500; color: rgba(255,255,255,.9); letter-spacing: -.5px; }
  .tablet { margin: 0; transform: perspective(2600px) rotateY(-13deg) rotateZ(-2.5deg); transform-origin: 30% 50%; }
  .tablet .bezel { background: linear-gradient(135deg, #12231f, #060e0d); border: 3px solid #2d5650; border-radius: 40px; padding: 22px;
    box-shadow: 0 60px 90px -30px rgba(0,0,0,.8), 0 0 0 12px rgba(94,234,212,.08), 0 0 140px rgba(45,212,191,.38); }
  .tablet img { display: block; width: 100%; border-radius: 18px; }
  .tablet .fl { position: absolute; width: 124px; height: 124px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 66px; border: 8px solid #fff;
    box-shadow: 0 0 80px rgba(255,255,255,.18), 0 24px 40px -14px rgba(0,0,0,.6); }
  .tablet .fl.a { left: -58px; bottom: 62px; background: linear-gradient(135deg, #ff6a63, #d03b3b); }
  .tablet .fl.g { right: -30px; top: -52px; background: linear-gradient(135deg, #3ddc84, #109a4a); }
  .gstrip { position: relative; z-index: 3; margin: -68px 100px 0; background: #fff; border-radius: 42px; border: 2px solid var(--line); box-shadow: 0 34px 60px -26px rgba(2,26,24,.6);
    display: grid; grid-template-columns: 250px repeat(4, 1fr); align-items: center; padding: 26px 34px 26px 44px; gap: 14px; }
  .gstrip .gt { font-size: 30px; font-weight: 800; letter-spacing: 5px; text-transform: uppercase; color: var(--t800); line-height: 1.25; border-right: 3px solid var(--line); padding-right: 14px; }
  .gstrip .g { display: flex; align-items: center; gap: 18px; padding-left: 18px; }
  .gstrip .n { width: 66px; height: 66px; border-radius: 50%; flex: none; display: flex; align-items: center; justify-content: center; font-size: 30px; font-weight: 800; color: #fff;
    background: linear-gradient(135deg, var(--t800), var(--t500)); box-shadow: 0 0 0 7px rgba(20,184,166,.14); }
  .gstrip b { display: block; font-size: 38px; font-weight: 800; letter-spacing: -.5px; color: var(--t900); line-height: 1.05; }
  .gstrip small { display: block; font-size: 25px; font-weight: 500; color: var(--ink2); margin-top: 3px; }
  .flow2 { flex: 1; min-height: 0; padding: 22px 100px 0; display: flex; flex-direction: column; }
  .band2 { margin: 30px 100px 0; border-radius: 44px; overflow: hidden; position: relative; color: #fff; display: grid; grid-template-columns: 1fr 940px; align-items: center; padding: 0 56px 0 64px; height: 318px;
    background: radial-gradient(900px 400px at 85% 50%, rgba(45,212,191,.35), transparent 65%), linear-gradient(135deg, #021a18, #06403b 60%, #0a5a53);
    box-shadow: 0 34px 60px -28px rgba(2,26,24,.7); }
  .band2::before { content: ""; position: absolute; inset: 0; background-image: linear-gradient(rgba(167,243,230,.06) 2px, transparent 2px), linear-gradient(90deg, rgba(167,243,230,.06) 2px, transparent 2px); background-size: 60px 60px; }
  .band2 > * { position: relative; }
  .band2 .bar { width: 120px; height: 8px; border-radius: 4px; background: var(--t300); margin-bottom: 22px; }
  .band2 h2 { margin: 0; font-size: 78px; line-height: 1.02; letter-spacing: -2.4px; font-weight: 800; }
  .band2 h2 span { background: linear-gradient(90deg, #86efdc, #3ddc84); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .band2 p { margin: 18px 0 0; font-size: 31px; font-weight: 500; color: var(--t200); }
  .band2 svg { width: 100%; height: 100%; }
"""


def col_card(x, y, label, sub, name, fill):
    w, h = 226, 196
    o = [f'<rect x="{x + 3}" y="{y + 10}" width="{w}" height="{h}" rx="34" fill="{T900}" opacity=".10"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="34" fill="#fff" stroke="{LINE}" stroke-width="2.5"/>',
         f'<circle cx="{x + w / 2}" cy="{y + 70}" r="48" fill="{fill}"/>',
         f'<circle cx="{x + w / 2}" cy="{y + 70}" r="58" fill="none" stroke="{fill}" stroke-opacity=".22" stroke-width="6"/>',
         icon(name, x + w / 2, y + 70, 54, "#fff", 1.9),
         text(x + w / 2, y + 156, label, 33, 800, T900, "middle", -.5),
         text(x + w / 2, y + 184, sub, 22, 500, INK2, "middle")]
    return "".join(o)


def chevrons(cx, cy):
    o = []
    for i, op in enumerate((.35, .65, 1)):
        x = cx - 34 + i * 30
        o.append(f'<path d="M{x},{cy - 30} L{x + 24},{cy} L{x},{cy + 30}" fill="none" stroke="{T400}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>')
    return "".join(o)


def head2(x, anchor, small, big):
    return (text(x, 40, small, 26, 700, T600, anchor, 6) + text(x, 92, big, 46, 800, T900, anchor, -1.2))


def build_flow():
    ba.VS, ba.CS = 64, 30
    ring = [f'<circle cx="{ba.RC[0]}" cy="{ba.RC[1]}" r="{ba.RR + 150}" fill="url(#mHalo)"/>',
            f'<circle cx="{ba.RC[0]}" cy="{ba.RC[1]}" r="{ba.RR - 128}" fill="none" stroke="{T300}" stroke-width="2.5" stroke-dasharray="2 15" stroke-linecap="round" opacity=".7"/>',
            ba.ring_arcs(), ba.balanced_scale(), ba.ring_nodes()]
    sc = 0.71
    o = []
    o.append(f'<rect x="296" y="122" width="1368" height="948" rx="52" fill="#fff" fill-opacity=".65" stroke="{LINE}" stroke-width="2.5"/>')
    o.append(f'<g transform="translate(980 677) scale({sc}) translate({-ba.RC[0]} {-ba.RC[1]})">' + "".join(ring) + "</g>")
    ys = [150, 372, 594, 816]
    left = [("Code", "software repo", "code"), ("Changes", "change requests", "clip"), ("Hardware", "parts & BOMs", "chip"), ("Releases", "versions", "box")]
    right = [("Dashboard", "live status", "grid"), ("Alerts", "unapproved", "alert"), ("Baselines", "approved versions", "layers"), ("Reports", "PDF audit", "file")]
    lf = [T700, T700, T700, T700]
    rf = [T700, RED, GREEN, T900]
    for y, (l, s_, n_), f in zip(ys, left, lf):
        o.append(col_card(0, y, l, s_, n_, f))
    for y, (l, s_, n_), f in zip(ys, right, rf):
        o.append(col_card(1734, y, l, s_, n_, f))
    o.append(chevrons(260, 596))
    o.append(chevrons(1700, 596))
    o.append(head2(0, "start", "FROM", "MULTIPLE SOURCES"))
    o.append(head2(980, "middle", "OUR SOLUTION", "One control loop"))
    o.append(head2(1960, "end", "TO", "ACTIONABLE INSIGHTS"))
    return defs() + "".join(o)


def band_svg():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 318" font-family="{ba.FONT_FAMILY}">', defs()]
    o.append(f'<g transform="translate(10 48) scale(.9)">{window(0, 0, 800, 226)}</g>')
    o.append(f'<g transform="translate(748 40) scale(.98)">{doc(0, 0)}</g>')
    o.append("</svg>")
    return "".join(o)


def head_html():
    prods = "".join(f'<span><svg class="ico"><use href="#i-{k}"/></svg></span>' for k in ("phone", "car", "plane", "heart", "factory"))
    goals = [("Track", "every item", "layers"), ("Control", "every change", "shield"), ("Detect", "drift automatically", "alert"), ("Audit", "in seconds", "file")]
    gs = "".join(f'<div class="g"><span class="n">{i + 1}</span><div><b>{t}</b><small>{s}</small></div></div>' for i, (t, s, _) in enumerate(goals))
    return f"""<header class="hero2">
    <!--ART:begin--><!--ART:end-->
    <div class="h2l">
      <div class="chip"><i></i>Final Year Project</div>
      <h1>Configuration<br>Control<br><span>Dashboard</span></h1>
      <div class="sub">for any configurable product</div>
      <div class="prods">{prods}</div>
    </div>
    <figure class="tablet">
      <div class="bezel"><img src="assets/hero_overview.png" alt="CCD dashboard showing detected drift"></div>
      <span class="fl a"><svg class="ico"><use href="#i-alert"/></svg></span>
      <span class="fl g"><svg class="ico"><use href="#i-shield"/></svg></span>
    </figure>
  </header>
  <section class="gstrip"><div class="gt">Project<br>Goals</div>{gs}</section>

  <main class="flow2">
    <div class="map"><!--MAP:begin--><!--MAP:end--></div>
  </main>

  <section class="band2">
    <div><div class="bar"></div><h2>A smarter way to<br><span>control any product</span></h2><p>Web dashboard &nbsp;|&nbsp; Python &nbsp;|&nbsp; Automation</p></div>
    <div><!--BAND:begin--><!--BAND:end--></div>
  </section>
"""


def main():
    with open(os.path.join(HERE, "poster.html"), encoding="utf-8") as fh:
        base = fh.read()
    a = base.index('<header class="header">')
    b = base.index("</main>") + len("</main>")
    base = base[:a] + head_html() + base[b:]
    base = base.replace("</style>", CSS + "</style>", 1)
    art = (f'<svg class="art" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2160 800" preserveAspectRatio="xMidYMid slice" aria-hidden="true">{header_art()}</svg>')
    mp = wrap_map(build_flow(), 1130)
    for target, built in ((OUT, built_html()), (OUT_PLAIN, "")):
        html = inject(inject(inject(inject(base, "MAP", mp), "ART", art), "BUILT", built), "BAND", band_svg())
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(html)


if __name__ == "__main__":
    main()
