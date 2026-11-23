#!/usr/bin/env python3
"""news-image-20261122 (heru1933) — "One Day, Everywhere", Sunday 22 November 2026.
Magazine-style front page. Pure stdlib PNG renderer (no Pillow). 1024x1024.
35 stories, all verified and dated/reported 22 Nov 2026 (see NEWS22-V3.md).
Writes entry.png to MAKEFUN_OUTPUT_DIR when set, else local output/ dir.
"""
import hashlib
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 248, 242)
INK = (16, 16, 16)
INK_SOFT = (64, 62, 56)
GREY = (128, 124, 114)
LINE = (196, 188, 172)
NAVY = (14, 32, 58)
NAVY_LT = (28, 58, 96)
TEAL = (12, 92, 88)
RED = (176, 32, 26)
GOLD = (172, 128, 28)
CREAM = (240, 230, 206)
SKY = (206, 222, 232)
WHITE = (255, 255, 255)
BLACK = (8, 8, 8)

REGION_COLORS = {
    "EUROPE": (24, 64, 120),
    "MIDDLE EAST": (176, 32, 26),
    "ASIA": (12, 92, 88),
    "AFRICA": (172, 128, 28),
    "AMERICAS": (96, 48, 120),
    "OCEANIA": (32, 120, 96),
    "GLOBAL": (64, 62, 56),
}

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, 5 bits (bit 4 = leftmost pixel).
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "a": (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    "b": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    "c": (0x00, 0x00, 0x0E, 0x10, 0x10, 0x10, 0x0E),
    "d": (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    "e": (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    "f": (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    "g": (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "h": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "i": (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    "j": (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    "k": (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    "n": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "o": (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    "p": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10),
    "q": (0x00, 0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01),
    "r": (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    "s": (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    "t": (0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06),
    "u": (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    "v": (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "w": (0x00, 0x00, 0x11, 0x11, 0x15, 0x15, 0x0A),
    "x": (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    "y": (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "z": (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x06, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "–": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "—": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "·": (0x00, 0x00, 0x00, 0x0C, 0x0C, 0x00, 0x00),
    "•": (0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "₦": (0x11, 0x1F, 0x15, 0x1F, 0x15, 0x11, 0x11),
    "’": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "‘": (0x08, 0x04, 0x04, 0x00, 0x00, 0x00, 0x00),
    "“": (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "”": (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "×": (0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x00),
    "▲": (0x04, 0x0E, 0x1F, 0x04, 0x04, 0x04, 0x04),
    "●": (0x00, 0x0E, 0x1F, 0x1F, 0x1F, 0x0E, 0x00),
    "◆": (0x04, 0x0A, 0x11, 0x1F, 0x11, 0x0A, 0x04),
    "★": (0x04, 0x15, 0x1F, 0x0E, 0x04, 0x04, 0x04),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def disc_outline(self, cx, cy, r, c):
        for a in range(360):
            import math
            x = int(cx + r * math.cos(math.radians(a)))
            y = int(cy + r * math.sin(math.radians(a)))
            self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns list of lines."""
        words = s.split()
        lines = []
        cur = ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, max_w, c, lh):
        lines = self.wrap(s, scale, max_w)
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, scale, c)
        return y + len(lines) * lh


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", comp)
        + chunk(b"IEND", b"")
    )

# ---------------------------------------------------------------- stories
# All verified, dated/reported Sunday 22 November 2026. Source per story.
# (title, deck, source, region)
HERO = (
    "COP31 COLLAPSES",
    "UN climate talks in Antalya end with no deal after the EU and others reject the final text. The fossil-fuel mention was the breaking point.",
    "REUTERS",
    "GLOBAL",
)
SECOND = [
    (
        "IRAN STRIKES US BASES IN BAHRAIN",
        "IRGC missiles and drones hit US positions at Al-Riffa and Awali; a civilian facility burns, 2 injured.",
        "REUTERS / XINHUA",
        "MIDDLE EAST",
    ),
    (
        "'EL CHAPO ISIDRO' CAPTURED",
        "Mexican special forces arrest the cartel boss in Sinaloa. 11 killed in the raid, including 4 soldiers.",
        "AP",
        "AMERICAS",
    ),
]
MEDIUMS = [
    ("KRYVYI RIH HIT", "Russian missile kills a boy, 7, and a woman, 20; 60 wounded. A boy is pulled alive from the rubble.", "BBC", "EUROPE"),
    ("BALTIC SHIP TOWED AWAY", "Russian cargo ship Sparta II towed out of Finnish waters after a suspected Ukrainian drone strike set it on fire.", "BBC", "EUROPE"),
    ("THREE MISSILES OVER POLAND", "All three objects that flew into Polish airspace on Friday were Russian Kh-101 missiles, prosecutors say.", "REUTERS", "EUROPE"),
    ("GAZA FOOD VAN HIT", "Israeli strike on a van carrying food aid in Gaza City kills three. Papers bore a World Central Kitchen logo; WCK says it was not its vehicle.", "REUTERS", "MIDDLE EAST"),
    ("FACTORY FIRE KILLS THREE", "Fire at a candy factory in Cikande, Indonesia; 3 dead, 36 missing.", "AP", "ASIA"),
    ("MINISTER RESIGNS OVER AI EXAMS", "South Korea's education minister Choi Kyo-jin quits after late rule changes to catch AI cheating caused chaos in the college entrance exam.", "REUTERS", "ASIA"),
    ("QUAKE SHAKES JAPAN", "5.7-magnitude quake hits central Japan at 1:04 a.m.; 22 injured, windows shattered, trains disrupted in Aichi and Shizuoka.", "JMA", "ASIA"),
    ("BAYELSA BOAT TOLL 29", "Wooden boat carrying mourners capsizes in Bayelsa, Nigeria; at least 29 dead, 50+ in hospital.", "PUNCH", "AFRICA"),
    ("DEMOCRATS TAKE 258 SEATS", "Democrats win their largest House majority since 1992 after flipping a North Carolina seat.", "AP", "AMERICAS"),
    ("VERSTAPPEN WINS VEGAS", "Max Verstappen wins the Las Vegas Grand Prix, his third in four years and 75th career win, as the Ferraris collide.", "BBC", "AMERICAS"),
]
LIST = [
    ("BURNHAM'S EU DEAL", "BBC", "EUROPE"),
    ("UK TO HOST 2035 WOMEN'S WORLD CUP", "BBC", "EUROPE"),
    ("CO-OP LIVE EVACUATED", "BBC", "EUROPE"),
    ("ALCARAZ WINS ATP FINALS", "ATP", "EUROPE"),
    ("PRICE WINS GRAND SLAM", "BBC", "EUROPE"),
    ("TWO DIE OF WOUNDS IN GAZA", "WAFA", "MIDDLE EAST"),
    ("TWO TANKERS HIT OFF HORMUZ", "UKMTO", "MIDDLE EAST"),
    ("EISENKOT CONDEMNS ARSON", "REUTERS", "MIDDLE EAST"),
    ("CENTCOM: F-16 CLAIM 'FALSE'", "CENTCOM", "MIDDLE EAST"),
    ("PAKISTAN TAKE TEST SERIES", "ESPNCRICINFO", "ASIA"),
    ("HONG KONG OPEN", "BWF", "ASIA"),
    ("INDIA SEAL HOCKEY SERIES", "THE HINDU", "ASIA"),
    ("THREE KILLED IN GOMBE", "PEN AGENCY", "AFRICA"),
    ("NAIRA NEARS 1,400", "PEN AGENCY", "AFRICA"),
    ("IOWA EXPLOSIVES DEFIANCE", "BBC", "AMERICAS"),
    ("FBI DATABASE HACK PROBE", "BBC", "AMERICAS"),
    ("SPY CHIEF CONFIRMS PROBE", "ABC", "AMERICAS"),
    ("BESSENT WARNS THE FED", "CBS", "AMERICAS"),
    ("US INFLUENCE FALLS IN ASIA", "AAP", "OCEANIA"),
    ("PANT 128 IN WELLINGTON", "THE HINDU", "OCEANIA"),
    ("BITCOIN HOLDS $60,800", "REUTERS", "GLOBAL"),
    ("S&P 500 DOWN 11.6%", "REUTERS", "GLOBAL"),
]
STATS = [
    ("35", "STORIES"),
    ("7", "REGIONS"),
    ("$60,800", "BITCOIN"),
    ("11", "KILLED · SINALOA"),
    ("29", "DEAD · BAYELSA"),
    ("258", "DEM SEATS"),
]

# ---------------------------------------------------------------- illustration helpers
def draw_globe(cv, cx, cy, r):
    """Stylised globe: sky disc, land blobs, latitude lines."""
    cv.circle(cx, cy, r, SKY)
    cv.disc_outline(cx, cy, r, NAVY)
    # land blobs (abstract continents)
    cv.circle(cx - r // 3, cy - r // 4, r // 3, (214, 198, 158))
    cv.circle(cx + r // 4, cy + r // 5, r // 4, (214, 198, 158))
    cv.circle(cx + r // 8, cy - r // 2, r // 5, (214, 198, 158))
    # latitude lines
    for dy in (-r // 2, 0, r // 2):
        cv.hline(cx - r + 6, cy + dy, 2 * r - 12, (180, 200, 214))
    # thermometer bar
    bx = cx + r + 18
    cv.rect(bx, cy - r + 10, 10, 2 * r - 20, RED)
    cv.rect(bx - 2, cy - r + 10, 14, 8, RED)
    cv.circle(bx + 5, cy + r - 6, 12, RED)
    cv.circle(bx + 5, cy + r - 6, 6, WHITE)


def draw_missile(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    # radar arcs
    for r in (18, 30, 42):
        cv.disc_outline(x + w // 2, y + h - 8, r, NAVY)
    # missile streak
    cv.rect(x + 12, y + 14, w - 24, 4, RED)
    cv.rect(x + 12, y + 26, w - 40, 4, RED)
    cv.text(x + 12, y + h - 22, "KH-101", 2, NAVY)


def draw_badge(cv, x, y, w, h):
    cv.rect(x, y, w, h, GOLD)
    cv.rect(x + 4, y + 4, w - 8, h - 8, NAVY)
    cv.text(x + 14, y + h // 2 - 7, "AP", 3, GOLD)


# ---------------------------------------------------------------- layout
def render():
    cv = Canvas(W, H, PAPER)
    M = 28  # margin
    # --- masthead band (navy) ---
    cv.rect(0, 0, W, 104, NAVY)
    cv.text(M, 14, "THE WORLD", 6, WHITE)
    cv.text(M, 56, "ONE DAY, EVERYWHERE", 3, (200, 210, 224))
    date_s = "SUNDAY 22 NOVEMBER 2026"
    dw = cv.text_w(date_s, 3)
    cv.text(W - M - dw, 16, date_s, 3, WHITE)
    cv.text(W - M - cv.text_w("35 STORIES · 7 REGIONS", 2), 52, "35 STORIES · 7 REGIONS", 2, (200, 210, 224))
    cv.rect(0, 104, W, 4, RED)

    # --- hero feature (COP31) ---
    hy = 120
    cv.text(M, hy, "THE LEAD", 2, RED)
    cv.hline(M, hy + 20, W - 2 * M, LINE)
    ix, iy, iw, ih = M, hy + 30, 260, 158
    cv.rect(ix, iy, iw, ih, SKY)
    draw_globe(cv, ix + 105, iy + 74, 58)
    cv.text(ix + 8, iy + ih - 24, "ANTALYA · NO DEAL", 2, NAVY)
    tx = ix + iw + 22
    tw = W - M - tx
    y = iy + 2
    y = cv.para(tx, y, HERO[0], 4, tw, INK, 34)
    y += 4
    y = cv.para(tx, y, HERO[1], 2, tw, INK_SOFT, 20)
    y += 8
    cv.rect(tx, y, 120, 22, RED)
    cv.text(tx + 10, y + 4, "GLOBAL · CLIMATE", 2, WHITE)
    cv.text(tx + 132, y + 4, "SOURCE: " + HERO[2], 2, GREY)

    # --- second row: two mediums side by side ---
    sy = hy + 30 + ih + 14
    col_w = (W - 2 * M - 20) // 2
    for i, (t, d, src, reg) in enumerate(SECOND):
        x = M + i * (col_w + 20)
        cv.rect(x, sy, col_w, 3, REGION_COLORS[reg])
        y = sy + 10
        y = cv.para(x, y, t, 3, col_w, INK, 26)
        y += 2
        y = cv.para(x, y, d, 2, col_w, INK_SOFT, 18)
        y += 4
        cv.text(x, y, reg + "  ·  SOURCE: " + src, 2, GREY)
    dy = sy + 124
    cv.hline(M, dy, W - 2 * M, LINE)

    # --- medium grid: 2 columns x 5 rows ---
    gy = dy + 10
    cv.text(M, gy, "THE DAY IN FULL", 2, RED)
    gy += 20
    row_h = 52
    for i, (t, d, src, reg) in enumerate(MEDIUMS):
        col = i % 2
        row = i // 2
        x = M + col * (col_w + 20)
        y = gy + row * row_h
        cv.rect(x, y + 2, 6, 6, REGION_COLORS[reg])
        y = cv.para(x + 14, y, t, 2, col_w - 14, INK, 16)
        y = cv.para(x + 14, y, d, 1, col_w - 14, INK_SOFT, 11)
        cv.text(x + 14, y + 1, "SOURCE: " + src, 1, GREY)

    # --- list section: two columns ---
    ly = gy + 5 * row_h + 10
    cv.hline(M, ly, W - 2 * M, LINE)
    ly += 10
    cv.text(M, ly, "ALSO TODAY — 22 STORIES IN BRIEF", 2, RED)
    ly += 20
    per_col = 11
    for i, (t, src, reg) in enumerate(LIST):
        col = i // per_col
        row = i % per_col
        x = M + col * (col_w + 20)
        y = ly + row * 14
        cv.text(x, y, str(i + 14) + ".", 1, REGION_COLORS[reg])
        cv.text(x + 26, y, t, 1, INK)
        sw = cv.text_w(src, 1)
        cv.text(x + col_w - sw, y, src, 1, GREY)

    # --- stats strip (navy) ---
    sy2 = ly + per_col * 14 + 12
    cv.rect(0, sy2, W, 52, NAVY)
    seg_w = W // len(STATS)
    for i, (num, lab) in enumerate(STATS):
        x = i * seg_w + 16
        cv.text(x, sy2 + 7, num, 3, WHITE)
        cv.text(x, sy2 + 32, lab, 1, (200, 210, 224))
        if i:
            cv.vline(i * seg_w, sy2 + 9, 34, NAVY_LT)
    fy = sy2 + 52 + 6
    cv.text(M, fy, "All stories verified against Reuters, AP, BBC, ESPN, JMA, ATP, BWF, WAFA, UKMTO, CENTCOM, ABC, CBS, AAP, The Hindu, Punch, Pen Agency.", 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    cv = render()
    data = png_bytes(cv)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes", "sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
