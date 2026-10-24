#!/usr/bin/env python3
import bisect
import json
import math
import os
import random
import re

from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "poster.html")
HTML_PLAIN = os.path.join(HERE, "poster_no_credits.html")
HTML_SIDE = os.path.join(HERE, "poster_side.html")
HTML_SIDE_PLAIN = os.path.join(HERE, "poster_side_no_credits.html")
OUT_SVG = os.path.join(HERE, "workflow.svg")
FONT_FILE = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
FONT_FAMILY = "Inter, 'Segoe UI', Arial, sans-serif"

T950, T900, T800, T700, T600, T500, T400, T300, T200, T100, T50 = (
    "#04302c", "#06403b", "#0a5a53", "#0f766e", "#13897e", "#14b8a6",
    "#2dd4bf", "#5eead4", "#a7f3e6", "#d9f5ef", "#effaf8",
)
INK, INK2, LINE = "#0a2926", "#46625e", "#cfe3df"
RED, RED_D, AMBER, GREEN, GREEN_L = "#e0443f", "#a52828", "#f5a30a", "#1fa854", "#3ddc84"

W, H = 1960, 1340
CX = 1040
SRC_X = [CX - 640, CX - 200, CX + 200, CX + 640]
SRC_Y, SRC_R = 50, 46
SOURCES = [("Code", "code"), ("Changes", "clip"), ("Hardware", "chip"), ("Releases", "box")]
DBC = (CX, 248)
DB_END = 190
PIV = (CX, 440)
HALF, THETA, HANG = 320, 7.0, 142
BASE_Y = PIV[1] + 226
FORK_Y = 730
HEAD_TOP, HEAD_W, HEAD_H = 790, 116, 156
ALARM_X, MATCH_X = CX - 290, CX + 290
LOOP_X = 170
STN_Y = [834, 709, 585, 460]
WIN = (CX - 340, 1072, 800, 226)
DOC = (CX + 516, 1062)
EL = (PIV[0] - HALF * math.cos(math.radians(THETA)), PIV[1] - HALF * math.sin(math.radians(THETA)))
ER = (PIV[0] + HALF * math.cos(math.radians(THETA)), PIV[1] + HALF * math.sin(math.radians(THETA)))
CHIP_DY = HANG - 44

SYMBOLS = {
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "clip": '<rect x="5" y="5" width="14" height="16" rx="2.5"/><rect x="9" y="3" width="6" height="4" rx="1.2"/><path d="M9 14l2.2 2.2L15.5 12"/>',
    "chip": '<rect x="6.5" y="6.5" width="11" height="11" rx="2"/><rect x="10" y="10" width="4" height="4" rx=".6"/><path d="M9.5 3v3.5M14.5 3v3.5M9.5 17.5V21M14.5 17.5V21M3 9.5h3.5M3 14.5h3.5M17.5 9.5H21M17.5 14.5H21"/>',
    "box": '<path d="M12 2.8l8.2 4.6v9.2L12 21.2l-8.2-4.6V7.4z"/><path d="M3.8 7.4L12 12l8.2-4.6M12 12v9.2"/>',
    "shield": '<path d="M12 2.8l7.5 2.8v6.1c0 4.7-3.1 8.1-7.5 9.9-4.4-1.8-7.5-5.2-7.5-9.9V5.6z"/><path d="M8.6 12.2l2.5 2.5 4.4-4.9"/>',
    "pulse": '<path d="M2.5 12h4l2.6-7 5.2 14 2.6-7h4.6"/>',
    "badge": '<circle cx="12" cy="9.5" r="6.5"/><path d="M9.2 9.6l2 2 3.6-4M8.6 15l-1.6 6.2 5-2.4 5 2.4-1.6-6.2"/>',
    "alert": '<path d="M12 3L22 20.5H2z"/><path d="M12 9.8v5M12 17.6v.1"/>',
    "filep": '<path d="M6 2.8h8.2L19 7.6V21H6z"/><path d="M14 2.8v5h5M12.5 11.8v6M9.5 14.8h6"/>',
    "eye": '<path d="M1.8 12S5.7 5 12 5s10.2 7 10.2 7-3.9 7-10.2 7S1.8 12 1.8 12z"/><circle cx="12" cy="12" r="3"/>',
    "stamp": '<circle cx="12" cy="5.6" r="3.3"/><path d="M12 8.9V12"/><path d="M5.8 12h12.4a1.6 1.6 0 0 1 1.6 1.6V16.5H4.2v-2.9A1.6 1.6 0 0 1 5.8 12z"/><path d="M3 20.6h18"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="2.3"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/><path d="M12 14.6v2.3"/>',
    "check": '<path d="M4.5 12.8l5 5L19.5 7"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "db": '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.8"/><path d="M4.5 5.5v13c0 1.55 3.35 2.8 7.5 2.8s7.5-1.25 7.5-2.8v-13M4.5 12c0 1.55 3.35 2.8 7.5 2.8s7.5-1.25 7.5-2.8"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/><path d="M8 10.6l1.8 1.8 3.2-3.6"/>',
    "file": '<path d="M6 2.8h8.2L19 7.6V21H6z"/><path d="M14 2.8v5h5M9.5 13h6M9.5 16.8h6"/>',
}

_fonts = {}


def tw(text, size, weight="Bold"):
    key = (weight, size)
    if key not in _fonts:
        try:
            _fonts[key] = ImageFont.truetype(FONT_FILE % weight, size)
        except OSError:
            _fonts[key] = None
    if _fonts[key] is None:
        return 0.6 * size * len(text)
    return _fonts[key].getlength(text)


def n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
    )


class Route:
    def __init__(self, x, y):
        self.start = (x, y)
        self.cur = (x, y)
        self.segs = []
        self._cache = None

    def line(self, x, y):
        self.segs.append(("L", self.cur, (x, y)))
        self.cur = (x, y)
        return self

    def curve(self, x1, y1, x2, y2, x, y):
        self.segs.append(("C", self.cur, (x1, y1), (x2, y2), (x, y)))
        self.cur = (x, y)
        return self

    def d(self):
        out = [f"M{n(self.start[0])},{n(self.start[1])}"]
        for g in self.segs:
            if g[0] == "L":
                out.append(f"L{n(g[2][0])},{n(g[2][1])}")
            else:
                out.append("C" + " ".join(f"{n(p[0])},{n(p[1])}" for p in g[2:]))
        return " ".join(out)

    def _table(self):
        if self._cache is None:
            pts = [self.start]
            for g in self.segs:
                if g[0] == "L":
                    a, b = g[1], g[2]
                    steps = max(2, int(math.dist(a, b) / 2))
                    pts += [(a[0] + (b[0] - a[0]) * i / steps, a[1] + (b[1] - a[1]) * i / steps) for i in range(1, steps + 1)]
                else:
                    pts += [bez(g[1], g[2], g[3], g[4], i / 240) for i in range(1, 241)]
            cum = [0.0]
            for i in range(1, len(pts)):
                cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
            self._cache = (pts, cum)
        return self._cache

    def length(self):
        return self._table()[1][-1]

    def at(self, s):
        pts, cum = self._table()
        s = max(0.0, min(s, cum[-1]))
        i = max(1, min(bisect.bisect_left(cum, s), len(pts) - 1))
        a, b = pts[i - 1], pts[i]
        seg = cum[i] - cum[i - 1] or 1.0
        t = (s - cum[i - 1]) / seg
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        j0, j1 = max(0, i - 3), min(len(pts) - 1, i + 2)
        ang = math.degrees(math.atan2(pts[j1][1] - pts[j0][1], pts[j1][0] - pts[j0][0]))
        return x, y, ang


def text(x, y, s, size, weight=700, fill=INK, anchor="start", spacing=0):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{n(x)}" y="{n(y)}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{sp}>{s}</text>')


def icon(name, cx, cy, size, color, sw=1.9):
    return (f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            f'<use href="#m-{name}" x="{n(cx - size / 2)}" y="{n(cy - size / 2)}" width="{n(size)}" height="{n(size)}"/></g>')


def chip(cx, cy, s, size=32, h=46, color=INK, pad=22):
    w = tw(s, size) + pad * 2
    return (f'<rect x="{n(cx - w / 2 + 2)}" y="{n(cy - h / 2 + 6)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{T900}" opacity=".10"/>'
            f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="#fff" stroke="{LINE}" stroke-width="2.5"/>'
            + text(cx, cy + size * 0.36, s, size, 700, color, "middle"))


def chip2(cx, cy, title, sub, color=INK):
    w = max(tw(title, 31), tw(sub, 26, "Medium")) + 52
    h = 82
    return (f'<rect x="{n(cx - w / 2 + 2)}" y="{n(cy - h / 2 + 6)}" width="{n(w)}" height="{h}" rx="28" fill="{T900}" opacity=".10"/>'
            f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{h}" rx="28" fill="#fff" stroke="{LINE}" stroke-width="2.5"/>'
            + text(cx, cy - 6, title, 31, 700, color, "middle")
            + text(cx, cy + 25, sub, 26, 500, INK2, "middle"))


def stage(num, x, y, verb, cap, centered=False):
    width = 27 * 2 + 14 + tw(verb, 58, "ExtraBold")
    if centered:
        x = x - max(width, tw(cap, 30, "Medium") + 68) / 2
    s = f'<circle cx="{n(x + 27)}" cy="{n(y)}" r="27" fill="{T800}"/>'
    s += text(x + 27, y + 11, str(num), 30, 800, "#fff", "middle")
    s += text(x + 68, y + 20, verb, 58, 800, T900, "start", -1.5)
    s += text(x + 68, y + 62, cap, 30, 500, INK2)
    return s


def tracks(items):
    out = []
    for rt, stroke, width in items:
        out.append(f'<path d="{rt.d()}" fill="none" stroke="#fff" stroke-opacity=".96" stroke-width="{width + 12}" stroke-linecap="round" stroke-linejoin="round"/>')
    for rt, stroke, width in items:
        out.append(f'<path d="{rt.d()}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
    chev = []
    for rt, stroke, width in items:
        length = rt.length()
        p = 30.0
        while p < length - 14:
            x, y, a = rt.at(p)
            chev.append(f'<path d="M-4.5,-6.5L3.5,0L-4.5,6.5" transform="translate({n(x)} {n(y)}) rotate({n(a)})"/>')
            p += 58
    out.append(f'<g fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" opacity=".95">{"".join(chev)}</g>')
    return "".join(out)


def token(rt, s, color, tail=3):
    x, y, _ = rt.at(s)
    out = [f'<circle cx="{n(x)}" cy="{n(y)}" r="27" fill="{color}" opacity=".16"/>']
    for k in range(tail, 0, -1):
        tx, ty, _ = rt.at(s - 17 * k)
        out.append(f'<circle cx="{n(tx)}" cy="{n(ty)}" r="{n(12 - k * 2.2)}" fill="{color}" opacity="{n(0.62 - k * 0.15)}"/>')
    out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="15" fill="{color}" stroke="#fff" stroke-width="4"/>')
    out.append(f'<circle cx="{n(x - 4)}" cy="{n(y - 4)}" r="4" fill="#fff" opacity=".85"/>')
    return "".join(out)


def port(x, y, name):
    return (f'<circle cx="{x}" cy="{y + 8}" r="{SRC_R}" fill="{T900}" opacity=".12"/>'
            f'<circle cx="{x}" cy="{y}" r="{SRC_R}" fill="#fff" stroke="{T300}" stroke-width="6"/>'
            f'<circle cx="{x}" cy="{y}" r="{SRC_R - 12}" fill="{T50}"/>'
            + icon(name, x, y, 48, T700))


def equation(x, y):
    rows = [("", T700, "Approved"), ("+", GREEN, "Authorized"), ("=", INK, "Actual")]
    w, h = 330, 168
    s = f'<rect x="{x + 3}" y="{y + 9}" width="{w}" height="{h}" rx="32" fill="{T900}" opacity=".10"/>'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="32" fill="#fff" stroke="{LINE}" stroke-width="2.5"/>'
    for i, (op, col, word) in enumerate(rows):
        cy = y + 46 + i * 44
        if op:
            s += text(x + 40, cy + 11, op, 34, 800, INK2, "middle")
        s += f'<circle cx="{x + 84}" cy="{cy}" r="11" fill="{col}"/>'
        s += text(x + 108, cy + 11, word, 32, 700, INK)
    return s


def database():
    x, y = DBC
    rx, ry, hh = 74, 24, 56
    s = f'<g transform="translate({x} {y})">'
    s += f'<circle cx="0" cy="0" r="150" fill="url(#mGlowT)"/>'
    s += f'<ellipse cx="0" cy="{hh + ry + 8}" rx="{rx + 26}" ry="13" fill="{T900}" opacity=".13"/>'
    s += f'<path d="M{-rx},{-hh} V{hh} A{rx},{ry} 0 0 0 {rx},{hh} V{-hh} Z" fill="url(#mDb)"/>'
    for yy in (-12, 32):
        s += f'<path d="M{-rx},{yy} A{rx},{ry} 0 0 0 {rx},{yy}" fill="none" stroke="#fff" stroke-opacity=".34" stroke-width="4"/>'
    for yy in (10, 54):
        for xx in (-46, -30):
            s += f'<circle cx="{xx}" cy="{yy + 10}" r="4.5" fill="{T300}"/>'
    s += f'<ellipse cx="0" cy="{-hh}" rx="{rx}" ry="{ry}" fill="url(#mDbTop)"/>'
    s += f'<ellipse cx="0" cy="{-hh}" rx="{rx - 20}" ry="{ry - 8}" fill="none" stroke="#fff" stroke-opacity=".75" stroke-width="3"/>'
    s += "</g>"
    return s


def scale_art():
    px, py = PIV
    el, er = EL, ER
    s = []
    s.append(f'<ellipse cx="{px}" cy="{BASE_Y + 34}" rx="230" ry="15" fill="{T900}" opacity=".12"/>')
    s.append(f'<rect x="{px - 17}" y="{py}" width="34" height="{BASE_Y - py}" rx="9" fill="url(#mPost)"/>')
    s.append(f'<rect x="{px - 26}" y="{py + 88}" width="52" height="13" rx="6.5" fill="{T900}"/>')
    s.append(f'<rect x="{px - 26}" y="{py + 140}" width="52" height="13" rx="6.5" fill="{T900}"/>')
    s.append(f'<rect x="{px - 104}" y="{BASE_Y - 16}" width="208" height="22" rx="11" fill="url(#mPost)"/>')
    s.append(f'<rect x="{px - 170}" y="{BASE_Y}" width="340" height="28" rx="14" fill="url(#mPost)"/>')
    s.append(f'<rect x="{px - 150}" y="{BASE_Y + 4}" width="300" height="4" rx="2" fill="#fff" opacity=".22"/>')
    s.append(f'<rect x="{px - 7}" y="{py - 62}" width="14" height="40" rx="7" fill="{T900}"/>')
    s.append(f'<circle cx="{px}" cy="{py - 62}" r="14" fill="{T700}" stroke="{T300}" stroke-width="4"/>')
    s.append(f'<g transform="translate({n(px)} {n(py)}) rotate({THETA})">')
    s.append(f'<path d="M-352,-9 L-72,-19 Q0,-25 72,-19 L352,-9 A9,9 0 0 1 352,9 L72,19 Q0,25 -72,19 L-352,9 A9,9 0 0 1 -352,-9 Z" fill="url(#mBeam)"/>')
    s.append(f'<path d="M-338,-7 L-72,-16 Q0,-21 72,-16 L338,-7" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="3" stroke-linecap="round"/>')
    for sx in (-HALF, HALF):
        s.append(f'<circle cx="{sx}" cy="0" r="16" fill="{T900}" stroke="{T300}" stroke-width="3.5"/><circle cx="{sx}" cy="0" r="4.5" fill="{T300}"/>')
    s.append("</g>")
    s.append(f'<circle cx="{px}" cy="{py}" r="31" fill="{T900}" stroke="{T300}" stroke-width="4"/><circle cx="{px}" cy="{py}" r="11" fill="{T300}"/>')
    for e in (el, er):
        s.append(f'<g transform="translate({n(e[0])} {n(e[1])})">')
        s.append(f'<ellipse cx="0" cy="{HANG + 48}" rx="74" ry="8" fill="{T900}" opacity=".10"/>')
        s.append(f'<path d="M0,0 L-106,{HANG} M0,0 L106,{HANG}" stroke="{T700}" stroke-width="4" stroke-linecap="round" fill="none"/>')
        s.append(f'<path d="M-120,{HANG} C-96,{HANG + 50} 96,{HANG + 50} 120,{HANG} Z" fill="url(#mDish)" stroke="{T700}" stroke-width="5" stroke-linejoin="round"/>')
        s.append(f'<path d="M-122,{HANG} H122" stroke="{T700}" stroke-width="8" stroke-linecap="round"/>')
        s.append("</g>")
    cy_item = CHIP_DY
    lx, ly = el[0] - 48, el[1] + cy_item
    s.append(f'<ellipse cx="{n(lx)}" cy="{n(ly + 46)}" rx="40" ry="6" fill="{T900}" opacity=".14"/>')
    s.append(f'<circle cx="{n(lx)}" cy="{n(ly)}" r="44" fill="{T700}" stroke="#fff" stroke-width="4"/>')
    s.append(icon("shield", lx, ly, 46, "#fff"))
    s.append(f'<circle cx="{n(lx + 31)}" cy="{n(ly - 36)}" r="18" fill="{T900}" stroke="#fff" stroke-width="3.5"/>')
    s.append(text(lx + 31, ly - 29.5, "v1", 19, 800, "#fff", "middle"))
    sx_, sy_ = el[0] + 48, el[1] + cy_item
    s.append(f'<circle cx="{n(sx_)}" cy="{n(sy_)}" r="44" fill="#fff" fill-opacity=".55" stroke="{T400}" stroke-width="4" stroke-dasharray="9 9"/>')
    s.append(icon("plus", sx_, sy_, 34, T400, 2.2))
    rx_, ry_ = er[0], er[1] + cy_item
    s.append(f'<circle cx="{n(rx_)}" cy="{n(ry_)}" r="82" fill="url(#mGlowR)"/>')
    s.append(f'<ellipse cx="{n(rx_)}" cy="{n(ry_ + 46)}" rx="40" ry="6" fill="{T900}" opacity=".14"/>')
    s.append(f'<circle cx="{n(rx_)}" cy="{n(ry_)}" r="44" fill="{INK}" stroke="{RED}" stroke-width="6"/>')
    s.append(icon("pulse", rx_, ry_, 46, "#fff"))
    s.append(f'<circle cx="{n(rx_ + 33)}" cy="{n(ry_ - 34)}" r="16" fill="{RED}" stroke="#fff" stroke-width="3.5"/>')
    s.append(text(rx_ + 33, ry_ - 27, "!", 24, 800, "#fff", "middle"))
    hover = (sx_, el[1] - 112)
    s.append(f'<path d="M{n(sx_)},{n(hover[1] + 62)} L{n(sx_)},{n(sy_ - 62)}" stroke="{GREEN}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 13" fill="none"/>')
    s.append(f'<path d="M{n(sx_ - 15)},{n(sy_ - 70)} L{n(sx_)},{n(sy_ - 50)} L{n(sx_ + 15)},{n(sy_ - 70)}" fill="none" stroke="{GREEN}" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>')
    s.append(f'<circle cx="{n(hover[0])}" cy="{n(hover[1])}" r="86" fill="url(#mGlowG)"/>')
    s.append(f'<circle cx="{n(hover[0])}" cy="{n(hover[1] + 7)}" r="50" fill="{T900}" opacity=".16"/>')
    s.append(f'<circle cx="{n(hover[0])}" cy="{n(hover[1])}" r="50" fill="url(#mGreenB)" stroke="#fff" stroke-width="5"/>')
    s.append(icon("badge", hover[0], hover[1], 54, "#fff", 2))
    labels = {
        "Approved": (el[0], el[1] + HANG + 36 + 40),
        "Actual": (er[0], er[1] + HANG + 36 + 40),
        "Authorized": (hover[0] - 50 - 18 - (tw("Authorized", 32) + 44) / 2, hover[1]),
    }
    return "".join(s), labels, el, er, hover


def head(cx, lit):
    top, w, h = HEAD_TOP, HEAD_W, HEAD_H
    s = f'<rect x="{cx - w / 2 + 7}" y="{top + 12}" width="{w}" height="{h}" rx="30" fill="{T900}" opacity=".16"/>'
    s += f'<rect x="{cx - w / 2}" y="{top}" width="{w}" height="{h}" rx="30" fill="url(#mHouse)" stroke="{T800}" stroke-width="3"/>'
    for i, (name, on_col, off_col) in enumerate((("red", "#ff5a52", "#4a2220"), ("green", GREEN_L, "#17402f"))):
        ly = top + 44 + 68 * i
        on = lit == name
        if on:
            s += f'<circle cx="{cx}" cy="{ly}" r="86" fill="url(#mGlow{"R" if name == "red" else "G"})"/>'
            s += f'<circle cx="{cx}" cy="{ly}" r="{47 if name == "red" else 44}" fill="none" stroke="{on_col}" stroke-width="4" opacity=".5"/>'
            if name == "red":
                s += f'<circle cx="{cx}" cy="{ly}" r="62" fill="none" stroke="{on_col}" stroke-width="3.5" opacity=".28"/>'
        s += f'<circle cx="{cx}" cy="{ly}" r="31" fill="#031a17"/>'
        s += f'<circle cx="{cx}" cy="{ly}" r="27" fill="{on_col if on else off_col}"/>'
        if on:
            s += f'<ellipse cx="{cx - 8}" cy="{ly - 10}" rx="10" ry="6.5" fill="#fff" opacity=".55"/>'
    return s


def station(cx, cy, color, name, solid=False, r=40):
    s = f'<circle cx="{cx}" cy="{cy + 7}" r="{r}" fill="{T900}" opacity=".13"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color if solid else "#fff"}" stroke="{color}" stroke-width="7"/>'
    s += icon(name, cx, cy, r * 1.08, "#fff" if solid else color, 2)
    return s


def window(x, y, w, h):
    p = [f'<g transform="translate({x} {y})">']
    p.append(f'<rect x="10" y="20" width="{w}" height="{h}" rx="26" fill="{T900}" opacity=".12"/>')
    p.append(f'<rect width="{w}" height="{h}" rx="26" fill="#fff" stroke="{T200}" stroke-width="4"/>')
    p.append(f'<path d="M2,42 V28 a24,24 0 0 1 24,-24 H{w - 26} a24,24 0 0 1 24,24 V42 Z" fill="{T50}"/>')
    p.append(f'<path d="M2,42 H{w - 2}" stroke="{T100}" stroke-width="2.5"/>')
    for i, c in enumerate((RED, AMBER, GREEN_L)):
        p.append(f'<circle cx="{30 + i * 22}" cy="23" r="6.5" fill="{c}"/>')
    p.append(text(100, 32, "Live dashboard", WT, 700, T800))
    for i in range(7):
        p.append(f'<rect x="20" y="{56 + i * 25}" width="24" height="17" rx="5" fill="{T700 if i == 0 else T200}"/>')
    tile_cols = [T500, T500, RED, GREEN]
    for i, c in enumerate(tile_cols):
        tx = 84 + i * 176
        p.append(f'<rect x="{tx}" y="56" width="164" height="60" rx="13" fill="#fff" stroke="{T100}" stroke-width="2.5"/>')
        p.append(f'<path d="M{tx},68 a13,13 0 0 1 13,-12 H{tx + 151} a13,13 0 0 1 13,12 V70 H{tx} Z" fill="{c}"/>')
        p.append(f'<rect x="{tx + 14}" y="80" width="62" height="8" rx="4" fill="{T100}"/>')
        p.append(f'<rect x="{tx + 14}" y="94" width="{[90, 70, 38, 100][i]}" height="14" rx="7" fill="{c}" opacity=".85"/>')
    special = {(3, 1): RED, (11, 0): RED, (11, 2): RED, (6, 2): "#cfd8d6", (13, 1): "#cfd8d6", (1, 0): "#cfd8d6"}
    shades = ["#2fbf71", "#27b366", "#37c97c"]
    for r in range(3):
        for c in range(15):
            col = special.get((c, r)) or shades[(c * 3 + r * 5) % 3]
            p.append(f'<rect x="{84 + c * 26}" y="{132 + r * 26}" width="22" height="22" rx="5.5" fill="{col}"/>')
    circ = 2 * math.pi * 34
    p.append(f'<circle cx="572" cy="170" r="34" fill="none" stroke="{T100}" stroke-width="15"/>')
    p.append(f'<circle cx="572" cy="170" r="34" fill="none" stroke="#2fbf71" stroke-width="15" stroke-dasharray="{n(circ * 0.88)} {n(circ)}" transform="rotate(-90 572 170)"/>')
    p.append(f'<circle cx="572" cy="170" r="34" fill="none" stroke="{RED}" stroke-width="15" stroke-dasharray="{n(circ * 0.07)} {n(circ)}" stroke-dashoffset="{n(-circ * 0.9)}" transform="rotate(-90 572 170)"/>')
    p.append(icon("check", 572, 170, 28, GREEN, 2.6))
    for i, hgt in enumerate((40, 64, 34, 76, 52)):
        p.append(f'<rect x="{648 + i * 28}" y="{208 - hgt}" width="18" height="{hgt}" rx="5" fill="{T600 if i == 3 else T300}"/>')
    p.append("</g>")
    return "".join(p)


def doc(x, y):
    p = [f'<g transform="translate({x} {y}) rotate(-4 95 120)">']
    p.append(f'<rect x="22" y="12" width="190" height="240" rx="18" fill="{T100}" stroke="{T200}" stroke-width="4" transform="rotate(6 117 132)"/>')
    p.append(f'<path d="M10,22 a18,18 0 0 1 18,-18 H148 L200,56 V230 a18,18 0 0 1 -18,18 H28 a18,18 0 0 1 -18,-18 Z" fill="{T900}" opacity=".12"/>')
    p.append(f'<path d="M0,18 a18,18 0 0 1 18,-18 H138 L190,52 V222 a18,18 0 0 1 -18,18 H18 a18,18 0 0 1 -18,-18 Z" fill="#fff" stroke="{T200}" stroke-width="4"/>')
    p.append(f'<path d="M138,2 V34 a18,18 0 0 0 18,18 H188 Z" fill="{T100}" stroke="{T200}" stroke-width="3" stroke-linejoin="round"/>')
    p.append(f'<rect x="22" y="30" width="92" height="20" rx="10" fill="{T700}"/>')
    for i, wd in enumerate((146, 118, 150, 92)):
        p.append(f'<rect x="22" y="{74 + i * 22}" width="{wd}" height="10" rx="5" fill="{T100}"/>')
    for i, hgt in enumerate((22, 36, 28, 40)):
        p.append(f'<rect x="{26 + i * 24}" y="{196 - hgt}" width="16" height="{hgt}" rx="4" fill="{T300 if i != 3 else T600}"/>')
    p.append(f'<rect x="22" y="204" width="58" height="24" rx="12" fill="{RED}"/>')
    p.append(text(51, 221.5, "PDF", 15, 800, "#fff", "middle"))
    p.append(f'<circle cx="166" cy="208" r="31" fill="{GREEN}" stroke="#fff" stroke-width="5"/>')
    p.append(icon("check", 166, 208, 34, "#fff", 2.8))
    p.append("</g>")
    return "".join(p)


def defs():
    syms = "".join(f'<symbol id="m-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in SYMBOLS.items())
    return f"""<defs>
<linearGradient id="mDb" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T800}"/><stop offset=".42" stop-color="{T600}"/><stop offset="1" stop-color="{T900}"/></linearGradient>
<linearGradient id="mDbTop" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T200}"/><stop offset="1" stop-color="{T400}"/></linearGradient>
<linearGradient id="mBeam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T600}"/><stop offset="1" stop-color="{T900}"/></linearGradient>
<linearGradient id="mPost" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T900}"/><stop offset=".5" stop-color="{T700}"/><stop offset="1" stop-color="{T900}"/></linearGradient>
<linearGradient id="mDish" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="{T100}"/></linearGradient>
<linearGradient id="mGreenB" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GREEN_L}"/><stop offset="1" stop-color="{GREEN}"/></linearGradient>
<linearGradient id="mHouse" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#12413c"/><stop offset="1" stop-color="#062421"/></linearGradient>
<linearGradient id="mLoop" gradientUnits="userSpaceOnUse" x1="0" y1="{STN_Y[0]}" x2="0" y2="{STN_Y[-1]}"><stop offset="0" stop-color="{RED}"/><stop offset=".34" stop-color="{AMBER}"/><stop offset=".72" stop-color="{GREEN_L}"/><stop offset="1" stop-color="{GREEN}"/></linearGradient>
<radialGradient id="mGlowT"><stop offset="0" stop-color="{T300}" stop-opacity=".42"/><stop offset="1" stop-color="{T300}" stop-opacity="0"/></radialGradient>
<radialGradient id="mGlowR"><stop offset="0" stop-color="#ff5a52" stop-opacity=".5"/><stop offset="1" stop-color="#ff5a52" stop-opacity="0"/></radialGradient>
<radialGradient id="mGlowG"><stop offset="0" stop-color="{GREEN_L}" stop-opacity=".5"/><stop offset="1" stop-color="{GREEN_L}" stop-opacity="0"/></radialGradient>
<radialGradient id="mHalo"><stop offset="0" stop-color="{T300}" stop-opacity=".34"/><stop offset=".6" stop-color="{T300}" stop-opacity=".12"/><stop offset="1" stop-color="{T300}" stop-opacity="0"/></radialGradient>
{syms}
</defs>"""


def build_map():
    px, py = PIV
    src = [Route(x, SRC_Y + SRC_R).curve(x, SRC_Y + SRC_R + 62, CX, DB_END - 62, CX, DB_END) for x in SRC_X]
    trunk = Route(CX, DBC[1] + 80).line(CX, py - 76)
    exit_ = Route(CX, BASE_Y + 28).line(CX, FORK_Y)
    alarm_a = Route(CX, FORK_Y).curve(CX, FORK_Y + 40, ALARM_X, HEAD_TOP - 40, ALARM_X, HEAD_TOP)
    alarm_b = Route(ALARM_X - HEAD_W / 2, STN_Y[0]).line(LOOP_X, STN_Y[0])
    chip_y = EL[1] + CHIP_DY
    loop = (Route(LOOP_X, STN_Y[0]).line(LOOP_X, STN_Y[-1]).line(450, STN_Y[-1])
            .curve(530, STN_Y[-1], 560, chip_y, 640, chip_y).line(EL[0] - 40, chip_y))
    match_a = Route(CX, FORK_Y).curve(CX, FORK_Y + 40, MATCH_X, HEAD_TOP - 40, MATCH_X, HEAD_TOP)
    match_b = Route(MATCH_X, HEAD_TOP + HEAD_H).line(MATCH_X, WIN[1] + 8)
    link = Route(WIN[0] + WIN[2], WIN[1] + 118).line(DOC[0] + 14, WIN[1] + 112)

    out = []
    out.append(f'<circle cx="{px}" cy="{py + 60}" r="560" fill="url(#mHalo)"/>')
    for r in (270, 410, 550):
        out.append(f'<circle cx="{px}" cy="{py + 40}" r="{r}" fill="none" stroke="{T300}" stroke-width="2.5" stroke-dasharray="2 15" stroke-linecap="round" opacity=".7"/>')

    out.append(tracks(
        [(r, T400, 12) for r in src]
        + [(trunk, T500, 12), (exit_, T500, 12), (alarm_a, RED, 12), (alarm_b, RED, 12),
           (loop, "url(#mLoop)", 12), (match_a, GREEN, 12), (match_b, GREEN, 12), (link, GREEN, 12)]
    ))

    for r in src:
        out.append(token(r, r.length() * 0.56, T400))
    out.append(token(trunk, trunk.length() * 0.5, T400, 2))
    out.append(token(alarm_a, alarm_a.length() * 0.6, RED))
    out.append(token(alarm_b, alarm_b.length() * 0.3, RED))
    out.append(token(loop, 62, RED))
    out.append(token(loop, 187, AMBER))
    out.append(token(loop, 312, GREEN_L))
    out.append(token(match_a, match_a.length() * 0.5, GREEN_L))

    for x, (label, name) in zip(SRC_X, SOURCES):
        out.append(port(x, SRC_Y, name))
        out.append(chip(x, SRC_Y + SRC_R + 24, label))

    out.append(database())

    scale_svg, labels, el, er, hover = scale_art()
    out.append(scale_svg)
    out.append(chip(labels["Approved"][0], labels["Approved"][1], "Approved"))
    out.append(chip(labels["Actual"][0], labels["Actual"][1], "Actual"))
    out.append(chip(labels["Authorized"][0], labels["Authorized"][1], "Authorized"))

    out.append(f'<circle cx="{CX}" cy="{FORK_Y}" r="17" fill="#fff" stroke="{T500}" stroke-width="6"/>')
    out.append(head(ALARM_X, "red"))
    out.append(head(MATCH_X, "green"))
    out.append(chip2(ALARM_X, HEAD_TOP + HEAD_H + 54, "Unapproved change", "Alarm raised", RED_D))
    out.append(chip2(MATCH_X, HEAD_TOP + HEAD_H + 54, "Match", "Compliant", "#0b6e33"))

    stations = [(RED, "filep", "Request", False), (AMBER, "eye", "Review", False),
                (GREEN, "stamp", "Approve", False), (GREEN, "lock", "New baseline", True)]
    for y, (col, name, label, solid) in zip(STN_Y, stations):
        out.append(station(LOOP_X, y, col, name, solid))
        out.append(chip(LOOP_X + 40 + 16 + (tw(label, 32) + 44) / 2, y, label))

    out.append(window(*WIN))
    out.append(doc(*DOC))
    out.append(chip(DOC[0] + 96, DOC[1] - 12, "Audit report"))

    out.append(stage(1, CX + 110, 252, "Collect", "one database"))
    out.append(stage(2, CX + 520, 470, "Compare", "three-way check"))
    out.append(equation(CX + 520, 590))
    out.append(stage(3, CX, 868, "Alert", "flag drift instantly", centered=True))
    out.append(stage(4, 84, 326, "Control", "change by approval"))
    out.append(stage(5, 84, 1160, "Report", "audit-ready anytime"))

    return defs() + "".join(out)


VS, CS = 62, 31
CHIPSZ, WT, TYPE2 = 31, 26, False
RC = (980, 722)
RR, NR = 490, 88
AMBER_D = "#e8920a"
STAGES = [
    ("Collect", "Sync every source", "db", T600, T800),
    ("Compare", "Three-way check", "search", T800, T900),
    ("Alert", "Flag drift instantly", "alert", RED, RED_D),
    ("Control", "Change by approval", "stamp", AMBER_D, "#9a5a00"),
    ("Report", "Audit-ready anytime", "file", GREEN, "#0b6e33"),
]
ARC_COLORS = [T400, RED, AMBER_D, GREEN_L, T300]


def r_ang(k):
    return math.radians(-90 + 72 * k)


def r_pt(a, r=RR):
    return RC[0] + r * math.cos(a), RC[1] + r * math.sin(a)


def ring_arcs():
    gap = 2 * math.asin((NR + 24) / (2 * RR))
    outlines, colored, chev, toks = [], [], [], []
    for k in range(5):
        a0, a1 = r_ang(k) + gap, r_ang(k + 1) - gap
        (x0, y0), (x1, y1) = r_pt(a0), r_pt(a1)
        d = f"M{n(x0)},{n(y0)} A{RR},{RR} 0 0 1 {n(x1)},{n(y1)}"
        dash = ""
        outlines.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".95" stroke-width="30" stroke-linecap="round"/>')
        colored.append(f'<path d="{d}" fill="none" stroke="{ARC_COLORS[k]}" stroke-width="16" stroke-linecap="round"{dash}/>')
        a = a0 + 0.5 * 58 / RR
        while a < a1 - 0.5 * 58 / RR:
            x, y = r_pt(a)
            chev.append(f'<path d="M-6,-8.5L5,0L-6,8.5" transform="translate({n(x)} {n(y)}) rotate({n(math.degrees(a) + 90)})"/>')
            a += 58 / RR
        f = 0.5
        am = a0 + (a1 - a0) * f
        x, y = r_pt(am)
        t = [f'<circle cx="{n(x)}" cy="{n(y)}" r="30" fill="{ARC_COLORS[k]}" opacity=".16"/>']
        for j in range(3, 0, -1):
            tx, ty = r_pt(am - j * 17 / RR)
            t.append(f'<circle cx="{n(tx)}" cy="{n(ty)}" r="{n(12 - j * 2.2)}" fill="{ARC_COLORS[k]}" opacity="{n(0.62 - j * 0.15)}"/>')
        t.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="15" fill="{ARC_COLORS[k]}" stroke="#fff" stroke-width="4"/>')
        t.append(f'<circle cx="{n(x - 4)}" cy="{n(y - 4)}" r="4" fill="#fff" opacity=".85"/>')
        if k != 4:
            toks.append("".join(t))
    chev_g = f'<g fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" opacity=".95">{"".join(chev)}</g>'
    return "".join(outlines) + "".join(colored) + chev_g + "".join(toks)


def ring_nodes():
    out = []
    for k, (verb, cap, name, color, dark) in enumerate(STAGES):
        x, y = r_pt(r_ang(k))
        out.append(f'<circle cx="{n(x)}" cy="{n(y + 10)}" r="{NR}" fill="{T900}" opacity=".15"/>')
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{NR + 18}" fill="{color}" opacity=".15"/>')
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{NR}" fill="{color}" stroke="#fff" stroke-width="9"/>')
        out.append(icon(name, x, y, 92, "#fff", 1.9))
        bx, by = x - NR * 0.74, y - NR * 0.74
        out.append(f'<circle cx="{n(bx)}" cy="{n(by)}" r="{34 if TYPE2 else 27}" fill="#fff" stroke="{color}" stroke-width="6"/>')
        out.append(text(bx, by + (14 if TYPE2 else 10.5), str(k + 1), 42 if TYPE2 else 31, 800, dark, "middle"))
        if TYPE2:
            blk = VS * 0.72 + 14 + CS * 0.9
            if k == 0:
                vb = y - NR - 26 - CS * 0.9 - 14
                out.append(text(x, vb, verb, VS, 800, T900, "middle", -1.5))
                out.append(text(x, vb + 14 + CS * 0.9, cap, CS, 500, INK2, "middle"))
            else:
                lx = x + NR + 36 if k in (1, 2) else x - NR - 36
                anc = "start" if k in (1, 2) else "end"
                vb = y - blk / 2 + VS * 0.72
                out.append(text(lx, vb, verb, VS, 800, T900, anc, -1.5))
                out.append(text(lx, vb + 14 + CS * 0.9, cap, CS, 500, INK2, anc))
            continue
        if k == 0:
            out.append(text(x, y - NR - 70, verb, VS, 800, T900, "middle", -1.5))
            out.append(text(x, y - NR - 28, cap, CS, 500, INK2, "middle"))
        elif k in (1, 2):
            lx = x + NR + 36
            out.append(text(lx, y + 4, verb, VS, 800, T900, "start", -1.5))
            out.append(text(lx, y + 50, cap, CS, 500, INK2, "start"))
        else:
            lx = x - NR - 36
            out.append(text(lx, y + 4, verb, VS, 800, T900, "end", -1.5))
            out.append(text(lx, y + 50, cap, CS, 500, INK2, "end"))
    return "".join(out)


def stack_chip(cx, cy, l1, l2, c1=INK, c2=GREEN):
    w = max(tw(l1, CHIPSZ), tw(l2, CHIPSZ)) + 52
    h = int(CHIPSZ * 2.84)
    return (f'<rect x="{n(cx - w / 2 + 2)}" y="{n(cy - h / 2 + 6)}" width="{n(w)}" height="{h}" rx="28" fill="{T900}" opacity=".10"/>'
            f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{h}" rx="28" fill="#fff" stroke="{LINE}" stroke-width="2.5"/>'
            + text(cx, cy - CHIPSZ * 0.2, l1, CHIPSZ, 700, c1, "middle") + text(cx, cy + CHIPSZ * 0.9, l2, CHIPSZ, 700, c2, "middle"))


def balanced_scale(cx=980, cy=650):
    half, hang = 250, 134
    base_y = cy + 206
    o = [f'<circle cx="{cx}" cy="{cy + 50}" r="330" fill="url(#mGlowT)"/>']
    o.append(f'<ellipse cx="{cx}" cy="{base_y + 38}" rx="210" ry="14" fill="{T900}" opacity=".12"/>')
    o.append(f'<rect x="{cx - 16}" y="{cy}" width="32" height="{base_y - cy}" rx="9" fill="url(#mPost)"/>')
    o.append(f'<rect x="{cx - 24}" y="{cy + 88}" width="48" height="13" rx="6.5" fill="{T900}"/>')
    o.append(f'<rect x="{cx - 96}" y="{base_y - 16}" width="192" height="22" rx="11" fill="url(#mPost)"/>')
    o.append(f'<rect x="{cx - 152}" y="{base_y}" width="304" height="28" rx="14" fill="url(#mPost)"/>')
    o.append(f'<rect x="{cx - 132}" y="{base_y + 4}" width="264" height="4" rx="2" fill="#fff" opacity=".22"/>')
    o.append(f'<g transform="translate({cx} {cy})">'
             f'<path d="M-272,-9 L-72,-19 Q0,-25 72,-19 L272,-9 A9,9 0 0 1 272,9 L72,19 Q0,25 -72,19 L-272,9 A9,9 0 0 1 -272,-9 Z" fill="url(#mBeam)"/>'
             f'<path d="M-258,-7 L-72,-16 Q0,-21 72,-16 L258,-7" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="3" stroke-linecap="round"/>'
             + "".join(f'<circle cx="{sx}" cy="0" r="16" fill="{T900}" stroke="{T300}" stroke-width="3.5"/><circle cx="{sx}" cy="0" r="4.5" fill="{T300}"/>' for sx in (-half, half))
             + "</g>")
    o.append(f'<rect x="{cx - 6}" y="{cy - 46}" width="12" height="30" rx="6" fill="{T900}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="31" fill="{T900}" stroke="{T300}" stroke-width="4"/><circle cx="{cx}" cy="{cy}" r="11" fill="{T300}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy - 72}" r="34" fill="{GREEN_L}" opacity=".25"/>')
    o.append(f'<circle cx="{cx}" cy="{cy - 72}" r="28" fill="url(#mGreenB)" stroke="#fff" stroke-width="5"/>')
    o.append(icon("check", cx, cy - 72, 30, "#fff", 3))
    for sx in (-half, half):
        px = cx + sx
        o.append(f'<g transform="translate({px} {cy})">'
                 f'<ellipse cx="0" cy="{hang + 46}" rx="70" ry="8" fill="{T900}" opacity=".10"/>'
                 f'<path d="M0,0 L-102,{hang} M0,0 L102,{hang}" stroke="{T700}" stroke-width="4" stroke-linecap="round" fill="none"/>'
                 f'<path d="M-116,{hang} C-92,{hang + 48} 92,{hang + 48} 116,{hang} Z" fill="url(#mDish)" stroke="{T700}" stroke-width="5" stroke-linejoin="round"/>'
                 f'<path d="M-118,{hang} H118" stroke="{T700}" stroke-width="8" stroke-linecap="round"/></g>')
    ly = cy + hang - 42
    for dx, col, name in ((-46, T700, "shield"), (46, GREEN, "badge")):
        x = cx - half + dx
        o.append(f'<ellipse cx="{x}" cy="{ly + 44}" rx="38" ry="6" fill="{T900}" opacity=".14"/>')
        o.append(f'<circle cx="{x}" cy="{ly}" r="40" fill="{col}" stroke="#fff" stroke-width="4"/>')
        o.append(icon(name, x, ly, 42, "#fff"))
    x = cx + half
    o.append(f'<circle cx="{x}" cy="{ly - 2}" r="78" fill="url(#mGlowG)"/>')
    o.append(f'<ellipse cx="{x}" cy="{ly + 46}" rx="40" ry="6" fill="{T900}" opacity=".14"/>')
    o.append(f'<circle cx="{x}" cy="{ly - 2}" r="44" fill="{INK}" stroke="{GREEN_L}" stroke-width="6"/>')
    o.append(icon("pulse", x, ly - 2, 46, "#fff"))
    o.append(stack_chip(cx - half, cy + hang + 108, "Approved", "+ Authorized"))
    o.append(chip(cx + half, cy + hang + 108, "Actual", CHIPSZ, int(CHIPSZ * 1.68)))
    return "".join(o)


RH = 1400


def build_ring():
    ring = [f'<circle cx="{RC[0]}" cy="{RC[1]}" r="{RR + 150}" fill="url(#mHalo)"/>']
    ring.append(f'<circle cx="{RC[0]}" cy="{RC[1]}" r="{RR - 128}" fill="none" stroke="{T300}" stroke-width="2.5" stroke-dasharray="2 15" stroke-linecap="round" opacity=".7"/>')
    ring.append(ring_arcs())
    ring.append(balanced_scale())
    ring.append(ring_nodes())
    out = [f'<g transform="translate(0 -112) translate({RC[0]} {RC[1]}) scale(.8) translate({-RC[0]} {-RC[1]})">' + "".join(ring) + "</g>"]
    wx, wy = 452, 1112
    out.append(f'<circle cx="{wx + 400}" cy="{wy + 120}" r="520" fill="url(#mHalo)"/>')
    lk = Route(wx + 800 + 6, wy + 118).line(wx + 862, wy + 112)
    out.append(tracks([(lk, GREEN, 12)]))
    out.append(window(wx, wy, 800, 226))
    out.append(doc(wx + 868, wy - 8))
    out.append(chip(wx + 868 + 96, wy - 20, "Audit report"))
    out.append(f'<circle cx="{wx + 4}" cy="{wy + 4}" r="30" fill="{GREEN}" stroke="#fff" stroke-width="6"/>')
    out.append(text(wx + 4, wy + 16, "5", 34, 800, "#fff", "middle"))
    return defs() + "".join(out)


def header_art(w=2160, h=800):
    rnd = random.Random(5)
    pts = []
    for _ in range(6000):
        if len(pts) >= 44:
            break
        p = (rnd.uniform(-30, w + 30), rnd.uniform(-30, h + 30))
        if all(math.dist(p, q) > 140 for q in pts):
            pts.append(p)
    edges = set()
    for i, p in enumerate(pts):
        for j in sorted(range(len(pts)), key=lambda k: math.dist(p, pts[k]))[1:4]:
            if math.dist(p, pts[j]) < 320:
                edges.add(tuple(sorted((i, j))))
    out = ['<defs><radialGradient id="aGlow"><stop offset="0" stop-color="#5eead4" stop-opacity=".55"/><stop offset="1" stop-color="#5eead4" stop-opacity="0"/></radialGradient></defs>']
    for i, j in sorted(edges):
        out.append(f'<line x1="{n(pts[i][0])}" y1="{n(pts[i][1])}" x2="{n(pts[j][0])}" y2="{n(pts[j][1])}" stroke="#a7f3e6" stroke-opacity=".16" stroke-width="2"/>')
    bright = set(rnd.sample(range(len(pts)), 9))
    for i, (x, y) in enumerate(pts):
        if i in bright:
            out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="34" fill="url(#aGlow)"/>')
            out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="14" fill="none" stroke="#5eead4" stroke-opacity=".55" stroke-width="2"/>')
            out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="6.5" fill="#5eead4"/>')
        else:
            out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rnd.uniform(3, 5.5))}" fill="#a7f3e6" fill-opacity=".38"/>')
    return "".join(out)


def inject(html, tag, body):
    pat = re.compile(rf"(<!--{tag}:begin-->).*?(<!--{tag}:end-->)", re.S)
    if not pat.search(html):
        raise SystemExit(f"missing markers for {tag}")
    return pat.sub(lambda m: m.group(1) + body + m.group(2), html)


def wrap_map(inner, h):
    return (f'<svg class="mapsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" '
            f'preserveAspectRatio="xMidYMid meet" font-family="{FONT_FAMILY}">{inner}</svg>')


def standalone(svg):
    out = svg.replace('<svg class="mapsvg" xmlns="http://www.w3.org/2000/svg"',
                      '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + out.replace("<use href=", "<use xlink:href=") + "\n"


def built_html():
    with open(os.path.join(HERE, "assets", "tool_icons.json"), encoding="utf-8") as fh:
        tools = json.load(fh)
    items = "".join(
        f'<div class="tool"><span class="ti"><svg viewBox="0 0 24 24"><path fill="{t["color"]}" d="{t["d"]}"/></svg></span><small>{t["name"]}</small></div>'
        for t in tools)
    return f'<section class="built"><div class="lbl">Built<br>with</div><div class="tools">{items}</div></section>'


def build_side():
    global VS, CS
    VS, CS = 76, 38
    ring = [f'<circle cx="{RC[0]}" cy="{RC[1]}" r="{RR + 150}" fill="url(#mHalo)"/>',
            f'<circle cx="{RC[0]}" cy="{RC[1]}" r="{RR - 128}" fill="none" stroke="{T300}" stroke-width="2.5" stroke-dasharray="2 15" stroke-linecap="round" opacity=".7"/>',
            ring_arcs(), balanced_scale(), ring_nodes()]
    sc, cx, cy = 0.645, 628, 612
    out = [f'<g transform="translate({cx} {cy}) scale({sc}) translate({-RC[0]} {-RC[1]})">' + "".join(ring) + "</g>"]
    VS, CS = 62, 31
    px = 1262
    out.append(f'<rect x="{px - 34}" y="170" width="3" height="780" rx="1.5" fill="{T200}"/>')
    out.append(f'<circle cx="{px + 340}" cy="560" r="470" fill="url(#mHalo)"/>')
    out.append(text(px + 340, 214, "What you get", 62, 800, T900, "middle", -1.5))
    out.append(f'<g transform="translate({px} 262) scale(0.85)">' + window(0, 0, 800, 226) + "</g>")
    out.append(f'<path d="M{px + 340},474 V540" stroke="{GREEN}" stroke-width="11" stroke-linecap="round"/>')
    out.append(f'<path d="M{px + 318},522 L{px + 340},548 L{px + 362},522" fill="none" stroke="{GREEN}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<g transform="translate({px + 214} 580) scale(1.38)">' + doc(0, 0) + "</g>")
    out.append(chip(px + 340 + 190, 590, "Audit report", 30, 48))
    return defs() + "".join(out)


def main():
    art_svg = (f'<svg class="art" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2160 800" '
               f'preserveAspectRatio="xMidYMid slice" aria-hidden="true">{header_art()}</svg>')
    with open(HTML, encoding="utf-8") as fh:
        base = fh.read()
    stacked = wrap_map(build_ring(), RH)
    side = wrap_map(build_side(), 1100)
    for target, mp, built in ((HTML, stacked, built_html()), (HTML_PLAIN, stacked, ""),
                              (HTML_SIDE, side, built_html()), (HTML_SIDE_PLAIN, side, "")):
        html = inject(inject(inject(base, "MAP", mp), "ART", art_svg), "BUILT", built)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(html)
    with open(OUT_SVG, "w", encoding="utf-8") as fh:
        fh.write(standalone(stacked))


if __name__ == "__main__":
    main()
