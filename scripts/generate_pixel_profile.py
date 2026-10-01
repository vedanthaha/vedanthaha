from PIL import Image, ImageDraw, ImageFont
import math, os

# Full-page hand-drawn doodle animation.
# The stickman is not trapped in one banner: it travels through the whole
# profile, touching sections, moving objects, dragging data, typing, and waving.
# Everything is rendered as smooth line art; there is no pixel-art scaling.

W, H = 520, 1100
FRAMES = 32
DURATION = 100

BG = (248, 246, 238)
PAPER = (255, 254, 250)
INK = (27, 28, 26)
MUTED = (115, 114, 106)
GREEN = (81, 139, 72)
BLUE = (76, 111, 154)
RED = (176, 78, 69)
YELLOW = (200, 163, 67)
PURPLE = (126, 99, 145)
LINE = (224, 221, 211)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = lambda n: ImageFont.truetype(FONT, n)
B = lambda n: ImageFont.truetype(BOLD, n)


def P(x, y):
    return (float(x), float(y))


def line(d, pts, c=INK, w=3):
    d.line([(int(a), int(b)) for a, b in pts], fill=c, width=w, joint="curve")


def txt(d, p, s, font, c=INK):
    d.text((int(p[0]), int(p[1])), s, font=font, fill=c)


def box(d, x, y, w, h, fill=PAPER, outline=INK, wid=2, r=6):
    d.rounded_rectangle(
        (x, y, x + w, y + h),
        radius=r,
        fill=fill,
        outline=outline,
        width=wid,
    )


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def arrow(d, a, b, c=INK):
    line(d, [a, b], c, 2)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for z in (2.55, -2.55):
        line(
            d,
            [
                b,
                (
                    b[0] + math.cos(ang + z) * 8,
                    b[1] + math.sin(ang + z) * 8,
                ),
            ],
            c,
            2,
        )


def sticker(d, x, y, w, h, label, accent, phase):
    x += math.sin(phase * 0.7) * 1.5
    y += math.sin(phase) * 2
    box(d, x + 3, y + 3, w, h, fill=INK, outline=INK, wid=2, r=8)
    box(d, x, y, w, h, fill=PAPER, outline=INK, wid=2, r=8)
    txt(d, P(x + 9, y + 7), label, B(10))
    line(d, [P(x + 8, y + h - 7), P(x + w - 8, y + h - 7)], accent, 2)


def stickman(d, x, y, pose, phase=0):
    head = (x, y - 72)
    neck = (x, y - 59)
    hip = (x, y - 23)

    d.ellipse(
        (head[0] - 13, head[1] - 13, head[0] + 13, head[1] + 13),
        fill=PAPER,
        outline=INK,
        width=3,
    )
    d.ellipse((x - 5, head[1] - 2, x - 2, head[1] + 1), fill=INK)
    d.ellipse((x + 2, head[1] - 2, x + 5, head[1] + 1), fill=INK)
    line(d, [P(*neck), P(*hip)], INK, 4)

    if pose == "type":
        tap = 2 if int(phase * 8) % 2 == 0 else 0
        line(d, [P(x, y - 52), P(x + 18, y - 41), P(x + 42, y - 41 + tap)], INK, 4)
        line(d, [P(x, y - 52), P(x + 12, y - 39), P(x + 35, y - 39 - tap)], INK, 4)
        line(d, [P(*hip), P(x - 9, y - 4)], INK, 4)
        line(d, [P(*hip), P(x + 10, y - 4)], INK, 4)

    elif pose == "pull":
        line(d, [P(x, y - 52), P(x + 18, y - 44), P(x + 48, y - 44)], INK, 4)
        line(d, [P(x, y - 52), P(x + 17, y - 36), P(x + 48, y - 36)], INK, 4)
        line(d, [P(*hip), P(x - 11, y - 4)], INK, 4)
        line(d, [P(*hip), P(x + 10, y - 4)], INK, 4)

    elif pose == "wave":
        lift = math.sin(phase * 5) * 3
        line(d, [P(x, y - 52), P(x - 16, y - 40), P(x - 24, y - 27)], INK, 4)
        line(d, [P(x, y - 52), P(x + 13, y - 40), P(x + 16, y - 70 + lift)], INK, 4)
        line(d, [P(*hip), P(x - 9, y - 4)], INK, 4)
        line(d, [P(*hip), P(x + 9, y - 4)], INK, 4)

    elif pose == "sit":
        line(d, [P(*hip), P(x + 16, y - 22), P(x + 28, y - 4)], INK, 4)
        line(d, [P(*hip), P(x + 28, y - 5), P(x + 47, y - 4)], INK, 4)
        line(d, [P(x, y - 52), P(x + 17, y - 42), P(x + 38, y - 42)], INK, 4)
        line(d, [P(x, y - 52), P(x + 12, y - 39), P(x + 33, y - 40)], INK, 4)

    else:
        step = 6 if int(phase * 8) % 2 == 0 else -6
        line(d, [P(x, y - 52), P(x - 17, y - 39), P(x - 22, y - 25)], INK, 4)
        line(d, [P(x, y - 52), P(x + 17, y - 39), P(x + 22, y - 25)], INK, 4)
        line(d, [P(*hip), P(x - 9 + step, y - 4)], INK, 4)
        line(d, [P(*hip), P(x + 9 - step, y - 4)], INK, 4)


def laptop(d, x, y, frame):
    box(d, x, y, 100, 58, fill=PAPER, wid=3)
    box(d, x + 8, y + 7, 84, 39, fill=(242, 244, 237), wid=2, r=3)
    txt(d, P(x + 12, y + 11), "~/vedant", B(9), MUTED)

    for i, w in enumerate((28, 40, 24, 52)):
        line(
            d,
            [
                P(x + 12, y + 26 + i * 6),
                P(
                    x + 12 + w + (2 if i == 2 and frame % 4 < 2 else 0),
                    y + 26 + i * 6,
                ),
            ],
            GREEN if i == 2 else INK,
            3,
        )

    cx = x + 15 + (frame * 5) % 68
    cy = y + 24 + ((frame // 5) % 4) * 6
    line(d, [P(cx, cy), P(cx, cy + 5)], RED, 2)
    line(d, [P(x - 8, y + 62), P(x + 108, y + 62)], INK, 5)


def mini_graph(d, x, y, frame, drag=0):
    box(d, x, y, 102, 66, wid=2)
    txt(d, P(x + 8, y + 8), "ACTIVITY", B(9))
    pts = []
    for i in range(8):
        pts.append(
            P(
                x + 10 + i * 12 + drag,
                y + 48 - 12 * math.sin(i * 0.8 + frame * 0.05) - 3 * math.sin(i),
            )
        )
    line(d, pts, BLUE, 3)
    for px, py in pts[::2]:
        d.ellipse((px - 2, py - 2, px + 2, py + 2), fill=RED, outline=INK, width=1)


def draw(frame):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    # Paper rules / sketchbook feel.
    for yy in range(0, H, 40):
        line(d, [P(0, yy), P(W, yy)], LINE, 1)

    # HERO
    txt(d, P(26, 20), "VEDANT", B(42))
    txt(d, P(28, 68), "developer · designer · builder", F(14), MUTED)
    line(d, [P(28, 92), P(180, 92)], GREEN, 3)
    sticker(d, 315, 24, 74, 30, "BUILD", GREEN, frame * 0.2)
    sticker(d, 402, 58, 84, 30, "DESIGN", BLUE, frame * 0.2 + 1)

    # ABOUT
    txt(d, P(26, 132), "ABOUT", B(18), MUTED)
    box(d, 25, 160, 470, 102, wid=2)
    txt(d, P(42, 180), "I build software, interfaces, automations", F(15))
    txt(d, P(42, 204), "and weird little experiments.", F(15))

    # PROJECTS
    txt(d, P(26, 292), "PROJECTS", B(18), MUTED)
    for label, accent, x in [
        ("CIVIFIX", GREEN, 30),
        ("BLINKY", BLUE, 188),
        ("DAILYS", PURPLE, 346),
    ]:
        box(d, x, 324, 142, 84, wid=2)
        txt(d, P(x + 14, 342), label, B(15))
        line(d, [P(x + 14, 370), P(x + 112, 370)], accent, 3)
        txt(d, P(x + 14, 386), "build / ship / iterate", F(9), MUTED)

    # STACK
    txt(d, P(26, 444), "STACK", B(18), MUTED)
    for i, label in enumerate(["REACT", "TS", "PYTHON", "SUPABASE", "N8N", "FIGMA"]):
        x = 30 + (i % 3) * 156
        yy = 480 + (i // 3) * 48
        box(d, x, yy, 130, 34, wid=2)
        txt(d, P(x + 12, yy + 9), label, B(10))

    # STATS
    txt(d, P(26, 594), "BUILDING IN PUBLIC", B(18), MUTED)
    box(d, 26, 628, 210, 100, wid=2)
    txt(d, P(40, 644), "commits", B(11))
    for i, value in enumerate([42, 55, 49, 71, 63, 82, 75, 90]):
        line(d, [P(40 + i * 20, 710), P(40 + i * 20, 710 - 52 * value / 100)], GREEN, 8)

    graph_drag = ease((frame - 20) / 4) * 18 if 20 <= frame < 24 else 0
    mini_graph(d, 260, 628, frame, graph_drag)

    # CURRENTLY BUILDING
    txt(d, P(26, 760), "CURRENTLY BUILDING", B(18), MUTED)
    box(d, 26, 794, 470, 130, wid=2)
    laptop(d, 62, 828, frame)
    sticker(d, 306, 812, 136, 32, "AUTOMATION", YELLOW, frame * 0.18)
    txt(d, P(310, 858), "n8n · AI · systems", B(10), MUTED)

    # CONTACT
    txt(d, P(26, 960), "LET'S BUILD", B(28))
    txt(d, P(28, 1005), "github.com/vedanthaha", F(12), MUTED)
    line(
        d,
        [P(28 + i * 4, 1040 + math.sin(i * 0.6 + frame * 0.15) * 3) for i in range(50)],
        RED,
        3,
    )

    for sep in (276, 436, 586, 752, 950):
        line(d, [P(20, sep), P(500, sep)], INK, 2)

    # The same little character travels through the whole page.
    if frame < 5:
        q = frame / 4
        x = 5 + 130 * ease(q)
        y = 112
        pose = "walk"
        txt(d, P(255, 100), "hey.", B(14), MUTED)

    elif frame < 9:
        q = (frame - 5) / 4
        x = 135
        y = 120 + 35 * ease(q)
        pose = "walk"

    elif frame < 16:
        q = (frame - 9) / 7
        x = 135 + 220 * ease(q)
        y = 238
        pose = "walk"
        arrow(d, P(285, 300), P(310, 320), GREEN)

    elif frame < 20:
        q = (frame - 16) / 4
        x = 355
        y = 420 + 55 * ease(q)
        pose = "walk"

    elif frame < 24:
        q = (frame - 20) / 4
        x = 355 - 170 * ease(q)
        y = 580 + 50 * ease(q)
        pose = "pull"
        txt(d, P(112, 740), "dragging data", B(9), BLUE)

    elif frame < 28:
        q = (frame - 24) / 4
        x = 185 + 90 * ease(q)
        y = 728
        pose = "type"

    else:
        q = (frame - 28) / 3
        x = 275
        y = 930 - 95 * ease(q)
        pose = "wave"
        sticker(d, 330, 880, 94, 30, "SHIPPED", GREEN, frame * 0.2)

    stickman(d, x, y, pose, frame / FRAMES * math.pi * 2)

    # A little object follows the character's hand during the project pass.
    if 9 <= frame < 16:
        px = x + 35
        py = y - 46
        d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=YELLOW, outline=INK, width=2)

    # Roaming cursor makes the whole page feel alive.
    cx = 40 + (frame * 17) % 420
    cy = 280 + 10 * math.sin(frame * 0.35)
    line(d, [P(cx, cy), P(cx + 9, cy + 4), P(cx + 4, cy + 12)], INK, 2)

    return im


frames = [draw(i) for i in range(FRAMES)]
os.makedirs("assets", exist_ok=True)

frames[0].save(
    "assets/profile.gif",
    save_all=True,
    append_images=frames[1:],
    duration=DURATION,
    loop=0,
    optimize=True,
    disposal=2,
)

print("wrote assets/profile.gif", os.path.getsize("assets/profile.gif"))
