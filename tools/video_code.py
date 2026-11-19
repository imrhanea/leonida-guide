#!/usr/bin/env python3
"""Génère une vidéo TikTok verticale (1080x1920) « code de triche » sans aucune image tierce.

Usage : python3 tools/video_code.py sortie.mp4
Les textes et le code sont définis dans SCENES ci-dessous.
"""
import subprocess, sys, tempfile, pathlib, math
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

TITLE = ["Le code des", "250 000 $", "dans GTA 6"]
CODE = ["↑", "→", "↓", "←", "↑", "←", "↓", "→"]
WARNING = ["⚠️ MAIS", "il ne marche qu'après", "avoir FINI l'histoire"]
WARNING[0] = "MAIS ATTENTION"
END = ["Les 61 codes", "+ comment les débloquer", "→ Leonida Guide", "(lien en bio)"]

# Timeline (secondes)
T_TITLE = (0.0, 2.6)
T_CODE = (2.6, 8.2)
T_WARN = (8.2, 11.0)
T_END = (11.0, 14.0)
DURATION = T_END[1]


def gradient(t):
    """Fond dégradé coucher de soleil qui bouge doucement."""
    img = Image.new("RGB", (W, H))
    px = img.load()
    shift = 0.08 * math.sin(t * 0.8)
    top = (255, 138, 61)
    mid = (230, 51, 122)
    bot = (82, 39, 170)
    rows = []
    for y in range(H):
        f = min(1, max(0, y / H + shift))
        if f < 0.55:
            k = f / 0.55
            c = tuple(int(top[i] + (mid[i] - top[i]) * k) for i in range(3))
        else:
            k = (f - 0.55) / 0.45
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * k) for i in range(3))
        rows.append(c)
    d = ImageDraw.Draw(img)
    for y, c in enumerate(rows):
        d.line([(0, y), (W, y)], fill=c)
    return img


def ease(x):
    x = min(1, max(0, x))
    return 1 - (1 - x) ** 3


def centered(d, y, text, font, fill=(255, 255, 255), alpha=1.0, base=None):
    w = d.textlength(text, font=font)
    x = (W - w) / 2
    # ombre
    d.text((x + 4, y + 6), text, font=font, fill=(0, 0, 0, int(110 * alpha)))
    d.text((x, y), text, font=font, fill=fill + (int(255 * alpha),))


def frame(t, bg_cache):
    key = round(t * 4) / 4  # fond recalculé 4 fois par seconde
    if key not in bg_cache:
        bg_cache[key] = gradient(key)
    img = bg_cache[key].copy().convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f_big = ImageFont.truetype(BOLD, 150)
    f_mid = ImageFont.truetype(BOLD, 84)
    f_small = ImageFont.truetype(REG, 58)
    f_arrow = ImageFont.truetype(BOLD, 150)

    # Marque en haut
    centered(d, 120, "LEONIDA GUIDE", ImageFont.truetype(BOLD, 46), alpha=0.85)

    if T_TITLE[0] <= t < T_TITLE[1]:
        k = ease((t - T_TITLE[0]) / 0.5)
        y0 = 620 + (1 - k) * 80
        centered(d, y0, TITLE[0], f_mid, alpha=k)
        centered(d, y0 + 120, TITLE[1], f_big, fill=(255, 236, 120), alpha=k)
        centered(d, y0 + 310, TITLE[2], f_mid, alpha=k)

    elif T_CODE[0] <= t < T_CODE[1]:
        centered(d, 360, "Sors le téléphone,", f_small)
        centered(d, 440, "maintiens L1 + appuie sur R1,", f_small)
        centered(d, 520, "puis tape :", f_small)
        per = (T_CODE[1] - T_CODE[0] - 1.2) / len(CODE)
        shown = (t - T_CODE[0]) / per
        # 2 lignes de 4 flèches
        cell = 200
        for i, a in enumerate(CODE):
            k = ease(shown - i)
            if k <= 0:
                continue
            row, col = divmod(i, 4)
            x = (W - 4 * cell) / 2 + col * cell
            y = 780 + row * 260 + (1 - k) * 60
            d.rounded_rectangle([x + 15, y, x + cell - 15, y + 200], radius=36,
                                fill=(0, 0, 0, int(90 * k)))
            aw = d.textlength(a, font=f_arrow)
            d.text((x + (cell - aw) / 2, y + 12), a, font=f_arrow, fill=(255, 255, 255, int(255 * k)))
        centered(d, 1400, "= 250 000 $", f_mid, fill=(255, 236, 120), alpha=ease(shown - len(CODE)))

    elif T_WARN[0] <= t < T_WARN[1]:
        k = ease((t - T_WARN[0]) / 0.4)
        centered(d, 640, WARNING[0], f_mid, fill=(255, 236, 120), alpha=k)
        centered(d, 820, WARNING[1], f_small, alpha=k)
        centered(d, 910, WARNING[2], ImageFont.truetype(BOLD, 70), alpha=k)
        centered(d, 1120, "et ça désactive la sauvegarde", f_small, alpha=k)
        centered(d, 1200, "et les trophées", f_small, alpha=k)

    else:
        k = ease((t - T_END[0]) / 0.5)
        centered(d, 640, END[0], f_mid, alpha=k)
        centered(d, 760, END[1], f_small, alpha=k)
        centered(d, 960, END[2], ImageFont.truetype(BOLD, 96), fill=(255, 236, 120), alpha=k)
        centered(d, 1110, END[3], f_small, alpha=k)

    return Image.alpha_composite(img, layer).convert("RGB")


def main(out):
    out = pathlib.Path(out)
    with tempfile.TemporaryDirectory() as tmp:
        cache = {}
        n = int(DURATION * FPS)
        for i in range(n):
            frame(i / FPS, cache).save(f"{tmp}/f{i:05d}.png")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", str(FPS), "-i", f"{tmp}/f%05d.png",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-c:a", "aac", "-movflags", "+faststart", str(out)], check=True)
    print("Vidéo créée :", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "videos/code-250000.mp4")
