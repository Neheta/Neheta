#!/usr/bin/env python3
"""
build.py: generates a pastel-pink, pixel-art GitHub profile README.

  1. Edit profile.json
  2. Run:  python3 build.py
  3. Commit README.md, assets/ and .github/ to the repo named after your username

Everything visual (banner, headers, cards, footer) is a self-contained SVG with
its own pixel font, so GitHub's SVG sanitizer can't strip anything.
"""
import json
import random
import sys
import textwrap
import urllib.parse
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
PREVIEW = ROOT / "preview"
WARN = set()

# ── brand tokens ────────────────────────────────────────────────────────────
BG = "#1A1420"        # deep plum-black: banner, headers, footer
SURFACE = "#241B2E"   # cards
BORDER = "#3A2D45"    # borders, dividers, empty meter cells
TEXT = "#EDE3F0"      # body text
MUTED = "#A898B3"     # secondary text

THEMES = {
    "pink": dict(PINK="#FFB3D1", SOFT="#F8C8DC", BLUSH="#FFD6E8", ROSE="#D97AA5", ACCENT="#C8B6FF"),
    "peach": dict(PINK="#FFC2A8", SOFT="#FFD8C2", BLUSH="#FFE6D6", ROSE="#E0957A", ACCENT="#F3B6D1"),
    "rose-mint": dict(PINK="#FFB3D1", SOFT="#F8C8DC", BLUSH="#FFD6E8", ROSE="#D97AA5", ACCENT="#A8E6CF"),
}
PINK = SOFT = BLUSH = ROSE = ACCENT = ""

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
W = 800      # width of full-width assets
STEP = 4     # pixel-corner step used on every panel

# ── 5x7 pixel font ──────────────────────────────────────────────────────────
FONT_SRC = {
    "A": ".###. #...# #...# ##### #...# #...# #...#",
    "B": "####. #...# #...# ####. #...# #...# ####.",
    "C": ".###. #...# #.... #.... #.... #...# .###.",
    "D": "####. #...# #...# #...# #...# #...# ####.",
    "E": "##### #.... #.... ####. #.... #.... #####",
    "F": "##### #.... #.... ####. #.... #.... #....",
    "G": ".###. #...# #.... #.### #...# #...# .####",
    "H": "#...# #...# #...# ##### #...# #...# #...#",
    "I": ".###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.",
    "J": "..### ...#. ...#. ...#. ...#. #..#. .##..",
    "K": "#...# #..#. #.#.. ##... #.#.. #..#. #...#",
    "L": "#.... #.... #.... #.... #.... #.... #####",
    "M": "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    "N": "#...# #...# ##..# #.#.# #..## #...# #...#",
    "O": ".###. #...# #...# #...# #...# #...# .###.",
    "P": "####. #...# #...# ####. #.... #.... #....",
    "Q": ".###. #...# #...# #...# #.#.# #..#. .##.#",
    "R": "####. #...# #...# ####. #.#.. #..#. #...#",
    "S": ".#### #.... #.... .###. ....# ....# ####.",
    "T": "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    "U": "#...# #...# #...# #...# #...# #...# .###.",
    "V": "#...# #...# #...# #...# #...# .#.#. ..#..",
    "W": "#...# #...# #...# #.#.# #.#.# #.#.# .#.#.",
    "X": "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    "Y": "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
    "Z": "##### ....# ...#. ..#.. .#... #.... #####",
    "0": ".###. #...# #..## #.#.# ##..# #...# .###.",
    "1": "..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.",
    "2": ".###. #...# ....# ...#. ..#.. .#... #####",
    "3": "####. ....# ....# .###. ....# ....# ####.",
    "4": "...#. ..##. .#.#. #..#. ##### ...#. ...#.",
    "5": "##### #.... ####. ....# ....# #...# .###.",
    "6": ".###. #.... #.... ####. #...# #...# .###.",
    "7": "##### ....# ...#. ..#.. .#... .#... .#...",
    "8": ".###. #...# #...# .###. #...# #...# .###.",
    "9": ".###. #...# #...# .#### ....# ....# .###.",
    " ": "..... ..... ..... ..... ..... ..... .....",
    ".": "..... ..... ..... ..... ..... .##.. .##..",
    ",": "..... ..... ..... ..... .##.. ..#.. .#...",
    "!": "..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..",
    "?": ".###. #...# ....# ...#. ..#.. ..... ..#..",
    "-": "..... ..... ..... .###. ..... ..... .....",
    ":": "..... .##.. .##.. ..... .##.. .##.. .....",
    "'": "..#.. ..#.. .#... ..... ..... ..... .....",
    "/": "....# ....# ...#. ..#.. .#... #.... #....",
    "&": ".##.. #..#. #.#.. .#... #.#.# #..#. .##.#",
    "+": "..... ..#.. ..#.. ##### ..#.. ..#.. .....",
    "=": "..... ..... ##### ..... ##### ..... .....",
    "#": ".#.#. .#.#. ##### .#.#. ##### .#.#. .#.#.",
    "*": "..... #.#.# .###. ##### .###. #.#.# .....",
    ">": ".#... ..#.. ...#. ....# ...#. ..#.. .#...",
    "<": "...#. ..#.. .#... #.... .#... ..#.. ...#.",
    "_": "..... ..... ..... ..... ..... ..... #####",
    "(": "...#. ..#.. .#... .#... .#... ..#.. ...#.",
    ")": ".#... ..#.. ...#. ...#. ...#. ..#.. .#...",
    "♥": "..... .#.#. ##### ##### .###. ..#.. .....",
    "✦": "..#.. ..#.. .###. ##### .###. ..#.. ..#..",
}
FONT = {k: v.split() for k, v in FONT_SRC.items()}

CAT = [
    ".R.......R.",
    "RPR.....RPR",
    "RPPRRRRRPPR",
    "RPPPPPPPPPR",
    "RPEPPPPPEPR",
    "RPPPPRPPPPR",
    "RBPPPPPPPBR",
    ".RPPPPPPPR.",
    "..RRRRRRR..",
]
PLANT = [
    "..G.G..",
    ".GG.GG.",
    "..GGG..",
    "...G...",
    ".RRRRR.",
    "..PPP..",
    "..PPP..",
]
HEART = [
    ".##.##.",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
]
PETAL = [".#.", "###", ".#."]

# two curly-haired chibis holding hands (girl left, boy right); hands meet in the middle
COUPLE = [  # he's two pixels taller than her
    "...............BB.BB...",
    ".............BBbBBbBBB.",
    "..HH.HH.HH..BBbBBBBBbBB",
    ".HHhHHhHHH..BBKKKKKKKBB",
    "HHhHHHHHHhH..BKEKKKEKB.",
    "HHKKKKKKKHH...KCKKKCK..",
    "HhKEKKKEKhH...KKKKKKK..",
    "HHKCKKKCKHH....SSSSS...",
    "hHKKKKKKKHh...SSSSSSS..",
    "HH.DDDDD.HH...SSSSSSS..",
    "h..DDDDDDKh..KSSSSSSS..",
    "..DDDDDDD......SSSSS...",
    "..DDDDDDD......PP.PP...",
    "...K...K.......PP.PP...",
    "...R...R.......MM.MM...",
]
PLUM = "#7E4F7A"
COUPLE_PAD = 0  # the raised hand fits in the space above her head

# little story, 12s loop: (frame, start s, end s)
COUPLE_STORY = [
    ("idle", 0, 3),        # both face the screen, hands by their sides
    ("look", 3, 4.5),      # they look at each other and smile
    ("up", 4.5, 4.85), ("down", 4.85, 5.2),    # he pats her head (x3)
    ("up", 5.2, 5.55), ("down", 5.55, 5.9),
    ("up", 5.9, 6.25), ("down", 6.25, 6.6),
    ("cool", 6.6, 9.2),    # he looks back at the screen like nothing happened; she keeps smiling at him
    ("rest", 9.2, 12),     # both facing the screen again
]
COUPLE_LOOP = 12


def couple_frames():
    """Returns {frame name: rows} built from COUPLE plus small edits per frame (row/col in COUPLE coords)."""
    def grid():
        return [list("." * len(COUPLE[0])) for _ in range(COUPLE_PAD)] + [list(r) for r in COUPLE]

    def put(g, ch, *pts):
        for r, c in pts:
            g[r + COUPLE_PAD][c] = ch

    # her face: eyes (6,3) (6,7), mouth (8,5).  his face: eyes (4,15) (4,19), mouth (6,17)
    def neutral(g, girl=True, boy=True):
        if girl:
            put(g, "m", (8, 5))
        if boy:
            put(g, "m", (6, 17))

    def girl_smile(g): put(g, "m", (7, 4), (7, 6), (8, 5))
    def boy_smile(g): put(g, "m", (5, 16), (5, 18), (6, 17))

    def girl_looks_at_him(g):
        put(g, "K", (6, 3), (6, 7))
        put(g, "E", (6, 4), (6, 8))

    def boy_looks_at_her(g):
        put(g, "K", (4, 15), (4, 19))
        put(g, "E", (4, 14), (4, 18))

    def girl_happy_eyes(g):  # ^ ^
        put(g, "K", (6, 3), (6, 7))
        put(g, "E", (5, 3), (6, 2), (6, 4), (5, 7), (6, 6), (6, 8))

    def let_go(g, his_hand_down=True):
        put(g, "h", (10, 10))                    # her curl comes back where her hand was
        put(g, ".", (10, 11), (10, 12))
        if not his_hand_down:
            put(g, ".", (10, 13))

    def pat(g, up):
        let_go(g, his_hand_down=False)
        put(g, "S", (7, 14), (6, 13), (5, 12), (4, 11), (3, 11))
        # a small rounded hand resting on (down) or just above (up) her curls
        if up:
            put(g, "S", (2, 11))
            put(g, "K", (1, 10), (0, 7), (0, 8), (0, 9), (1, 6), (1, 7), (1, 8), (1, 9))
        else:
            put(g, "K", (2, 10), (1, 7), (1, 8), (1, 9), (2, 6), (2, 7), (2, 8), (2, 9))

    def boy_happy_eyes(g):  # ^ ^
        put(g, "K", (4, 15), (4, 19))
        put(g, "E", (3, 15), (4, 14), (4, 16), (3, 19), (4, 18), (4, 20))

    def happy(g):  # they always smile, with happy ^ ^ eyes
        girl_happy_eyes(g); girl_smile(g)
        boy_happy_eyes(g); boy_smile(g)

    def extra_blush(g):  # rosier cheeks for the heart moment
        put(g, "C", (7, 2), (7, 8), (5, 14), (5, 20))

    frames = {}
    g = grid(); happy(g); frames["idle"] = g
    g = grid(); happy(g); extra_blush(g); frames["look"] = g
    for name, up in (("up", True), ("down", False)):
        # during the head pat their eyes open and they look at each other, still smiling
        g = grid(); pat(g, up)
        girl_looks_at_him(g); girl_smile(g)
        boy_looks_at_her(g); boy_smile(g)
        extra_blush(g)
        frames[name] = g
    g = grid(); let_go(g); happy(g); frames["cool"] = g
    g = grid(); let_go(g); happy(g); frames["rest"] = g
    return {k: ["".join(r) for r in v] for k, v in frames.items()}


def couple_scene(x, bottom, s=3, uid="cp"):
    """Frame-by-frame pixel animation, like a gif, done with CSS so it stays a crisp SVG."""
    frames = couple_frames()
    rows, cols = len(COUPLE) + COUPLE_PAD, len(COUPLE[0])
    y = bottom - rows * s
    palette = {"H": ROSE, "h": PINK, "B": PLUM, "b": ROSE, "K": BLUSH, "E": BG, "C": PINK,
               "D": PINK, "S": ACCENT, "P": MUTED, "R": ROSE, "M": PLUM, "m": PLUM}
    T, eps = COUPLE_LOOP, 0.01
    css, body = [], []
    for name, g in frames.items():
        pts = []
        for n, a, b in COUPLE_STORY:
            if n != name:
                continue
            pa, pb = a / T * 100, b / T * 100
            pts += [(pa - eps, 0), (pa, 1)] if pa > 0 else [(0, 1)]
            pts += [(pb - eps, 1), (pb, 0)] if pb < 100 else [(100, 1)]
        if not any(p == 0 for p, _ in pts):
            pts.append((0, 0))
        if not any(p == 100 for p, _ in pts):
            pts.append((100, 0))
        kf = "".join(f"{p:.3f}%{{opacity:{v}}}" for p, v in sorted(pts))
        css.append(f"@keyframes {uid}{name}{{{kf}}}"
                   f".{uid}{name}{{opacity:{1 if name == 'idle' else 0};animation:{uid}{name} {T}s linear infinite}}")
        body.append(f'<g class="{uid}{name}">{sprite(g, x, y, s, palette)}</g>')
    hx, hy = x + (cols * s) // 2 - 5, y - 4
    body.append(f'<g class="{uid}heart">{sprite(LITTLE_HEART, hx, hy, 2, {"#": PINK})}</g>')
    css.append(f".{uid}heart{{opacity:0;animation:{uid}heart {T}s ease-out infinite}}"
               f"@keyframes {uid}heart{{0%,25%{{opacity:0;transform:translateY(3px)}}28%{{opacity:1}}"
               f"40%,100%{{opacity:0;transform:translateY(-12px)}}}}")
    return "".join(css), "".join(body), cols * s
LITTLE_HEART = [".#.#.", "#####", ".###.", "..#.."]


def apply_theme(name):
    if name not in THEMES:
        sys.exit(f"unknown theme '{name}', pick one of: {', '.join(THEMES)}")
    globals().update(THEMES[name])


# ── drawing helpers ─────────────────────────────────────────────────────────
def pwidth(text, s):
    return max(0, (len(text) * 6 - 1) * s)


def glyph_path(ch, x, y, s):
    rows = FONT.get(ch.upper())
    if rows is None:
        WARN.add(f"pixel font has no glyph for {ch!r}; it was drawn as a space")
        rows = FONT[" "]
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < 5:
            if row[c] == "#":
                start = c
                while c < 5 and row[c] == "#":
                    c += 1
                n = (c - start) * s
                out.append(f"M{x + start * s} {y + r * s}h{n}v{s}h{-n}z")
            else:
                c += 1
    return "".join(out)


def ptext(text, x, y, s):
    return "".join(glyph_path(ch, x + i * 6 * s, y, s) for i, ch in enumerate(text))


def ptext_el(text, x, y, s, fill, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} fill="{fill}" d="{ptext(text, x, y, s)}"/>'


def sprite(rows, x, y, s, palette):
    groups = {}
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch in palette:
                groups.setdefault(ch, []).append(f"M{x + c * s} {y + r * s}h{s}v{s}h{-s}z")
    return "".join(f'<path fill="{palette[k]}" d="{"".join(v)}"/>' for k, v in groups.items())


def stepped(x, y, w, h, p=STEP):
    pts = [
        (x + 2 * p, y), (x + w - 2 * p, y), (x + w - 2 * p, y + p), (x + w - p, y + p),
        (x + w - p, y + 2 * p), (x + w, y + 2 * p), (x + w, y + h - 2 * p), (x + w - p, y + h - 2 * p),
        (x + w - p, y + h - p), (x + w - 2 * p, y + h - p), (x + w - 2 * p, y + h), (x + 2 * p, y + h),
        (x + 2 * p, y + h - p), (x + p, y + h - p), (x + p, y + h - 2 * p), (x, y + h - 2 * p),
        (x, y + 2 * p), (x + p, y + 2 * p), (x + p, y + p), (x + 2 * p, y + p),
    ]
    return "M" + "L".join(f"{a} {b}" for a, b in pts) + "Z"


def panel(w, h, fill, stroke=None):
    return f'<path d="{stepped(1, 1, w - 2, h - 2)}" fill="{fill}" stroke="{stroke or BORDER}" stroke-width="2"/>'


def dots(x1, x2, y, size=4, gap=12, fill=None):
    d = "".join(f"M{x} {y}h{size}v{size}h{-size}z" for x in range(x1, x2 - size + 1, gap))
    return f'<path fill="{fill or BORDER}" d="{d}"/>'


def sans(text, x, y, size, fill, anchor="start", weight="400", length=None):
    fixed = f' textLength="{length}" lengthAdjust="spacingAndGlyphs"' if length else ""
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{SANS}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{fixed}>{escape(text)}</text>')


def svg_doc(w, h, body, label, css="", reduced=""):
    style = f"{css}@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}{reduced}}}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}" shape-rendering="crispEdges">\n'
            f"<title>{escape(label)}</title>\n<style>{style}</style>\n{body}\n</svg>\n")


def fit(text, limit, what):
    if len(text) > limit:
        WARN.add(f"{what} is longer than {limit} characters and was shortened: {text!r}")
        return text[: limit - 1].rstrip() + "…" if what.endswith("(sans)") else text[:limit]
    return text


def logo_mark(x, y, initials, size=52, s=3):
    initials = initials.upper()[:2]
    tw = pwidth(initials, s)
    return (f'<path d="{stepped(x, y, size, size)}" fill="{SURFACE}" stroke="{PINK}" stroke-width="2"/>'
            + ptext_el(initials, x + (size - tw) // 2, y + (size - 7 * s) // 2, s, PINK))


# ── banner ──────────────────────────────────────────────────────────────────
def typing(lines, cy, s=3, slot=7.0):
    """Pixel typewriter: each line types in, rests, then fades softly."""
    n = len(lines)
    N = max(n, 2)
    T = slot * N
    eps = 0.22 / T * 100  # each character fades in over ~0.2s
    css, body = [], []
    for i, raw in enumerate(lines):
        line = "> " + raw.upper()
        L = len(line)
        x0 = (W - pwidth(line, s)) // 2
        y0 = cy - (7 * s) // 2
        sl = 100 / N
        a = sl * i
        te, he, fe, rs = a + sl * 0.40, a + sl * 0.86, a + sl * 0.96, a + sl * 0.99
        dt = (te - a) / 100 * T / L
        css.append(f"@keyframes ln{i}{{0%,{a:.3f}%{{opacity:0}}{a + 0.001:.3f}%,{he:.3f}%{{opacity:1}}"
                   f"{fe:.3f}%,100%{{opacity:0}}}}")
        css.append(f"@keyframes ch{i}{{0%,{a:.3f}%{{opacity:0}}{a + eps:.3f}%,{rs:.3f}%{{opacity:1}}"
                   f"{rs + 0.001:.3f}%,100%{{opacity:0}}}}")
        css.append(f"@keyframes cu{i}{{0%,{a:.3f}%{{transform:translateX(0);animation-timing-function:steps({L},start)}}"
                   f"{te:.3f}%,100%{{transform:translateX({L * 6 * s}px)}}}}")
        chars = []
        for k, ch in enumerate(line):
            d = glyph_path(ch, x0 + k * 6 * s, y0, s)
            if d:
                chars.append(f'<path d="{d}" style="animation:ch{i} {T}s linear {k * dt:.3f}s infinite both"/>')
        body.append(
            f'<g class="ln ln{i}" fill="{SOFT}" style="animation:ln{i} {T}s ease-in-out infinite both">'
            f'{"".join(chars)}'
            f'<g style="animation:cu{i} {T}s infinite both"><rect class="blink" x="{x0}" y="{y0}" '
            f'width="{3 * s}" height="{7 * s}" fill="{PINK}"/></g></g>')
    css.append(".ln{opacity:0}.ln0{opacity:1}.blink{opacity:0;animation:blink 1.6s ease-in-out infinite}"
               "@keyframes blink{0%,100%{opacity:.9}50%{opacity:.15}}")
    return "".join(css), "".join(body)


def banner(p):
    H = 300
    rnd = random.Random(11)
    name = fit(p["name"].upper(), 14, "name")
    css, body = [], []
    body.append(
        f'<defs><clipPath id="clip"><path d="{stepped(1, 1, W - 2, H - 2)}"/></clipPath>'
        f'<pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse">'
        f'<rect x="7" y="7" width="2" height="2" fill="{SURFACE}"/></pattern>'
        f'<radialGradient id="glow"><stop offset="0" stop-color="{PINK}" stop-opacity=".34"/>'
        f'<stop offset=".55" stop-color="{PINK}" stop-opacity=".1"/>'
        f'<stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient></defs>')
    body.append(panel(W, H, BG))
    body.append('<g clip-path="url(#clip)">')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')

    # breathing glow behind the name
    body.append('<ellipse class="glow" cx="400" cy="125" rx="320" ry="105" fill="url(#glow)"/>')
    css.append(".glow{transform-box:fill-box;transform-origin:center;opacity:.6;"
               "animation:breathe 7s ease-in-out infinite}"
               "@keyframes breathe{0%,100%{opacity:.5;transform:scale(.96)}50%{opacity:1;transform:scale(1.04)}}")

    # twinkling stars, kept away from the text
    placed = 0
    while placed < 18:
        x, y = rnd.randrange(20, W - 24, 4), rnd.randrange(16, H - 20, 4)
        if 90 < x < 710 and 64 < y < 250:
            continue
        if (x < 120 or x > 680) and y > 180:  # keep the corner sprites clear
            continue
        sz = rnd.choice([2, 2, 4])
        col = rnd.choice([BLUSH, ACCENT, SOFT])
        body.append(f'<rect class="tw" x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{col}" '
                    f'style="animation-duration:{rnd.uniform(4.5, 8):.1f}s;animation-delay:{-rnd.uniform(0, 8):.1f}s"/>')
        placed += 1
    css.append(".tw{animation:twinkle 6s ease-in-out infinite}@keyframes twinkle{0%,100%{opacity:.15}50%{opacity:.85}}")

    # slowly drifting petals
    for i in range(10):
        x = 34 + i * 76 + rnd.randrange(-14, 14, 2)
        s = rnd.choice([2, 3, 3])
        col = rnd.choice([PINK, SOFT, BLUSH])
        body.append(f'<g transform="translate({x} 0)"><g class="pt {rnd.choice(["fa", "fb"])}" '
                    f'style="animation-duration:{rnd.uniform(16, 24):.1f}s;animation-delay:{-rnd.uniform(0, 24):.1f}s">'
                    f'{sprite(PETAL, 0, 0, s, {"#": col})}</g></g>')
    css.append(".pt{opacity:0;animation-timing-function:ease-in-out;animation-iteration-count:infinite}"
               ".fa{animation-name:fa}.fb{animation-name:fb}"
               "@keyframes fa{0%{transform:translate(0,-20px);opacity:0}12%{opacity:.7}"
               "50%{transform:translate(22px,150px)}88%{opacity:.7}100%{transform:translate(-4px,320px);opacity:0}}"
               "@keyframes fb{0%{transform:translate(0,-20px);opacity:0}12%{opacity:.7}"
               "50%{transform:translate(-22px,150px)}88%{opacity:.7}100%{transform:translate(4px,320px);opacity:0}}")

    # top bar: logo mark + status
    initials = p.get("initials") or "".join(w[0] for w in p["name"].split()[:2])
    body.append(logo_mark(28, 28, initials))
    status = "♥ " + p.get("status", "player 1").upper()
    body.append(ptext_el(status, W - 28 - pwidth(status, 2), 47, 2, MUTED))

    # name with a soft rose drop shadow
    s = 7
    while s > 3 and pwidth(name, s) > 600:
        s -= 1
    nx, ny = (W - pwidth(name, s)) // 2, 118 - (7 * s) // 2
    o = max(2, s // 2)
    body.append(ptext_el(name, nx + o, ny + o, s, ROSE))
    body.append(ptext_el(name, nx, ny, s, PINK))

    role = fit(p["role"].upper(), 40, "role")
    body.append(ptext_el(role, (W - pwidth(role, 2)) // 2, ny + 7 * s + 22, 2, MUTED))

    # typewriter line
    lines = [fit(l, 30, "typing line") for l in p["typing_lines"]] or ["hello, world!"]
    tcss, tbody = typing(lines, cy=226)
    css.append(tcss)
    body.append(tbody)

    # floating cat (bottom right) and a little plant (bottom left)
    cx, cy = W - 30 - 66, H - 30 - 54 - 10
    if p.get("couple"):
        # bottom-right, in the cat's spot: the little animated couple, standing on a soft shadow
        cw = len(COUPLE[0]) * 3
        qx, bottom = W - 30 - cw, cy + 54
        body.append(f'<rect x="{qx + 4}" y="{bottom + 8}" width="{cw - 8}" height="4" fill="{BORDER}"/>')
        ccss, cbody, _ = couple_scene(qx, bottom)
        css.append(ccss)
        body.append(cbody)
    else:
        body.append(f'<rect class="shadow" x="{cx + 8}" y="{cy + 62}" width="50" height="4" fill="{BORDER}"/>')
        body.append(f'<g class="float">{sprite(CAT, cx, cy, 6, {"R": ROSE, "P": BLUSH, "E": BG, "B": PINK})}</g>')
        css.append(".float{animation:float 5s ease-in-out infinite}"
                   "@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}"
                   ".shadow{transform-box:fill-box;transform-origin:center;animation:shadow 5s ease-in-out infinite}"
                   "@keyframes shadow{0%,100%{transform:scaleX(1);opacity:.9}50%{transform:scaleX(.7);opacity:.45}}")
    body.append(sprite(PLANT, 30, H - 30 - 35, 5, {"G": ACCENT, "R": ROSE, "P": SOFT}))

    body.append("</g>")
    label = f"{p['name']}: {p['role']}. " + " / ".join(lines)
    return svg_doc(W, H, "".join(body), label, "".join(css), ".pt{display:none}")


# ── section header ──────────────────────────────────────────────────────────
def header(title):
    H, s = 52, 3
    t = title.upper()
    y = (H - 7 * s) // 2
    body = [panel(W, H, BG), ptext_el("✦", 24, y, s, ACCENT), ptext_el(t, 24 + 6 * s * 2, y, s, PINK)]
    end = 24 + 6 * s * 2 + pwidth(t, s) + 24
    body.append(dots(end, W - 24, H // 2 - 2))
    return svg_doc(W, H, "".join(body), title)


# ── about / character sheet ─────────────────────────────────────────────────
def about_card(p):
    pad, row_h = 28, 34
    rows, meters = p.get("about", []), p.get("meters", [])
    body, top = [], pad
    if p.get("bio"):
        body.append(sans(fit(p["bio"], 92, "bio (sans)"), pad, top + 15, 16, TEXT))
        top += 34
        body.append(dots(pad, W - pad, top, size=4, gap=8))
        top += 24
    css = ""
    ys, y, content_bottom = [], top, top
    for i, (label, value) in enumerate(rows):
        # long values wrap to a second line; rows below the meters can use the full width
        width = 42 if len(ys) < len(meters) else 74
        # "\n" in a value starts a new line on purpose; long lines also wrap on their own
        lines = [l for part in value.split("\n") for l in (textwrap.wrap(part, width) or [""])]
        if len(lines) > 2:
            WARN.add(f"about value for {label!r} was cut to 2 lines")
            lines = lines[:2]
        ys.append(y)
        body.append(ptext_el(fit(label.upper(), 11, "about label"), pad, y, 2, PINK))
        for j, line in enumerate(lines):
            body.append(sans(line, pad + 150, y + 13 + j * 21, 15, TEXT))
        content_bottom = y + 14 + 21 * (len(lines) - 1)
        y += row_h + 21 * (len(lines) - 1)
    mx = 520
    for i, (label, value) in enumerate(meters):
        y = ys[i] if i < len(ys) else top + i * row_h
        content_bottom = max(content_bottom, y + 14)
        body.append(ptext_el(fit(label.upper(), 9, "meter label"), mx, y, 2, MUTED))
        v = max(0, min(10, int(value)))
        on = "".join(f"M{mx + 126 + j * 12} {y}h8v14h-8z" for j in range(v))
        off = "".join(f"M{mx + 126 + j * 12} {y}h8v14h-8z" for j in range(v, 10))
        body.append(f'<path fill="{PINK}" d="{on}"/><path fill="{BORDER}" d="{off}"/>')
    H = content_bottom + pad
    label = (p.get("bio", "") + " " + "; ".join(f"{a}: {b}".replace("\n", " ") for a, b in rows)).strip()
    return svg_doc(W, H, panel(W, H, SURFACE) + "".join(body), label, css)


# ── project card ────────────────────────────────────────────────────────────
def project_card(pr):
    w, h, pad = 390, 184, 22
    title = fit(pr["title"].upper(), 24, "project title")
    body = [panel(w, h, SURFACE), ptext_el(title, pad, pad + 2, 2, PINK),
            ptext_el("✦", w - pad - 10, pad + 2, 2, ACCENT)]
    lines = textwrap.wrap(pr.get("description", ""), 44)
    if len(lines) > 3:
        WARN.add(f"description for {pr['title']!r} was cut to 3 lines")
        lines = lines[:3]
        lines[-1] = lines[-1][:41].rstrip() + "…"
    for i, line in enumerate(lines):
        body.append(sans(line, pad, pad + 48 + i * 21, 14, TEXT))
    x, ty = pad, h - pad - 24
    for tag in pr.get("tags", [])[:4]:
        tw = int(len(tag) * 7 + 20)
        if x + tw > w - pad - 30:
            break
        body.append(f'<path d="{stepped(x, ty, tw, 24, 2)}" fill="{BG}" stroke="{ACCENT}" stroke-width="1.5"/>')
        body.append(sans(tag, x + tw // 2, ty + 16, 12, ACCENT, anchor="middle"))
        x += tw + 8
    body.append(ptext_el(">", w - pad - 10, h - pad - 18, 2, PINK))
    label = f"{pr['title']}: {pr.get('description', '')} ({', '.join(pr.get('tags', []))})"
    return svg_doc(w, h, "".join(body), label)


# ── footer ──────────────────────────────────────────────────────────────────
def footer(p):
    H = 156
    title = p.get("footer_title", "thanks for visiting").upper()
    sub = p.get("footer_subtitle", "press start to connect >").upper()
    line_d = "".join(f"M{x} 26h8v4h-8z" for x in range(28, W - 28 - 7, 12))
    body = [
        f'<defs><clipPath id="ln"><path d="{line_d}"/></clipPath>'
        f'<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="{PINK}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>'
        f"</linearGradient></defs>",
        panel(W, H, BG),
        f'<g clip-path="url(#ln)"><rect width="{W}" height="40" fill="{BORDER}"/>'
        f'<rect class="shimmer" x="-180" y="20" width="180" height="16" fill="url(#sh)"/></g>',
    ]
    s = 3
    tw = pwidth(title, s)
    total = tw + 14 + 7 * s
    tx = (W - total) // 2
    body.append(ptext_el(title, tx, 62, s, PINK))
    body.append(f'<g class="beat">{sprite(HEART, tx + tw + 14, 62, s, {"#": PINK})}</g>')
    body.append(ptext_el(sub, (W - pwidth(sub, 2)) // 2, 104, 2, MUTED))
    initials = p.get("initials") or "".join(w[0] for w in p["name"].split()[:2])
    body.append(f'<g transform="translate({W - 28 - 36} {H - 28 - 36}) scale(.6923)">'
                f'{logo_mark(0, 0, initials)}</g>')
    css = (".shimmer{animation:shimmer 9s ease-in-out infinite}"
           "@keyframes shimmer{0%{transform:translateX(0)}70%,100%{transform:translateX(1160px)}}"
           ".beat{transform-box:fill-box;transform-origin:center;animation:beat 3.2s ease-in-out infinite}"
           "@keyframes beat{0%,100%{transform:scale(1)}50%{transform:scale(1.18)}}")
    return svg_doc(W, H, "".join(body), f"{p.get('footer_title', '')}. {p.get('footer_subtitle', '')}", css)


STATS_QUERY = """query($login: String!) { user(login: $login) {
  followers { totalCount }
  pullRequests { totalCount }
  issues { totalCount }
  repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
    totalCount nodes { stargazerCount } }
  contributionsCollection { totalCommitContributions restrictedContributionsCount }
} }"""


def fetch_stats(login, token):
    import urllib.request
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": STATS_QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "pastel-pixel-profile"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors") or not data.get("data", {}).get("user"):
        sys.exit(f"github api error: {data.get('errors')}")
    u = data["data"]["user"]
    cc = u["contributionsCollection"]
    return [
        ("commits", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("stars", sum(n["stargazerCount"] for n in u["repositories"]["nodes"])),
        ("prs", u["pullRequests"]["totalCount"]),
        ("repos", u["repositories"]["totalCount"]),
        ("issues", u["issues"]["totalCount"]),
        ("followers", u["followers"]["totalCount"]),
    ]


def stats_card(stats, w=495, h=195):
    """On-brand stats card. Built daily by the GitHub Action, so no third-party service is needed."""
    body = [panel(w, h, SURFACE), ptext_el("✦", 28, 26, 2, ACCENT), ptext_el("BATTLE STATS", 52, 26, 2, PINK)]
    cols = [28, 262]
    for i, (label, value) in enumerate(stats):
        x, y = cols[i % 2], 60 + (i // 2) * 36
        val = f"{value:,}" if value < 100000 else f"{value // 1000}K"
        body.append(ptext_el(label.upper(), x, y + 4, 2, MUTED))
        body.append(ptext_el(val, x + 205 - pwidth(val, 3), y, 3, PINK))
        if i // 2 < 2:
            body.append(dots(x, x + 205, y + 27, size=2, gap=6))
    body.append(sans("commits counted over the past year · refreshed daily", 28, h - 14, 11, MUTED))
    return svg_doc(w, h, "".join(body), "github stats: " + ", ".join(f"{v} {k}" for k, v in stats))


def mock_card(title, w=495, h=195):
    body = [panel(w, h, SURFACE), ptext_el(title.upper(), 28, 32, 2, PINK),
            sans("this appears on github once the", 28, 80, 15, TEXT),
            sans("\"generate pink snake\" action has run", 28, 102, 15, TEXT),
            dots(28, w - 28, h - 30, size=4, gap=8)]
    return svg_doc(w, h, "".join(body), title)


# ── README ──────────────────────────────────────────────────────────────────
def badge(label, logo):
    lab = urllib.parse.quote(label.replace("-", "--").replace("_", "__"))
    url = f"https://img.shields.io/badge/{lab}-{SURFACE[1:]}?style=for-the-badge"
    if logo:
        url += f"&logo={urllib.parse.quote(logo)}&logoColor={PINK[1:]}"
    return url


def img(src, alt, width="100%"):
    return f'<img src="{escape(src)}" width="{width}" alt="{escape(alt)}">'


def readme(p, for_preview=False):
    u = p["username"]
    placeholder = u in ("", "your-username")
    q = urllib.parse.urlencode
    mock = for_preview and placeholder
    output = f"https://raw.githubusercontent.com/{u}/{u}/output"

    def head(slug, title):
        return f'<p align="center">{img(f"assets/header-{slug}.svg", title)}</p>'

    out = ["<!-- generated by build.py from profile.json; edit that file and re-run instead of editing here -->",
           f'<p align="center">{img("assets/banner.svg", p["name"] + ": " + p["role"])}</p>',
           head("about", "about me"),
           f'<p align="center">{img("assets/about.svg", "character sheet: " + p.get("bio", ""))}</p>',
           head("inventory", "inventory: tech stack"),
           '<p align="center">\n' + "\n".join(img(badge(t["name"], t.get("logo", "")), t["name"], "")
                                            .replace(' width=""', "") for t in p["stack"]) + "\n</p>"]

    if p.get("projects"):
        out.append(head("quests", "quests: featured projects"))
        cards = [f'<a href="{escape(pr["url"])}">{img(f"assets/project-{i + 1}.svg", pr["title"], "49%")}</a>'
                 for i, pr in enumerate(p["projects"])]
        for i in range(0, len(cards), 2):
            out.append('<p align="center">\n' + "\n".join(cards[i:i + 2]) + "\n</p>")

    if p.get("show_stats") or p.get("show_streak") or p.get("show_snake"):
        out.append(head("stats", "battle log: github stats"))
        row = []
        if p.get("show_stats"):
            if for_preview:
                src = "preview/stats.svg" if (PREVIEW / "stats.svg").exists() else "preview/mock-stats.svg"
            else:
                src = f"{output}/stats.svg"
            row.append(img(src, "github stats", "49%"))
        if p.get("show_streak"):
            streak = dict(user=u, background=SURFACE[1:], border=BORDER[1:], stroke=BORDER[1:], ring=PINK[1:],
                          fire=PINK[1:], currStreakNum=PINK[1:], sideNums=TEXT[1:], currStreakLabel=PINK[1:],
                          sideLabels=MUTED[1:], dates=MUTED[1:], border_radius="0")
            src = "preview/mock-streak.svg" if mock else f"https://streak-stats.demolab.com/?{q(streak)}"
            row.append(img(src, "contribution streak", "49%"))
        if row:
            out.append('<p align="center">\n' + "\n".join(row) + "\n</p>")
        if p.get("show_snake"):
            src = "preview/mock-snake.svg" if for_preview else f"{output}/snake-pink.svg"
            out.append(f'<p align="center">{img(src, "contribution graph being eaten by a pink pixel snake")}</p>')

    if p.get("links"):
        out.append(head("save-point", "save point: say hi"))
        out.append('<p align="center">\n' + "\n".join(
            f'<a href="{escape(l["url"])}">{img(badge(l["label"], l.get("logo", "")), l["label"], "")}</a>'
            .replace(' width=""', "") for l in p["links"]) + "\n</p>")

    out.append(f'<p align="center">{img("assets/footer.svg", p.get("footer_title", "thanks for visiting"))}</p>')
    return "\n\n".join(out) + "\n"


PREVIEW_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Profile Preview</title>
<style>
:root{--page:#0d1117;--ink:#e6edf3;--line:#30363d}
body{margin:0;background:var(--page);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;transition:background .3s}
body.light{--page:#ffffff;--ink:#1f2328;--line:#d1d9e0}
.bar{display:flex;gap:12px;align-items:center;justify-content:space-between;max-width:790px;margin:20px auto 0;padding:0 16px;font-size:13px;opacity:.8}
button{font:inherit;background:transparent;color:inherit;border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.box{max-width:790px;margin:12px auto 40px;border:1px solid var(--line);border-radius:6px;padding:24px;box-sizing:border-box}
@media (max-width:820px){.box{margin:12px 16px 40px}}
.box p{margin:0 0 16px}.box img{max-width:100%;vertical-align:middle}
</style></head><body>
<div class="bar"><span>local preview of README.md</span><button id="t">show on GitHub light mode</button></div>
<div class="box">
__README__
</div>
<script>
document.getElementById('t').onclick=function(){var l=document.body.classList.toggle('light');this.textContent=l?'show on GitHub dark mode':'show on GitHub light mode'};
</script>
</body></html>
"""

WORKFLOW = """name: generate pink snake

on:
  schedule:
    - cron: "0 0 * * *"   # once a day
  workflow_dispatch:       # lets you run it by hand from the Actions tab
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - name: generate stats card
        run: python3 build.py --stats dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: generate snake svg
        uses: Platane/snk@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/snake-pink.svg?color_snake=__SNAKE__&color_dots=__DOTS__

      - name: push to the output branch
        uses: crazy-max/ghaction-github-pages@v4
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


def main():
    p = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
    apply_theme(p.get("theme", "pink"))

    if len(sys.argv) == 3 and sys.argv[1] == "--stats":
        # used by the GitHub Action (and for local previews): python3 build.py --stats <dir>
        import os
        token = os.environ.get("GITHUB_TOKEN") or sys.exit("set GITHUB_TOKEN to build the stats card")
        out = Path(sys.argv[2])
        out.mkdir(parents=True, exist_ok=True)
        (out / "stats.svg").write_text(stats_card(fetch_stats(p["username"], token)), encoding="utf-8")
        print(f"wrote {out / 'stats.svg'}")
        return

    for old in list(ASSETS.glob("*.svg")) + list(PREVIEW.glob("mock-*.svg")):
        old.unlink()

    files = [write("assets/banner.svg", banner(p)), write("assets/about.svg", about_card(p)),
             write("assets/footer.svg", footer(p))]
    for slug, title in [("about", "about me"), ("inventory", "inventory"), ("quests", "quests"),
                        ("stats", "battle log"), ("save-point", "save point")]:
        files.append(write(f"assets/header-{slug}.svg", header(title)))
    for i, pr in enumerate(p.get("projects", [])):
        files.append(write(f"assets/project-{i + 1}.svg", project_card(pr)))

    files.append(write("README.md", readme(p)))
    dots_ramp = ",".join([SURFACE, "#4A3358", "#7E4F7A", ROSE, PINK])
    files.append(write(".github/workflows/snake.yml",
                       WORKFLOW.replace("__SNAKE__", PINK).replace("__DOTS__", dots_ramp)))

    write("preview/mock-stats.svg", mock_card("github stats"))
    write("preview/mock-streak.svg", mock_card("streak"))
    write("preview/mock-snake.svg", mock_card("contribution snake", W, 160))
    write("preview.html", PREVIEW_HTML.replace("__README__", readme(p, for_preview=True)))

    print("built:\n  " + "\n  ".join(files) + "\n  preview.html (local only, don't commit)")
    for w in sorted(WARN):
        print("note:", w)
    if p["username"] in ("", "your-username"):
        print("note: set \"username\" in profile.json so the stats, streak and snake load")


if __name__ == "__main__":
    main()
