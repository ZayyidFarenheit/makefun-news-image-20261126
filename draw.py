#!/usr/bin/env python3
"""Draw the news-image-20261126 entry.

A newspaper front page (1024x1024) summing up Thursday 26 November 2026
world news in one image. It copies the rank-1 winner's layout closely:
huge serif masthead "THE WORLD IN ONE DAY", the date, an italic
sub-headline naming the three lead stories, a numbers strip, a region
colour bar, three large illustrated lead stories, ten smaller
illustrated stories, a UTC timeline, a world map with numbered pins, a
numbered brief list (14-36), a DATE CHECK box and a sources footer.
Every story carries a "HOW SURE" confidence tag (OFFICIAL / CONFIRMED /
REPORTED / CLAIM / ONGOING).

The one deliberate change from rank 1: five of its stories were first
reported on an earlier day, so they move into the DATE CHECK and their
grid slots go to genuine 26 November stories -- the Saudi interception
of two Houthi missiles over Riyadh, the EU budget/Ukraine summit, the
Taiwan tariff answer, the Asian markets bounce and the Norway oil
licences ruling. The three lead stories are unchanged: all three are
genuinely 26 November (the Macy's parade postponement, India's 26/11
anniversary and Constitution Day, and Gukesh-Sindarov Game 3 at 15:00
CET -- Friday 27 November is the rest day).

Method is fully drawn: all thirteen scenes are flat PIL illustrations
in one consistent newspaper style (muted palette, simple clean shapes,
like the rank-1 winner); all text, layout, map and lists are drawn here.

Deterministic: no network, no randomness, no timestamps. Pure Pillow.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 222)
INK = (25, 25, 25)
RED = (168, 35, 42)
REDK = (176, 39, 39)
GREY_TXT = (70, 70, 70)
RULE = (40, 40, 40)
GOLD = (205, 170, 100)

BLUE = (32, 96, 138)
GREEN = (45, 124, 78)
ORANGE = (212, 137, 31)
PURPLE = (124, 76, 156)
TEAL = (22, 138, 142)
GREY = (93, 93, 93)
BROWN = (150, 110, 70)
DARKGREEN = (60, 90, 60)
MAPSEA = (198, 220, 232)
MAPTAN = (233, 215, 180)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(d, text, f, maxw, max_lines=None):
    """Greedy word wrap; returns a list of lines (at most max_lines)."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
            if max_lines and len(lines) >= max_lines:
                break
    if cur and (not max_lines or len(lines) < max_lines):
        lines.append(cur)
    return lines


def fit(d, text, path, maxw, start, minimum=8):
    """Largest font size (<= start) at which text fits maxw."""
    size = start
    while size > minimum and d.textlength(text, font=font(path, size)) > maxw:
        size -= 1
    return font(path, size)


def center_text(d, cx, y, text, f, fill):
    d.text((cx, y), text, font=f, fill=fill, anchor="ma")


# ---------------------------------------------------------------- data
# (label, count, colour) -- region shares of the 36 stories; must sum 36.
REGIONS = [
    ("North America 7", 7, BLUE),
    ("South Asia 5", 5, REDK),
    ("Europe 6", 6, GREEN),
    ("Middle East 4", 4, ORANGE),
    ("Africa 4", 4, PURPLE),
    ("World 1", 1, GREY),
    ("East Asia 5", 5, TEAL),
    ("Oceania 2", 2, BROWN),
    ("South America 2", 2, DARKGREEN),
]

UTC_ITEMS = [
    ("00:00", "Thanksgiving Day begins in the US"),
    ("06:00", "Delhi wakes to Constitution Day"),
    ("13:30", "Macy's 100th parade was due to step off"),
    ("14:00", "Chess Game 3 begins in Geneva (15:00 CET)"),
    ("15:00", "High-wind warning begins in New York"),
    ("23:00", "The day's 36 stories filed"),
]

# tag -> colour for the HOW SURE confidence system.
TAGS = {
    "OFFICIAL": BLUE, "CONFIRMED": GREEN, "REPORTED": ORANGE,
    "CLAIM": REDK, "ONGOING": TEAL,
}

TOP3 = [
    dict(num=1, tag="REPORTED", source="AP",
         headline="Macy's 100th Thanksgiving parade postponed to Saturday",
         deck="A nor'easter brings 60 mph gusts to New York; the parade "
              "moves to Saturday, a first in 100 years.",
         ill="parade"),
    dict(num=2, tag="CONFIRMED", source="PTI",
         headline="India marks 18 years since the 26/11 Mumbai attacks",
         deck="Tributes across India on the anniversary, as the nation "
              "also marks 77 years of its Constitution.",
         ill="india"),
    dict(num=3, tag="ONGOING", source="FIDE",
         headline="Gukesh meets Sindarov in Game 3 of the title match",
         deck="The world championship is level after two draws; Game 3 "
              "is played in Geneva today.",
         ill="chess"),
]

GRID = [
    dict(num=4, tag="REPORTED", source="REUTERS",
         headline="Saudi defences down Houthi missiles over Riyadh",
         ill="missile"),
    dict(num=5, tag="OFFICIAL", source="EU COUNCIL",
         headline="EU leaders meet on budget and Ukraine aid",
         ill="summit"),
    dict(num=6, tag="REPORTED", source="AP",
         headline="Israeli strike kills Hamas security chief in Gaza",
         ill="gaza"),
    dict(num=7, tag="CLAIM", source="EUROMAIDAN",
         headline="Ukraine says laser downed a jet-powered drone",
         ill="laser"),
    dict(num=8, tag="REPORTED", source="REUTERS",
         headline="Russian strikes cut power across five regions",
         ill="power"),
    dict(num=9, tag="CONFIRMED", source="REUTERS",
         headline="US proposes new tariffs on 14 trading partners",
         ill="tariffs"),
    dict(num=10, tag="OFFICIAL", source="CNA",
         headline="Taiwan answers US tariff plan",
         ill="taiwan"),
    dict(num=11, tag="REPORTED", source="YONHAP",
         headline="Asian stocks bounce back",
         ill="stocks"),
    dict(num=12, tag="REPORTED", source="REUTERS",
         headline="Norway court voids oil licences",
         ill="court"),
    dict(num=13, tag="CONFIRMED", source="AP",
         headline="Solomons signs security pact with Australia",
         ill="pact"),
]

# (number, place, text) for the "AND ALSO" list, 14-36.
BRIEFS = [
    (14, "INDIA–NEPAL", "Sign Rs 15,000 crore package — PTI"),
    (15, "USA", "Jobless claims fall to 189,000 — Reuters"),
    (16, "INDIA", "Urges human control of war AI — Reuters"),
    (17, "EU", "Visa bans, quotas on Chinese cars — Reuters"),
    (18, "COLOMBIA", "Police free 20 supermarket hostages — AP"),
    (19, "SUDAN", "Drone strikes kill 19 in Blue Nile — Reuters"),
    (20, "NIGER", "Saudi national seized by 15 men — Reuters"),
    (21, "INDONESIA", "$50bn Chinese smart-city deal — Reuters"),
    (22, "GULF OF MEXICO", "Plane crash; six aboard — AP"),
    (23, "PAKISTAN", "PIA shifts UK flights to 777 fleet — Reuters"),
    (24, "PARIS", "Students march, Bastille to Panthéon — AP"),
    (25, "USA", "NFL Thanksgiving games kick off — AP"),
    (26, "INDIA", "IITs add 6,000 AI, robotics seats — Govt of India"),
    (27, "USA", "Tempus buys Personalis in $600m deal — Investing.com"),
    (28, "CHINA", "Xi probe hits Shanghai chief — Reuters"),
    (29, "KENYA", "Secures 293,600 jobs in Saudi Arabia — Reuters"),
    (30, "BRAZIL", "Mosquitoes cut infections 68% — Study"),
    (31, "AUSTRALIA", "Palm Beach ferries strike — NSW Govt"),
    (32, "MALAYSIA", "Sues Google for $14m over YouTube — Reuters"),
    (33, "CAMEROON", "Swiss tourist killed by elephants — AP"),
    (34, "IOWA", "Army blows up 5 tonnes of explosives — Al Jazeera"),
    (35, "YEMEN", "Coalition hits Hodeidah after attacks — Reuters"),
    (36, "GAZA", "UN staff sacked on unproven claims — The Guardian"),
]

# Items left out of the day's news, with the day they belong to.
DATECHECK_LEFT = [
    "Shenzhou-24 docks, first Pakistani in orbit — 25 Nov",
    "Two tankers hit mines in Hormuz — 25 Nov",
    "Bangladesh lifts garment wage 36% — 25 Nov",
    "Leaked count of Russia's war dead — 23 Nov",
    "Real Madrid rout PSV 5–1 — 24 Nov",
]
DATECHECK_RIGHT = [
    "Houthi claim on Ras Tanura refinery — 25 Nov",
    "Cairo tanker fire kills 31 — 25 Nov",
    "Hera's Dimorphos crater pictures — 25 Nov",
    "Sooryavanshi smashes 204 off 53 — 24 Nov",
    "Nvidia reinstates Jensen Huang — 24 Nov",
]

# (lon, lat, region colour) for map pins 1-13.
PINS = {
    1: (-74.0, 40.7, BLUE),
    2: (72.8, 19.1, REDK),
    3: (6.1, 46.2, GREY),
    4: (46.7, 24.7, ORANGE),
    5: (4.35, 50.85, GREEN),
    6: (34.45, 31.5, ORANGE),
    7: (30.5, 50.4, GREEN),
    8: (37.0, 47.5, GREEN),
    9: (-77.0, 38.9, BLUE),
    10: (121.6, 25.0, TEAL),
    11: (127.0, 37.5, TEAL),
    12: (10.75, 59.9, GREEN),
    13: (160.0, -9.4, BROWN),
}
# Pixel nudges (dx, dy) for pins that would overlap a neighbour; a thin
# leader line joins the badge to the pin's true position. Spread so no
# two badges are closer than ~20px centre-to-centre.
NUDGE = {5: (2, -18), 6: (-14, 18), 7: (14, -14), 8: (22, 2),
         9: (-20, 14), 10: (6, 14), 11: (-2, -16), 12: (-26, -4)}

# Simplified continent outlines in (lon, lat).
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 72), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-65, 44), (-70, 42), (-75, 35),
     (-80, 26), (-84, 20), (-90, 14), (-95, 17), (-105, 22), (-115, 30),
     (-125, 40), (-125, 48), (-135, 58), (-155, 60), (-168, 66)],
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-20, 70), (-25, 75),
     (-40, 78), (-58, 75), (-60, 68), (-55, 60)],
    [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, -5), (-40, -10),
     (-35, -20), (-40, -30), (-50, -35), (-60, -40), (-70, -45),
     (-70, -55), (-75, -50), (-75, -35), (-80, -20), (-80, -10), (-80, 10)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (40, 15), (50, 10), (48, 0), (40, -10), (35, -20),
     (30, -30), (20, -35), (15, -30), (12, -18), (13, -5), (9, 4),
     (0, 5), (-8, 5), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (23, 58), (28, 60), (30, 62), (30, 68),
     (25, 70), (18, 70), (12, 65), (5, 60), (5, 58), (0, 52), (-5, 50),
     (-10, 45), (-10, 36)],
    [(30, 36), (35, 36), (40, 38), (45, 40), (50, 40), (55, 45), (60, 45),
     (65, 50), (70, 55), (75, 60), (80, 65), (90, 70), (100, 72),
     (110, 73), (120, 72), (130, 70), (140, 72), (150, 70), (160, 66),
     (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 60),
     (142, 55), (140, 50), (135, 45), (130, 40), (127, 38), (122, 32),
     (120, 28), (115, 22), (110, 20), (105, 10), (103, 5), (100, 8),
     (98, 12), (95, 16), (92, 20), (90, 22), (85, 20), (80, 15),
     (77, 8), (75, 15), (72, 20), (68, 23), (65, 25), (60, 25),
     (57, 27), (52, 28), (50, 30), (48, 30), (45, 32), (42, 35),
     (38, 36), (35, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -35), (125, -33),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -30), (150, -25), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20), (113, -22)],
]


# ------------------------------------------------------- hero illustrations
# All three heroes are flat PIL drawings in the same visual language
# as the grid scenes (muted newspaper palette, simple clean shapes).


def _num_badge(d, x, y, num):
    d.ellipse([x + 1, y + 1, x + 25, y + 25], fill=REDK)
    d.text((x + 13, y + 12), str(num), font=font(SANS_B, 13),
           fill=(255, 255, 255), anchor="mm")


def _tag_box(d, x, y, tag, size=9):
    """Outlined confidence tag; returns its width. Top-left at (x, y)."""
    col = TAGS[tag]
    f = font(SANS_B, size)
    tw = d.textlength(tag, font=f)
    w = tw + 10
    h = size + 7
    d.rounded_rectangle([x, y, x + w, y + h], radius=2, outline=col,
                        width=1, fill=PAPER)
    d.text((x + w / 2, y + h / 2 - 1), tag, font=f, fill=col, anchor="mm")
    return w


def _chip(d, x, y, text, size=8, fg=(255, 255, 255), bg=(30, 30, 30)):
    f = font(SANS_B, size)
    tw = d.textlength(text, font=f)
    d.rectangle([x, y, x + tw + 8, y + size + 6], fill=bg)
    d.text((x + 4, y + 3), text, font=f, fill=fg)
    return tw + 8


def ill_parade(img, d, x, y, w, h):
    # Flat night skyline with a white parade balloon, like rank 1.
    d.rectangle([x, y, x + w, y + h], fill=(26, 42, 74))
    # Rain streaks.
    for rx, ry, rl in ((40, 8, 12), (90, 22, 10), (150, 6, 12),
                       (210, 18, 10), (260, 10, 12), (300, 26, 10)):
        d.line([x + rx, y + ry, x + rx - 4, y + ry + rl],
               fill=(110, 140, 185), width=1)
    # Skyline silhouettes with lit windows.
    for bx, bw, bh in ((0, 34, 30), (38, 22, 44), (64, 30, 26),
                       (98, 26, 52), (128, 34, 34), (166, 24, 48),
                       (194, 30, 28), (228, 26, 56), (258, 30, 36),
                       (292, 36, 46)):
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                    fill=(14, 24, 48))
        for wx in range(bx + 5, bx + bw - 3, 9):
            for wy in range(h - bh + 5, h - 4, 10):
                d.rectangle([x + wx, y + wy, x + wx + 2, y + wy + 3],
                            fill=(247, 190, 60))
    # White parade balloon.
    cx, cy = x + 130, y + 34
    d.ellipse([cx - 46, cy - 26, cx + 46, cy + 26], fill=(255, 255, 255))
    d.ellipse([cx - 18, cy - 8, cx - 12, cy - 2], fill=(20, 20, 20))
    d.ellipse([cx + 12, cy - 8, cx + 18, cy - 2], fill=(20, 20, 20))
    d.arc([cx - 14, cy - 2, cx + 14, cy + 16], start=15, end=165,
          fill=(200, 40, 40), width=2)
    # Small clouds.
    for ccx, ccy in ((250, 18), (270, 24)):
        d.ellipse([x + ccx, y + ccy, x + ccx + 26, y + ccy + 10],
                  fill=(220, 228, 240))
    _chip(d, x + 6, y + h - 22, "POSTPONED TO SATURDAY", 9,
          fg=(255, 255, 255), bg=REDK)
    d.ellipse([x + w - 40, y + h - 40, x + w - 6, y + h - 6],
              fill=(205, 170, 60), outline=(255, 255, 255), width=2)
    d.text((x + w - 23, y + h - 23), "100", font=font(SANS_B, 12),
           fill=(255, 255, 255), anchor="mm")


def ill_india(img, d, x, y, w, h):
    # Flat Gateway of India at sunset, diya candles below, tricolour.
    d.rectangle([x, y, x + w, y + h], fill=(232, 164, 76))
    d.rectangle([x, y + 62, x + w, y + h], fill=(240, 190, 120))
    # Sun, left.
    d.ellipse([x + 10, y + 8, x + 50, y + 48], fill=(247, 210, 120))
    # Gateway monument (dark terracotta silhouette).
    mx0, mx1 = x + 96, x + 232
    d.rectangle([mx0, y + 30, mx1, y + h], fill=(150, 80, 45))
    # Side towers with small domes.
    for tx in (mx0 - 26, mx1 + 2):
        d.rectangle([tx, y + 52, tx + 24, y + h], fill=(150, 80, 45))
        d.pieslice([tx - 2, y + 44, tx + 26, y + 60], start=180, end=360,
                   fill=(150, 80, 45))
    # Main dome and finial.
    d.pieslice([mx0 + 44, y + 14, mx0 + 92, y + 46], start=180, end=360,
               fill=(150, 80, 45))
    d.rectangle([mx0 + 62, y + 8, mx0 + 74, y + 18], fill=(150, 80, 45))
    # Big arch opening in sky colour.
    d.rectangle([mx0 + 46, y + 56, mx0 + 90, y + h], fill=(240, 190, 120))
    d.pieslice([mx0 + 46, y + 34, mx0 + 90, y + 78], start=180, end=360,
               fill=(240, 190, 120))
    # Small arched niches.
    for nx in (mx0 + 10, mx1 - 30):
        d.rectangle([nx, y + 62, nx + 18, y + h], fill=(120, 60, 35))
        d.pieslice([nx, y + 53, nx + 18, y + 71], start=180, end=360,
                   fill=(120, 60, 35))
    # Row of diya candles in the clear zones left and right.
    for fx in (x + 10, x + 24, x + 38, x + 52, x + 268, x + 282, x + 296):
        d.ellipse([fx, y + h - 16, fx + 8, y + h - 8], fill=(247, 190, 60))
        d.polygon([(fx + 4, y + h - 24), (fx + 1, y + h - 16),
                   (fx + 7, y + h - 16)], fill=(255, 120, 30))
    # Tricolour flag on a pole, top right.
    d.rectangle([x + w - 32, y + 26, x + w - 30, y + 62], fill=(60, 60, 60))
    d.rectangle([x + w - 30, y + 28, x + w - 4, y + 34], fill=(255, 153, 51))
    d.rectangle([x + w - 30, y + 34, x + w - 4, y + 40], fill=(255, 255, 255))
    d.rectangle([x + w - 30, y + 40, x + w - 4, y + 46], fill=(19, 136, 8))
    d.ellipse([x + w - 19, y + 34, x + w - 13, y + 40], fill=(20, 60, 140))
    _chip(d, x + w - 78, y + 6, "18 YEARS", 9,
          fg=(255, 255, 255), bg=(20, 20, 20))


def ill_chess(img, d, x, y, w, h):
    # Flat chessboard on a dark green table, like rank 1.
    d.rectangle([x, y, x + w, y + h], fill=(24, 58, 44))
    # Board: 8x8 squares of 11px.
    bx, by, s = x + 14, y + 2, 11
    for r in range(8):
        for c in range(8):
            col = (238, 228, 200) if (r + c) % 2 == 0 else (70, 120, 92)
            d.rectangle([bx + c * s, by + r * s,
                         bx + (c + 1) * s, by + (r + 1) * s], fill=col)
    d.rectangle([bx, by, bx + 8 * s, by + 8 * s], outline=(200, 180, 140),
                width=2)

    def _pawn(px, py, col):
        d.ellipse([px - 3, py - 8, px + 3, py - 2], fill=col)
        d.polygon([(px - 4, py - 2), (px + 4, py - 2), (px + 5, py),
                   (px - 5, py)], fill=col)

    def _king(px, py, col):
        d.rectangle([px - 1, py - 13, px + 1, py - 8], fill=col)
        d.rectangle([px - 3, py - 11, px + 3, py - 9], fill=col)
        d.ellipse([px - 3, py - 8, px + 3, py - 2], fill=col)
        d.polygon([(px - 4, py - 2), (px + 4, py - 2), (px + 5, py),
                   (px - 5, py)], fill=col)

    # (col, row) squares; py is the square's bottom edge.
    _king(bx + 4 * s + 5, by + 7 * s + 10, (245, 245, 240))
    _pawn(bx + 5 * s + 5, by + 6 * s + 10, (245, 245, 240))
    _king(bx + 3 * s + 5, by + 1 * s + 10, (20, 20, 20))
    _pawn(bx + 2 * s + 5, by + 2 * s + 10, (20, 20, 20))
    # A large white king standing on the table fills the middle.
    kx, kb = x + 162, y + h - 8
    d.polygon([(kx - 16, kb), (kx + 16, kb), (kx + 11, kb - 8),
               (kx - 11, kb - 8)], fill=(245, 245, 240))
    d.rectangle([kx - 7, kb - 30, kx + 7, kb - 8], fill=(245, 245, 240))
    d.ellipse([kx - 10, kb - 34, kx + 10, kb - 26], fill=(245, 245, 240))
    d.ellipse([kx - 9, kb - 48, kx + 9, kb - 32], fill=(245, 245, 240))
    d.rectangle([kx - 1, kb - 58, kx + 1, kb - 46], fill=(245, 245, 240))
    d.rectangle([kx - 6, kb - 53, kx + 6, kb - 51], fill=(245, 245, 240))
    _chip(d, x + w - 66, y + 6, "GAME 3", 9,
          fg=(255, 255, 255), bg=REDK)
    # Two clock faces and the score, like rank 1's hero.
    d.rectangle([x + w - 128, y + h - 30, x + w - 68, y + h - 6],
                fill=(255, 255, 255))
    d.rectangle([x + w - 62, y + h - 30, x + w - 6, y + h - 6],
                fill=(255, 255, 255))
    d.text((x + w - 98, y + h - 18), "1:32", font=font(SANS_B, 11),
           fill=(20, 20, 20), anchor="mm")
    d.text((x + w - 34, y + h - 18), "1:32", font=font(SANS_B, 11),
           fill=(20, 20, 20), anchor="mm")
    d.rectangle([x + 6, y + h - 14, x + 128, y + h - 2], fill=(20, 40, 30))
    d.text((x + 67, y + h - 8), "GUKESH 1 – 1 SINDAROV",
           font=font(SANS_B, 9), fill=(255, 255, 255), anchor="mm")


HERO_ILL = {"parade": ill_parade, "india": ill_india, "chess": ill_chess}


# ------------------------------------------------------- grid illustrations
def _rocket(d, cx, cy, ang):
    """Small rocket silhouette centred at (cx, cy), nose pointing along
    angle ang (degrees, 0 = east, -90 = north)."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)    # nose direction
    vx, vy = -uy, ux                     # perpendicular
    nose = (cx + 13 * ux, cy + 13 * uy)
    b1 = (cx + 2 * ux + 4 * vx, cy + 2 * uy + 4 * vy)
    b2 = (cx - 10 * ux + 4 * vx, cy - 10 * uy + 4 * vy)
    b3 = (cx - 10 * ux - 4 * vx, cy - 10 * uy - 4 * vy)
    b4 = (cx + 2 * ux - 4 * vx, cy + 2 * uy - 4 * vy)
    d.polygon([nose, b1, b2, b3, b4], fill=(235, 235, 235))
    # Red fins and a gold flame behind.
    d.polygon([(cx - 7 * ux + 4 * vx, cy - 7 * uy + 4 * vy),
               (cx - 13 * ux + 9 * vx, cy - 13 * uy + 9 * vy),
               (cx - 11 * ux + 4 * vx, cy - 11 * uy + 4 * vy)],
              fill=(200, 40, 40))
    d.polygon([(cx - 7 * ux - 4 * vx, cy - 7 * uy - 4 * vy),
               (cx - 13 * ux - 9 * vx, cy - 13 * uy - 9 * vy),
               (cx - 11 * ux - 4 * vx, cy - 11 * uy - 4 * vy)],
              fill=(200, 40, 40))
    d.polygon([(cx - 10 * ux, cy - 10 * uy),
               (cx - 18 * ux + 2 * vx, cy - 18 * uy + 2 * vy),
               (cx - 18 * ux - 2 * vx, cy - 18 * uy - 2 * vy)],
              fill=(247, 190, 60))


def ill_missile(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 26, 44))
    # City skyline along the bottom.
    for bx, bw, bh in ((0, 26, 18), (30, 18, 26), (52, 30, 14),
                       (86, 16, 24), (106, 24, 16), (134, 20, 28),
                       (158, 26, 14), (186, 8, 34)):
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                    fill=(48, 58, 78))
    # Two interceptor trails rising to a burst below the chip.
    d.line([x + 20, y + h - 6, x + 100, y + 26], fill=(220, 230, 255),
           width=2)
    d.line([x + 178, y + h - 6, x + 100, y + 26], fill=(220, 230, 255),
           width=2)
    for dx, dy in ((0, 0), (-7, 3), (7, 3), (0, -7), (-5, -5), (5, -5)):
        d.line([x + 100 + dx, y + 26 + dy, x + 100, y + 26],
               fill=(255, 200, 80), width=2)
    # Two clear interceptor rockets mid-trail, noses toward the burst.
    _rocket(d, x + 58, y + 38, -16)
    _rocket(d, x + 142, y + 38, -164)
    _chip(d, x + 30, y + 4, "2 MISSILES DOWNED", 8)


def ill_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 58, 95))
    # Ring of EU stars.
    cx, cy = x + w // 2, y + h // 2 - 2
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        sx = cx + int(52 * math.cos(a))
        sy = cy + int(24 * math.sin(a))
        d.polygon([(sx, sy - 4), (sx + 1, sy - 1), (sx + 4, sy),
                   (sx + 1, sy + 1), (sx, sy + 4), (sx - 1, sy + 1),
                   (sx - 4, sy), (sx - 1, sy - 1)], fill=(247, 190, 60))
    d.text((cx, cy - 4), "EU 27", font=font(SANS_B, 12),
           fill=(255, 255, 255), anchor="mm")
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(247, 190, 60))
    _chip(d, x + 30, y + 4, "2-DAY SUMMIT", 8, fg=(31, 58, 95),
          bg=(255, 255, 255))


def ill_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 204, 182))
    # Street scene: three flat buildings with windows; the middle one
    # damaged, a little smoke above its roofline only.
    d.rectangle([x + 12, y + 18, x + 66, y + h], fill=(168, 140, 110))
    for wx in (22, 40):
        for wy in (26, 38):
            d.rectangle([x + wx, y + wy, x + wx + 8, y + wy + 7],
                        fill=(60, 50, 40))
    # Middle damaged building with a broken top corner.
    d.rectangle([x + 74, y + 26, x + 126, y + h], fill=(140, 116, 88))
    d.polygon([(x + 104, y + 26), (x + 126, y + 26), (x + 126, y + 40)],
              fill=(214, 204, 182))
    for wx in (82, 102):
        d.rectangle([x + wx, y + 34, x + wx + 8, y + 41], fill=(60, 50, 40))
    # Rubble at its base.
    for rx, rw in ((74, 10), (88, 8), (102, 12)):
        d.rectangle([x + rx, y + h - 6, x + rx + rw, y + h],
                    fill=(95, 82, 66))
    # Right building.
    d.rectangle([x + 134, y + 20, x + 182, y + h], fill=(168, 140, 110))
    for wx in (142, 160):
        for wy in (28, 40):
            d.rectangle([x + wx, y + wy, x + wx + 8, y + wy + 7],
                        fill=(60, 50, 40))
    # Two small smoke puffs above the damaged roof.
    for sx, sy, r in ((100, 14, 6), (112, 8, 5)):
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(120, 120, 120))
    _chip(d, x + 30, y + 4, "GAZA CITY", 8)


def ill_laser(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 16, 30))
    for sx, sy in ((30, 12), (70, 8), (120, 14), (160, 8), (190, 12)):
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2],
                  fill=(255, 255, 255))
    # Green laser beam from lower left to the drone.
    d.line([x + 8, y + h - 4, x + 150, y + 18], fill=(90, 255, 140),
           width=2)
    # Small jet-powered drone silhouette.
    d.polygon([(x + 138, y + 14), (x + 168, y + 18), (x + 138, y + 22),
               (x + 146, y + 18)], fill=(200, 200, 200))
    d.ellipse([x + 148, y + 15, x + 158, y + 21], fill=(220, 220, 220))
    _chip(d, x + 30, y + 4, "BLYSK LASER", 8, fg=(90, 255, 140),
          bg=(12, 16, 30))


def ill_power(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 28, 40))
    # Two pylons with sagging lines.
    for px in (46, 140):
        d.line([x + px, y + 12, x + px, y + h], fill=(140, 140, 140),
               width=2)
        d.line([x + px - 16, y + 16, x + px + 16, y + 16],
               fill=(140, 140, 140), width=2)
    d.line([x + 30, y + 16, x + 96, y + 30], fill=(140, 140, 140))
    d.line([x + 96, y + 30, x + 156, y + 16], fill=(140, 140, 140))
    # Yellow lightning bolt.
    d.polygon([(x + 104, y + 6), (x + 90, y + 32), (x + 100, y + 32),
               (x + 92, y + 54), (x + 114, y + 26), (x + 104, y + 26)],
              fill=(247, 190, 60))
    _chip(d, x + 30, y + 4, "5 REGIONS DARK", 8, fg=(247, 190, 60),
          bg=(24, 28, 40))


def ill_tariffs(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
    d.text((x + 30, y + 4), "14 PARTNERS", font=font(SANS_B, 11),
           fill=REDK)
    # Four flag chips in a row: US, EU, China, Japan. No arrow.
    for i, code in enumerate(("us", "eu", "cn", "jp")):
        fx = x + 10 + i * 46
        fy = y + 26
        base = {"us": (255, 255, 255), "eu": (30, 60, 140),
                "cn": (200, 40, 40), "jp": (255, 255, 255)}[code]
        d.rectangle([fx, fy, fx + 40, fy + 24], fill=base,
                    outline=(120, 120, 120))
        if code == "us":
            for sy in (fy + 3, fy + 9, fy + 15, fy + 21):
                d.rectangle([fx, sy, fx + 40, sy + 2], fill=(200, 40, 40))
            d.rectangle([fx, fy, fx + 16, fy + 12], fill=(30, 60, 140))
            d.ellipse([fx + 6, fy + 4, fx + 10, fy + 8],
                      fill=(255, 255, 255))
        elif code == "eu":
            for sx, sy in ((fx + 12, fy + 7), (fx + 28, fy + 7),
                           (fx + 12, fy + 17), (fx + 28, fy + 17)):
                d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1],
                          fill=(247, 190, 60))
        elif code == "cn":
            d.polygon([(fx + 10, fy + 4), (fx + 12, fy + 9),
                       (fx + 17, fy + 9), (fx + 13, fy + 12),
                       (fx + 14, fy + 17), (fx + 10, fy + 14),
                       (fx + 6, fy + 17), (fx + 7, fy + 12),
                       (fx + 3, fy + 9), (fx + 8, fy + 9)],
                      fill=(247, 190, 60))
        else:  # jp
            d.ellipse([fx + 14, fy + 6, fx + 26, fy + 18],
                      fill=(200, 40, 40))


def ill_taiwan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(225, 232, 240))
    # Semiconductor wafer: big disc, fine grid clipped to the disc,
    # a chip square in the centre, traces running off right.
    cx, cy, r = x + 66, y + 30, 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 170, 200),
              outline=(90, 110, 140), width=2)
    for off in (-16, -8, 0, 8, 16):
        half = int(math.sqrt(max(0, (r - 2) ** 2 - off ** 2)))
        d.line([cx + off, cy - half, cx + off, cy + half],
               fill=(200, 210, 230), width=1)
        d.line([cx - half, cy + off, cx + half, cy + off],
               fill=(200, 210, 230), width=1)
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15],
              outline=(120, 145, 180), width=1)
    d.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=(30, 50, 80))
    for px, py in ((cx - 9, cy), (cx + 9, cy), (cx, cy - 9), (cx, cy + 9)):
        d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(247, 190, 60))
    d.line([cx + r, cy - 8, x + 150, cy - 8], fill=(60, 90, 130), width=1)
    d.line([x + 150, cy - 8, x + 150, cy - 16], fill=(60, 90, 130),
           width=1)
    d.line([cx + r, cy + 8, x + 150, cy + 8], fill=(60, 90, 130), width=1)
    d.line([x + 150, cy + 8, x + 150, cy + 16], fill=(60, 90, 130),
           width=1)
    _chip(d, x + 140, y + 4, "15% MAX", 8, fg=(255, 255, 255),
          bg=GREEN)


def ill_stocks(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 244, 238))
    # Rising bars and a green trend line.
    bars = [(20, 14), (52, 22), (84, 18), (116, 30), (148, 38)]
    for bx, bh in bars:
        d.rectangle([x + bx, y + h - 8 - bh, x + bx + 20, y + h - 8],
                    fill=GREEN)
    d.line([x + 14, y + h - 14, x + 60, y + 26, x + 110, y + 30,
            x + 170, y + 8], fill=(20, 90, 50), width=2)
    d.polygon([(x + 170, y + 8), (x + 158, y + 8), (x + 170, y + 20)],
              fill=(20, 90, 50))
    d.text((x + 30, y + 4), "KOSPI +2%", font=font(SANS_B, 11),
           fill=GREEN)


def ill_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(223, 232, 242))
    d.polygon([(x + 36, y + 12), (x + 98, y + 2), (x + 160, y + 12)],
              fill=(31, 58, 95))
    for cx in (52, 74, 96, 118, 140):
        d.rectangle([x + cx, y + 14, x + cx + 6, y + 42],
                    fill=(245, 245, 240))
    d.rectangle([x + 36, y + 42, x + 160, y + 48], fill=(31, 58, 95))
    # Oil derrick crossed out, kept inside the box.
    d.line([x + 176, y + 14, x + 176, y + 48], fill=(60, 60, 60),
           width=2)
    d.line([x + 168, y + 22, x + 184, y + 48], fill=(60, 60, 60),
           width=2)
    d.ellipse([x + 166, y + 10, x + 186, y + 30], outline=REDK, width=3)
    d.line([x + 168, y + 28, x + 184, y + 12], fill=REDK, width=3)
    _chip(d, x + 30, y + 4, "SUPREME COURT", 8, fg=(31, 58, 95),
          bg=(255, 255, 255))


def ill_pact(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 236, 220))
    # Treaty document with a red seal.
    d.rectangle([x + 12, y + 8, x + 92, y + 48], fill=(255, 255, 255),
                outline=(150, 150, 150))
    d.polygon([(x + 92, y + 8), (x + 92, y + 20), (x + 80, y + 8)],
              fill=(220, 220, 220))
    for ly in (16, 24, 32):
        d.line([x + 20, y + ly, x + 70, y + ly], fill=(120, 120, 120),
               width=1)
    d.ellipse([x + 72, y + 36, x + 84, y + 48], fill=REDK)
    d.text((x + 78, y + 42), "S", font=font(SANS_B, 7),
           fill=(255, 255, 255), anchor="mm")
    # Solomon Islands flag on its pole.
    d.rectangle([x + 118, y + 8, x + 120, y + 48], fill=(60, 60, 60))
    d.rectangle([x + 120, y + 10, x + 148, y + 28], fill=(30, 80, 160))
    d.line([x + 120, y + 28, x + 148, y + 10], fill=(247, 190, 60),
           width=2)
    for sx, sy in ((126, 15), (136, 13), (142, 20)):
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(247, 190, 60))
    d.rectangle([x + 120, y + 24, x + 148, y + 28], fill=(20, 120, 80))
    # Australian flag on its pole.
    d.rectangle([x + 158, y + 8, x + 160, y + 48], fill=(60, 60, 60))
    d.rectangle([x + 160, y + 10, x + 188, y + 28], fill=(30, 60, 140))
    d.rectangle([x + 160, y + 10, x + 172, y + 19], fill=(255, 255, 255))
    d.line([x + 160, y + 14, x + 172, y + 14], fill=(200, 40, 40),
           width=2)
    d.line([x + 166, y + 10, x + 166, y + 19], fill=(200, 40, 40),
           width=2)
    for sx, sy in ((180, 15), (184, 22)):
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(255, 255, 255))
    _chip(d, x + 30, y + 4, "SIGNED", 8)


GRID_ILL = {
    "missile": ill_missile, "summit": ill_summit, "gaza": ill_gaza,
    "laser": ill_laser, "power": ill_power, "tariffs": ill_tariffs,
    "taiwan": ill_taiwan, "stocks": ill_stocks, "court": ill_court,
    "pact": ill_pact,
}


# ------------------------------------------------------------- layout
def draw_header(d):
    f = fit(d, "THE WORLD IN ONE DAY", SERIF_B, 1000, 56)
    center_text(d, 512, 4, "THE WORLD IN ONE DAY", f, INK)
    d.rectangle([8, 64, 1016, 65], fill=RULE)
    center_text(d, 512, 68, "THURSDAY 26 NOVEMBER 2026",
                font(SERIF_B, 21), INK)
    sub = ("A nor'easter grounds New York's 100th Thanksgiving parade, "
           "India marks 18 years since the 26/11 Mumbai attacks, and "
           "Gukesh meets Sindarov in Game 3 of the world title match "
           "in Geneva.")
    lines = wrap(d, sub, font(SERIF_I, 15), 960, max_lines=2)
    yy = 94
    for ln in lines:
        center_text(d, 512, yy, ln, font(SERIF_I, 15), (90, 30, 35))
        yy += 18


def draw_numbers(d):
    boxes = [("36", "STORIES"), ("9", "REGIONS"),
             ("17", "SOURCES · 15 FIELDS")]
    bw = 1008 / 3
    for i, (num, label) in enumerate(boxes):
        x = 8 + i * bw
        d.rectangle([x, 130, x + bw - 4, 158], outline=RULE, width=1)
        nf = font(SERIF_B, 24)
        lf = font(SANS_B, 13)
        tw = (d.textlength(num, font=nf) + 8
              + d.textlength(label, font=lf))
        cx = x + (bw - 4 - tw) / 2
        d.text((cx, 136), num, font=nf, fill=REDK)
        d.text((cx + d.textlength(num, font=nf) + 8, 141), label,
               font=lf, fill=INK)


def draw_region_bar(d):
    total = sum(c for _, c, _ in REGIONS)
    x = 8
    for _, count, col in REGIONS:
        w = 1008 * count / total
        d.rectangle([x, 162, x + w, 172], fill=col)
        x += w
    labels = " · ".join("%s %d" % (name.rsplit(" ", 1)[0], count)
                        for name, count, _ in REGIONS)
    center_text(d, 512, 176, labels, font(SANS, 10), INK)


def draw_top3(img, d):
    for i, s in enumerate(TOP3):
        x = 8 + i * 336
        HERO_ILL[s["ill"]](img, d, x, 192, 328, 104)
        _num_badge(d, x, 192, s["num"])
        hf = font(SERIF_B, 19)
        lines = wrap(d, s["headline"], hf, 328, max_lines=3)
        yy = 300
        for ln in lines:
            d.text((x, yy), ln, font=hf, fill=INK)
            yy += 22
        df = font(SANS, 11)
        dlines = wrap(d, s["deck"], df, 328, max_lines=2)
        yy = 368
        for ln in dlines:
            d.text((x, yy), ln, font=df, fill=(50, 50, 50))
            yy += 13
        sf = font(SANS, 9)
        d.text((x, 398), "SOURCE: " + s["source"], font=sf,
               fill=GREY_TXT)
        _tag_box(d, x + 328 - _tag_w(d, s["tag"]), 397, s["tag"], 9)


def _tag_w(d, tag, size=9):
    f = font(SANS_B, size)
    return d.textlength(tag, font=f) + 10


def draw_grid(d):
    for row in range(2):
        y0 = 428 + row * 112
        for col in range(5):
            s = GRID[row * 5 + col]
            x = 8 + col * 202
            GRID_ILL[s["ill"]](d, x, y0, 194, 56)
            _num_badge(d, x, y0, s["num"])
            hf = font(SERIF_B, 13)
            lines = wrap(d, s["headline"], hf, 194, max_lines=2)
            yy = y0 + 60
            for ln in lines:
                d.text((x, yy), ln, font=hf, fill=INK)
                yy += 15
            sf = font(SANS, 8)
            d.text((x, y0 + 92), s["source"], font=sf, fill=GREY_TXT)
            _tag_box(d, x + 194 - _tag_w(d, s["tag"], 8), y0 + 91,
                     s["tag"], 8)


def draw_utc(d):
    d.text((8, 652), "THE DAY IN UTC", font=font(SANS_B, 11), fill=REDK)
    for row in range(2):
        for col in range(3):
            t, label = UTC_ITEMS[row * 3 + col]
            x = 8 + col * 336
            y = 668 + row * 16
            d.text((x, y), t, font=font(SANS_B, 11), fill=REDK)
            tw = d.textlength(t, font=font(SANS_B, 11))
            d.text((x + tw + 5, y), label, font=font(SANS, 10),
                   fill=INK)


def _project(lon, lat, x0, y0, w, h):
    px = x0 + (lon + 170.0) / 360.0 * w
    py = y0 + (75.0 - lat) / 130.0 * h
    return (px, py)


def draw_map(d):
    x0, y0, w, h = 8, 728, 332, 150
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=MAPSEA)
    for poly in CONTINENTS:
        pts = [_project(lon, lat, x0, y0, w, h) for lon, lat in poly]
        d.polygon(pts, fill=MAPTAN)
    for n, (lon, lat, col) in sorted(PINS.items()):
        px, py = _project(lon, lat, x0, y0, w, h)
        dx, dy = NUDGE.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            d.line([px, py, px + dx, py + dy], fill=(90, 90, 90),
                   width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
            px, py = px + dx, py + dy
        d.ellipse([px - 6.5, py - 6.5, px + 6.5, py + 6.5], fill=col,
                  outline=(255, 255, 255))
        d.text((px, py - 1), str(n), font=font(SANS_B, 8),
               fill=(255, 255, 255), anchor="mm")


def draw_briefs(d):
    cols_x = [352, 684]
    for idx, (num, place, text) in enumerate(BRIEFS):
        ci = idx // 12
        ri = idx % 12
        x = cols_x[ci]
        y = 728 + ri * 13
        d.text((x, y), str(num), font=font(SANS_B, 9), fill=REDK)
        tx = x + 18
        bf = font(SANS_B, 9)
        rf = font(SANS, 9)
        pref = place + " "
        full = pref + text
        f = rf
        if d.textlength(pref, font=bf) + d.textlength(text, font=rf) > 314:
            f = font(SANS, 8)
        d.text((tx, y), pref, font=bf, fill=INK)
        pw = d.textlength(pref, font=bf)
        d.text((tx + pw, y), text, font=f, fill=(50, 50, 50))


def draw_datecheck(d):
    d.rectangle([8, 890, 1016, 970], outline=REDK, width=2)
    d.text((16, 896), "DATE CHECK — THESE ARE NOT 26 NOVEMBER",
           font=font(SANS_B, 11), fill=REDK)
    f = font(SANS, 10)
    for col, items in ((16, DATECHECK_LEFT), (516, DATECHECK_RIGHT)):
        yy = 914
        for item in items:
            # Word-boundary wrap only; every item fits on one line.
            for ln in wrap(d, "× " + item, f, 492):
                d.text((col, yy), ln, font=f, fill=INK)
                yy += 11


def draw_footer(d):
    center_text(d, 512, 976,
                "Every story here happened or was first reported on "
                "Thursday 26 November 2026. Sources are named on each "
                "story.",
                font(SERIF_I, 12), INK)
    f = font(SANS, 9)
    legend = ("HOW SURE: OFFICIAL = government or institution · "
              "CONFIRMED = wire or two sources · REPORTED = one outlet's "
              "reporting · CLAIM = one side's account · ONGOING = still "
              "unfolding. Scenes are drawn illustrations, not photographs.")
    lines = wrap(d, legend, f, 1000, max_lines=2)
    yy = 990
    for ln in lines:
        center_text(d, 512, yy, ln, f, GREY_TXT)
        yy += 11
    center_text(d, 512, 1012,
                "THE WORLD IN ONE DAY · 26 NOV 2026 · 36 STORIES, "
                "9 REGIONS",
                font(SANS_B, 9), GREY_TXT)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    draw_numbers(d)
    draw_region_bar(d)
    draw_top3(img, d)
    d.rectangle([8, 418, 1016, 419], fill=RULE)
    draw_grid(d)
    draw_utc(d)
    d.rectangle([8, 704, 1016, 705], fill=RULE)
    d.text((8, 710), "WHERE IT HAPPENED — PINS 1–13",
           font=font(SANS_B, 12), fill=INK)
    d.text((352, 710), "AND ALSO — STORIES 14–36",
           font=font(SANS_B, 12), fill=REDK)
    draw_map(d)
    draw_briefs(d)
    draw_datecheck(d)
    draw_footer(d)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
