from PIL import Image, ImageDraw, ImageFont
import math, os

# Animated dark command-center dashboard for Vedant's profile README.
# Smooth UI motion, live charts, project cards and terminal activity.
# No external artwork and no pixel-art scaling.

W, H = 960, 600
FRAMES = 72
DURATION = 90

BG = (11, 12, 13)
PANEL = (17, 19, 20)
PANEL2 = (20, 22, 23)
GRID = (28, 31, 31)
TEXT = (235, 236, 230)
MUTED = (132, 136, 130)
LINE = (51, 54, 52)
GREEN = (128, 190, 104)
CYAN = (93, 164, 177)
ORANGE = (223, 154, 75)
RED = (211, 98, 93)
PURPLE = (151, 118, 192)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
F = lambda n: ImageFont.truetype(FONT, n)
B = lambda n: ImageFont.truetype(BOLD, n)
M = lambda n: ImageFont.truetype(MONO, n)

def rr(d, box, radius=10, fill=None, outline=None, width=1):
    d.rounded_rectangle(tuple(map(int, box)), radius=radius, fill=fill, outline=outline, width=width)

def line(d, pts, fill, width=2):
    d.line([(int(x), int(y)) for x, y in pts], fill=fill, width=width, joint="curve")

def txt(d, x, y, s, font, color=TEXT, anchor=None):
    d.text((int(x), int(y)), s, font=font, fill=color, anchor=anchor)

def pill(d, x, y, w, h, label, fill, txtc=BG, frame=0, phase=0):
    yy = y + math.sin(frame * 0.13 + phase) * 1.4
    rr(d, (x, yy, x + w, yy + h), h / 2, fill=fill)
    txt(d, x + w / 2, yy + h / 2, label, B(11), txtc, "mm")

def grid_bg(d, frame):
    drift = (frame * 2) % 40
    for x in range(-40, W + 40, 40):
        line(d, [(x + drift, 0), (x + drift, H)], (20, 22, 22), 1)
    for y in range(0, H, 40):
        line(d, [(0, y), (W, y)], (20, 22, 22), 1)

def draw_graph(d, x, y, w, h, frame):
    rr(d, (x, y, x + w, y + h), 10, fill=PANEL2, outline=LINE)
    txt(d, x + 16, y + 14, "ACTIVITY", B(11), MUTED)
    txt(d, x + w - 14, y + 14, "LIVE", B(10), GREEN, "ra")
    for gy in range(y + 42, y + h - 12, 24):
        line(d, [(x + 14, gy), (x + w - 14, gy)], GRID, 1)
    pts = []
    for i in range(34):
        px = x + 16 + i * (w - 34) / 33
        val = 0.48 + 0.18 * math.sin(i * 0.55 + frame * 0.055) + 0.08 * math.sin(i * 1.4 + frame * 0.02)
        py = y + h - 18 - val * (h - 66)
        pts.append((px, py))
    reveal = min(len(pts), max(5, int(8 + 26 * ((frame % FRAMES) / (FRAMES - 1)))))
    line(d, pts[:reveal], GREEN, 3)
    for i, (px, py) in enumerate(pts[:reveal:6]):
        r = 3 + int((frame + i) % 5 == 0)
        d.ellipse((px - r, py - r, px + r, py + r), fill=GREEN)
    txt(d, x + 16, y + h - 14, "08:00", M(8), MUTED)
    txt(d, x + w - 16, y + h - 14, "NOW", M(8), MUTED, "ra")

def draw_bars(d, x, y, w, h, frame):
    rr(d, (x, y, x + w, y + h), 10, fill=PANEL2, outline=LINE)
    txt(d, x + 16, y + 14, "STACK USAGE", B(11), MUTED)
    items = [("WEB", 0.79, CYAN), ("AI", 0.64, PURPLE), ("AUTO", 0.56, ORANGE), ("DESIGN", 0.47, GREEN)]
    for j, (label, value, accent) in enumerate(items):
        yy = y + 44 + j * 24
        txt(d, x + 16, yy, label, M(8), MUTED)
        rr(d, (x + 76, yy + 1, x + w - 16, yy + 9), 4, fill=(34, 37, 37))
        p = value * (0.96 + 0.04 * math.sin(frame * 0.1 + j))
        rr(d, (x + 76, yy + 1, x + 76 + (w - 92) * p, yy + 9), 4, fill=accent)
    txt(d, x + w - 16, y + h - 12, "24 modules", M(8), MUTED, "ra")

def project_card(d, x, y, w, h, title, tag, accent, frame, index):
    y += math.sin(frame * 0.12 + index) * 1.2
    rr(d, (x, y, x + w, y + h), 12, fill=PANEL, outline=LINE)
    d.ellipse((x + 14, y + 15, x + 20, y + 21), fill=accent)
    txt(d, x + 28, y + 12, title, B(14))
    txt(d, x + 14, y + 39, tag, M(8), MUTED)
    pts = []
    for i in range(22):
        px = x + 14 + i * (w - 28) / 21
        py = y + h - 18 - 9 * math.sin(i * 0.7 + frame * 0.05 + index)
        pts.append((px, py))
    line(d, pts, accent, 2)
    txt(d, x + w - 14, y + h - 22, f"0{index + 1}", M(8), MUTED, "ra")

def ring(d, cx, cy, r, progress, color, width=4):
    start = -math.pi / 2
    end = start + 2 * math.pi * progress
    n = max(2, int(34 * progress))
    pts = []
    for i in range(n):
        a = start + (end - start) * i / max(1, n - 1)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    if len(pts) > 1:
        line(d, pts, color, width)

def cursor(d, frame):
    x = 140 + (frame * 13) % 700
    y = 125 + 80 * math.sin(frame * 0.23)
    line(d, [(x, y), (x + 14, y + 6), (x + 7, y + 10), (x + 11, y + 21)], TEXT, 2)

def draw(frame):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    grid_bg(d, frame)

    rr(d, (20, 18, 940, 78), 14, fill=PANEL, outline=LINE)
    txt(d, 42, 34, "VEDANT", B(20))
    txt(d, 42, 58, "creative technology / command center", M(9), MUTED)
    txt(d, 690, 38, "SYSTEM", M(8), MUTED)
    pill(d, 740, 31, 75, 24, "ONLINE", GREEN, BG, frame)
    txt(d, 832, 38, "21:34", M(10))
    txt(d, 832, 55, "INDORE", M(8), MUTED)

    rr(d, (20, 94, 142, 572), 14, fill=PANEL, outline=LINE)
    txt(d, 40, 113, "NAV", M(8), MUTED)
    nav = [("01", "OVERVIEW", GREEN), ("02", "PROJECTS", CYAN), ("03", "TOOLS", ORANGE), ("04", "BUILDING", PURPLE), ("05", "CONTACT", RED)]
    active = (frame // 15) % 5
    for i, (num, label, accent) in enumerate(nav):
        yy = 150 + i * 62
        if i == active:
            rr(d, (32, yy - 7, 130, yy + 30), 9, fill=(27, 31, 28), outline=(39, 55, 40))
        txt(d, 42, yy, num, M(8), accent if i == active else MUTED)
        txt(d, 69, yy - 1, label, B(9), TEXT if i == active else MUTED)
    marker = 146 + active * 62
    line(d, [(31, marker - 3), (31, marker + 22)], GREEN, 3)

    txt(d, 164, 106, "BUILD / DESIGN / SHIP", B(25))
    txt(d, 165, 139, "A small operating system for the things I'm making.", F(11), MUTED)
    scan = 165 + (frame * 9) % 300
    line(d, [(scan, 153), (scan + 60, 153)], GREEN, 2)

    metrics = [("ACTIVE PROJECTS", "06", GREEN), ("STACK", "24", CYAN), ("AUTOMATIONS", "11", ORANGE), ("STATUS", "SHIPPING", RED)]
    for i, (label, value, accent) in enumerate(metrics):
        x = 164 + i * 183
        rr(d, (x, 172, x + 171, 226), 10, fill=PANEL, outline=LINE)
        txt(d, x + 14, 184, label, M(8), MUTED)
        txt(d, x + 14, 201, value, B(17), accent)
        txt(d, x + 157, 205, "↗", B(14), accent, "ra")

    txt(d, 164, 246, "PROJECTS", B(13), MUTED)
    project_card(d, 164, 270, 235, 98, "BLINKY", "desktop companion", CYAN, frame, 0)
    project_card(d, 412, 270, 235, 98, "CIVIFIX", "civic reporting", GREEN, frame, 1)
    project_card(d, 660, 270, 280, 98, "DAILYS", "workspace / systems", PURPLE, frame, 2)

    draw_graph(d, 164, 386, 490, 167, frame)
    draw_bars(d, 670, 386, 270, 167, frame)

    rr(d, (164, 566, 654, 592), 10, fill=(8, 9, 10), outline=LINE)
    txt(d, 177, 573, "$", M(10), GREEN)
    ticker = ["shipping UI", "syncing automations", "building something weird", "git push --quiet", "design → code → repeat"][(frame // 14) % 5]
    txt(d, 195, 573, ticker, M(10))

    rr(d, (670, 566, 940, 592), 10, fill=PANEL, outline=LINE)
    ring(d, 685, 579, 6, 0.55 + 0.2 * math.sin(frame * 0.18 + 1), GREEN, 2)
    txt(d, 702, 573, "LIVE BUILD", M(9), GREEN)
    txt(d, 920, 573, f"{frame + 1:02d}", M(8), MUTED, "ra")

    for i, (x, y, accent) in enumerate([(610, 115, GREEN), (630, 119, CYAN), (650, 115, ORANGE), (920, 110, RED)]):
        r = 2 + int((frame + i) % 6 == 0)
        d.ellipse((x - r, y - r, x + r, y + r), fill=accent)

    cursor(d, frame)
    return im

frames = [draw(i) for i in range(FRAMES)]
os.makedirs("assets", exist_ok=True)
frames[0].save("assets/dashboard.gif", save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True, disposal=2)
print("wrote assets/dashboard.gif", os.path.getsize("assets/dashboard.gif"))
