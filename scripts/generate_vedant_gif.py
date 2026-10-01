from PIL import Image, ImageDraw, ImageFont
import numpy as np, cv2, os

W, H = 1000, 560
FRAMES, FPS = 72, 18
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font = ImageFont.truetype(font_path, 185)

mask = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(mask)
word = "vedant"
box = d.textbbox((0, 0), word, font=font)
tw, th = box[2] - box[0], box[3] - box[1]
d.text(((W - tw) // 2, (H - th) // 2 - 18), word, font=font, fill=255)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cx, cy = W / 2, H / 2
frames = []

for i in range(FRAMES):
    t = i / FRAMES * 2 * np.pi
    dx = 22 * np.sin(yy / 58 + t * 1.15) + 10 * np.sin(yy / 31 - t * 1.7)
    dy = 14 * np.sin(xx / 76 + t) + 8 * np.sin(xx / 39 - t * 1.4)

    for bx, by, amp, phase in [
        (cx - 180, cy, 30, 0.0),
        (cx, cy - 8, 38, 1.8),
        (cx + 175, cy + 2, 30, 3.0),
    ]:
        g = np.exp(-(((xx - bx) / 125) ** 2 + ((yy - by) / 115) ** 2))
        dx += amp * g * np.sin(t + phase)
        dy += amp * 0.62 * g * np.cos(t + phase)

    mx = np.clip(xx + dx, 0, W - 1)
    my = np.clip(yy + dy, 0, H - 1)
    warped = cv2.remap(np.asarray(mask), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    warped = cv2.GaussianBlur(warped, (0, 0), 0.3)

    frame = np.full((H, W, 3), (12, 12, 12), dtype=np.uint8)
    frame[warped > 10] = (247, 247, 245)
    frames.append(Image.fromarray(frame).convert("P", palette=Image.Palette.ADAPTIVE))

os.makedirs("assets", exist_ok=True)
out = "assets/vedant.gif"
frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(1000 / FPS), loop=0, optimize=True, disposal=2)
print(out, os.path.getsize(out))
