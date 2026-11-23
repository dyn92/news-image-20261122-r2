#!/usr/bin/env python3
"""news-image-20261122 round 2: one image summing up the world news of
Sunday 22 November 2026. Pure Python standard library only.

Draws a deterministic 1024x1024 newspaper front page: a masthead naming
the day, then six panels, each with a pictogram, a headline and a short
factual summary of one verified story from 22 November 2026. The PNG is
encoded by hand (zlib + struct) so the output is byte-for-byte identical
on every run. No network, no files read, no randomness, no clock.
"""

import hashlib
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, one row per string, "#" = ink. Uppercase + digits +
# the punctuation the poster text needs. All poster text is uppercase.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}

BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def text_width(text, scale):
    """Pixel width of text at the given font scale (6 px advance/char)."""
    return len(text) * 6 * scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        """Filled disc."""
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=2):
        """Disc outline of given thickness."""
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 <= d2 <= (r + thick) ** 2:
                    self.set(xx, yy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        """Ellipse outline, one pixel thick."""
        for t in range(0, 360):
            import math
            a = math.radians(t)
            x = int(cx + rx * math.cos(a))
            y = int(cy + ry * math.sin(a))
            self.set(x, y, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle via scanline fill."""
        ys = sorted([y0, y1, y2])
        for y in range(ys[0], ys[2] + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1),
                                     (x1, y1, x2, y2),
                                     (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by):
                    xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for x in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(x, y, color)

    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch, BLANK)
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    self.rect(x + c * scale, y + r * scale,
                              scale, scale, color)

    def text(self, x, y, s, scale, color):
        # The bitmap font covers uppercase only; fold case here so no
        # lowercase letter ever renders blank.
        s = s.upper()
        for i, ch in enumerate(s):
            self.glyph(x + i * 6 * scale, y, ch, scale, color)

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns list of lines fitting max_w pixels."""
        words = s.split(" ")
        lines, cur = [], ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- PNG
def encode_png(canvas):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 6)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- palette
PAPER = bytes([250, 247, 240])
INK = bytes([24, 24, 28])
MUTED = bytes([90, 88, 84])
RULE = bytes([24, 24, 28])
LIGHT = bytes([238, 233, 224])
WHITE = bytes([255, 255, 255])
RED = bytes([178, 34, 34])
BLUE = bytes([28, 68, 140])
GREEN = bytes([26, 110, 70])
ORANGE = bytes([204, 102, 0])
TEAL = bytes([0, 120, 120])
PURPLE = bytes([96, 56, 140])

# ---------------------------------------------------------------- pictograms
# Each draws a simple flat pictogram inside a box (x, y, w, h).

def pic_climate(cv, x, y, w, h):
    # Globe with a crack: the climate talks broke down.
    cx, cy, r = x + w // 2, y + h // 2, 40
    cv.disc(cx, cy, r, TEAL)
    cv.ring(cx, cy, r, INK, 3)
    cv.ellipse(cx, cy, r, r // 2, WHITE)
    cv.vline(cx, cy - r, 2 * r, WHITE, 2)
    cv.line(cx - r + 8, cy - 26, cx + 6, cy - 4, RED)
    cv.line(cx + 6, cy - 4, cx - 4, cy + 12, RED)
    cv.line(cx - 4, cy + 12, cx + 12, cy + 30, RED)
    cv.line(cx - r - 14, cy - r - 6, cx - r + 14, cy - r + 6, RED)
    cv.line(cx - r - 14, cy - r + 6, cx - r + 14, cy - r - 6, RED)


def pic_ship(cv, x, y, w, h):
    # Warship at anchor, hit: smoke and a blast star above the deck.
    cx, cy = x + w // 2, y + h // 2 + 24
    cv.rect(cx - 78, cy - 6, 156, 22, INK)          # hull
    cv.triangle(cx - 78, cy - 6, cx - 52, cy - 6, cx - 78, cy + 16, INK)
    cv.rect(cx - 30, cy - 30, 46, 24, INK)          # superstructure
    cv.vline(cx + 4, cy - 52, 24, INK, 4)           # mast
    cv.disc(cx - 12, cy - 62, 9, ORANGE)           # blast
    cv.disc(cx - 26, cy - 52, 6, RED)
    cv.disc(cx + 2, cy - 56, 6, RED)
    cv.disc(cx - 44, cy - 52, 7, MUTED)            # smoke
    cv.disc(cx - 58, cy - 62, 6, MUTED)


def pic_building(cv, x, y, w, h):
    # Apartment block, one corner collapsed, dust cloud at the base.
    bx, by = x + w // 2 - 52, y + 2
    cv.rect(bx, by, 104, 84, BLUE)
    cv.triangle(bx + 52, by + 40, bx + 104, by + 40, bx + 104, by + 84, RED)
    cv.triangle(bx + 52, by + 40, bx + 78, by + 84, bx + 104, by + 84, INK)
    for row in range(3):
        for col in range(4):
            wx = bx + 10 + col * 24
            wy = by + 10 + row * 22
            if row == 2 and col >= 2:
                continue
            cv.rect(wx, wy, 12, 12, WHITE)
    cv.disc(bx + 88, by + 88, 12, MUTED)
    cv.disc(bx + 104, by + 92, 9, MUTED)
    cv.disc(bx + 66, by + 94, 7, MUTED)


def pic_capitol(cv, x, y, w, h):
    # Capitol dome; the 258 seats are in the headline below.
    cx, cy = x + w // 2, y + h // 2 + 16
    cv.rect(cx - 66, cy + 6, 132, 10, INK)          # base
    for i in range(5):
        cv.vline(cx - 56 + i * 28, cy - 26, 32, INK, 5)
    cv.rect(cx - 66, cy - 26, 132, 8, INK)
    cv.disc(cx, cy - 26, 34, BLUE)                 # dome
    cv.rect(cx - 34, cy - 26, 68, 10, BLUE)
    cv.vline(cx, cy - 56, 16, INK, 4)              # spire
    cv.disc(cx, cy - 58, 3, RED)


def pic_mercury(cv, x, y, w, h):
    # Mercury with its orbit ring and the twin BepiColombo craft.
    cx, cy = x + w // 2, y + h // 2
    cv.ellipse(cx, cy, 78, 30, TEAL)
    cv.disc(cx, cy, 34, ORANGE)
    cv.ring(cx, cy, 34, INK, 2)
    cv.disc(cx - 12, cy - 8, 6, bytes([170, 90, 0]))
    cv.disc(cx + 10, cy + 10, 5, bytes([170, 90, 0]))
    cv.disc(cx + 14, cy - 14, 4, bytes([170, 90, 0]))
    sx, sy = cx + 66, cy - 22
    cv.rect(sx - 18, sy - 4, 12, 8, INK)           # solar panel
    cv.rect(sx + 6, sy - 4, 12, 8, INK)
    cv.rect(sx - 6, sy - 6, 12, 12, BLUE)          # craft body
    cv.disc(sx, sy, 3, RED)


def pic_fire(cv, x, y, w, h):
    # Factory with a sawtooth roof, flames and smoke.
    fx, fy = x + w // 2 - 70, y + h // 2 + 14
    cv.rect(fx, fy - 10, 140, 40, INK)
    cv.triangle(fx, fy - 10, fx + 28, fy - 34, fx + 56, fy - 10, INK)
    cv.triangle(fx + 56, fy - 10, fx + 84, fy - 34, fx + 112, fy - 10, INK)
    cv.triangle(fx + 112, fy - 10, fx + 140, fy - 34, fx + 140, fy - 10, INK)
    cv.rect(fx + 8, fy + 12, 20, 20, ORANGE)
    cv.rect(fx + 44, fy + 12, 20, 20, WHITE)
    cv.rect(fx + 80, fy + 12, 20, 20, WHITE)
    cv.triangle(fx + 20, fy - 44, fx + 34, fy - 62, fx + 48, fy - 44, ORANGE)
    cv.triangle(fx + 34, fy - 40, fx + 44, fy - 56, fx + 56, fy - 40, RED)
    cv.disc(fx + 118, fy - 40, 8, MUTED)
    cv.disc(fx + 128, fy - 52, 6, MUTED)


# ---------------------------------------------------------------- stories
# All six stories happened, or were first reported, on Sunday 22 November
# 2026. Facts checked against Reuters, AP, BBC and One Turn coverage of
# that day. Every panel names its place and its sources.
STORIES = [
    dict(
        kicker="CLIMATE - ANTALYA, TURKEY",
        color=GREEN,
        pic=pic_climate,
        headline="COP31 ENDS WITH NO DEAL",
        body=("UN climate talks close two days late with no agreement: "
              "the EU and others reject a final text that drops all "
              "mention of fossil fuels."),
        source="REUTERS / AP - 22 NOV 2026",
    ),
    dict(
        kicker="CONFLICT - BENGHAZI, LIBYA",
        color=RED,
        pic=pic_ship,
        headline="RUSSIAN WARSHIP HIT IN PORT",
        body=("A suspected Ukrainian drone strikes a Russian warship "
              "docked at Benghazi; a second vessel is reported hit "
              "in the same attack."),
        source="BBC / ONE TURN - 22 NOV 2026",
    ),
    dict(
        kicker="WAR - DYMER, UKRAINE",
        color=BLUE,
        pic=pic_building,
        headline="DRONE HITS KYIV FLATS",
        body=("A Russian drone partly collapses a five-storey apartment "
              "block north of Kyiv: three people killed and fourteen "
              "missing under the rubble."),
        source="AP - 22 NOV 2026",
    ),
    dict(
        kicker="POLITICS - WASHINGTON, USA",
        color=PURPLE,
        pic=pic_capitol,
        headline="DEMOCRATS TAKE 258 SEATS",
        body=("Chuck Hubbard beats Virginia Foxx in North Carolina, "
              "giving Democrats at least 258 House seats - the largest "
              "majority of any party since 1992."),
        source="AP / REUTERS - 22 NOV 2026",
    ),
    dict(
        kicker="SPACE - MERCURY ORBIT",
        color=TEAL,
        pic=pic_mercury,
        headline="PROBE REACHES MERCURY",
        body=("After an eight-year cruise, the European-Japanese "
              "BepiColombo slips into orbit around Mercury; a thruster "
              "glitch is reported, but the craft is safe."),
        source="REUTERS / AP - 22 NOV 2026",
    ),
    dict(
        kicker="DISASTER - BANTEN, INDONESIA",
        color=ORANGE,
        pic=pic_fire,
        headline="FACTORY FIRE: 3 DEAD, DOZENS MISSING",
        body=("A candy factory fire in Banten kills three workers; "
              "rescuers search for 34 missing and recover remains "
              "in 24 body bags."),
        source="AP - 22 NOV 2026",
    ),
]

# ---------------------------------------------------------------- layout
PANEL_W, PANEL_H = 476, 272
PANEL_X = (24, 524)
PANEL_Y = (140, 426, 712)


def draw_panel(cv, x, y, story):
    # Border.
    cv.rect(x, y, PANEL_W, 2, INK)
    cv.rect(x, y + PANEL_H - 2, PANEL_W, 2, INK)
    cv.rect(x, y, 2, PANEL_H, INK)
    cv.rect(x + PANEL_W - 2, y, 2, PANEL_H, INK)
    # Kicker bar with place tag.
    cv.rect(x, y, PANEL_W, 30, story["color"])
    cv.text(x + 12, y + 8, story["kicker"], 2, WHITE)
    # Pictogram band.
    cv.rect(x, y + 30, PANEL_W, 96, LIGHT)
    story["pic"](cv, x, y + 30, PANEL_W, 96)
    # Headline, up to two lines.
    for i, line in enumerate(cv.wrap(story["headline"], 448, 3)[:2]):
        cv.text(x + 14, y + 134 + i * 25, line, 3, INK)
    # Body, up to four lines.
    for i, line in enumerate(cv.wrap(story["body"], 448, 2)[:4]):
        cv.text(x + 14, y + 186 + i * 16, line, 2, INK)
    # Source line.
    cv.text(x + 14, y + 256, story["source"], 1, MUTED)


def build():
    cv = Canvas(W, H, PAPER)
    # Masthead.
    cv.text_center(W // 2, 14, "THE WORLD IN ONE IMAGE", 4, INK)
    cv.text_center(W // 2, 52, "SUNDAY 22 NOVEMBER 2026", 2, RED)
    cv.hline(24, 88, W - 48, RULE, 3)
    cv.text_center(W // 2, 98,
                   "SIX STORIES FROM AROUND THE GLOBE - ALL FROM ONE DAY",
                   2, INK)
    cv.hline(24, 124, W - 48, RULE, 3)
    # Six panels, two columns by three rows.
    for i, story in enumerate(STORIES):
        draw_panel(cv, PANEL_X[i % 2], PANEL_Y[i // 2], story)
    # Footer: the date promise, in the image itself.
    cv.text_center(W // 2, 992,
                   "ALL SIX STORIES HAPPENED OR WERE FIRST REPORTED ON "
                   "22 NOVEMBER 2026.", 2, MUTED)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes) sha256=%s"
          % (path, len(png), hashlib.sha256(png).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
