"""Mini moteur de vidéos TikTok en pixel art (1080x1920).

Le décor et les personnages sont dessinés sur une petite toile (180x320), agrandie x6
sans lissage pour l'effet pixel. Les textes sont ajoutés ensuite en pleine résolution.
"""
import math, random, subprocess
from PIL import Image, ImageDraw, ImageFont

LW, LH, SCALE = 180, 320, 6
W, H, FPS = LW * SCALE, LH * SCALE, 30
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
YELLOW = (255, 226, 90)
WHITE = (255, 255, 255)
GROUND_Y = 214  # ligne du trottoir sur la petite toile

_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(BOLD, size)
    return _fonts[size]


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def lerp(a, b, k):
    return a + (b - a) * k


# ---------- dessin sur la petite toile ----------

def sprite(img, rows, pal, x, y, s=2, flip=False):
    """Dessine un sprite ; (x, y) = coin haut-gauche, s = taille d'un pixel du sprite."""
    d = ImageDraw.Draw(img)
    for j, row in enumerate(rows):
        if flip:
            row = row[::-1]
        for i, ch in enumerate(row):
            if ch == ".":
                continue
            c = pal.get(ch)
            if c is None:
                continue
            px, py = int(x + i * s), int(y + j * s)
            d.rectangle([px, py, px + s - 1, py + s - 1], fill=c)


def sprite_size(rows, s=2):
    return len(rows[0]) * s, len(rows) * s


SKY = [(255, 150, 70), (252, 120, 80), (240, 92, 110), (214, 70, 130),
       (170, 60, 150), (120, 50, 150), (80, 40, 130)]


def background(img, t, night=False):
    d = ImageDraw.Draw(img)
    sky = SKY if not night else [(30, 25, 70), (40, 30, 85), (50, 35, 100), (60, 40, 110),
                                 (70, 45, 120), (55, 35, 100), (40, 28, 80)]
    band = 30
    for i, c in enumerate(sky):
        d.rectangle([0, i * band, LW, (i + 1) * band], fill=c)
    # soleil (ou lune) à rayures
    cx, cy, r = 130, 70, 22
    sun = (255, 220, 110) if not night else (235, 235, 245)
    for yy in range(-r, r + 1):
        if not night and yy > 6 and (yy // 3) % 2 == 0:
            continue
        w = int(math.sqrt(max(0, r * r - yy * yy)))
        d.line([cx - w, cy + yy, cx + w, cy + yy], fill=sun)
    # étoiles la nuit
    if night:
        rnd = random.Random(3)
        for _ in range(40):
            sx, sy = rnd.randrange(LW), rnd.randrange(150)
            if (int(t * 3) + sx) % 5:
                d.point((sx, sy), fill=(255, 255, 255))
    # immeubles
    rnd = random.Random(7)
    x = -4
    while x < LW:
        bw, bh = rnd.randint(12, 24), rnd.randint(40, 110)
        top = GROUND_Y - 8 - bh
        col = (60, 30, 90) if not night else (25, 20, 45)
        d.rectangle([x, top, x + bw, GROUND_Y - 8], fill=col)
        for wy in range(top + 4, GROUND_Y - 12, 6):
            for wx in range(x + 3, x + bw - 2, 5):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 1, wy + 2], fill=(255, 200, 120) if night or rnd.random() < .5 else (150, 90, 160))
        x += bw + rnd.randint(1, 4)
    # palmiers
    from sprites import PALM, PALM_PAL
    for px in (6, 150):
        sprite(img, PALM, PALM_PAL, px, GROUND_Y - 8 - 36, 2)
    # trottoir + route
    d.rectangle([0, GROUND_Y - 8, LW, GROUND_Y + 2], fill=(150, 140, 160))
    d.rectangle([0, GROUND_Y + 2, LW, GROUND_Y + 30], fill=(55, 50, 65))
    off = int(t * 40) % 20
    for xx in range(-20, LW, 20):
        d.rectangle([xx + off, GROUND_Y + 15, xx + off + 9, GROUND_Y + 16], fill=(250, 210, 70))
    # panneau sombre pour les sous-titres
    d.rectangle([0, GROUND_Y + 30, LW, LH], fill=(26, 16, 38))


def rect(img, box, fill):
    ImageDraw.Draw(img).rectangle(box, fill=fill)


def coin(img, x, y):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + 4, y + 4], fill=(250, 200, 40))
    d.rectangle([x + 1, y + 1, x + 3, y + 3], fill=(255, 235, 120))


def bill(img, x, y):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + 8, y + 4], fill=(30, 110, 50))
    d.rectangle([x + 1, y + 1, x + 7, y + 3], fill=(90, 190, 100))
    d.point((x + 4, y + 2), fill=(30, 110, 50))


def money_burst(img, t, x, y, n=14, seed=1):
    """Billets qui jaillissent puis retombent (t en secondes depuis le début)."""
    rnd = random.Random(seed)
    for i in range(n):
        delay = i * 0.06
        tt = t - delay
        if tt < 0:
            continue
        vx = rnd.uniform(-30, 30)
        vy = rnd.uniform(-90, -60)
        px = x + vx * tt
        py = y + vy * tt + 70 * tt * tt
        if py < LH:
            bill(img, int(px), int(py))


def red_cross(img, cx, cy, r, k=1.0):
    d = ImageDraw.Draw(img)
    rr = int(r * k)
    for o in range(-2, 3):
        d.line([cx - rr + o, cy - rr, cx + rr + o, cy + rr], fill=(230, 30, 40))
        d.line([cx + rr + o, cy - rr, cx - rr + o, cy + rr], fill=(230, 30, 40))


def shop(img, x, y):
    """Supérette : 44x34, (x, y) = haut-gauche."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + 44, y + 34], fill=(235, 225, 200))
    for i in range(0, 44, 4):
        d.rectangle([x + i, y + 8, x + i + 1, y + 13], fill=(220, 50, 60))
        d.rectangle([x + i + 2, y + 8, x + i + 3, y + 13], fill=(255, 255, 255))
    d.rectangle([x + 4, y + 1, x + 40, y + 7], fill=(40, 160, 90))
    d.rectangle([x + 4, y + 17, x + 22, y + 30], fill=(140, 200, 230))
    d.rectangle([x + 28, y + 17, x + 39, y + 34], fill=(90, 60, 50))


def bank(img, x, y, door_open=0.0):
    """Banque 60x46 avec coffre ; door_open de 0 à 1."""
    d = ImageDraw.Draw(img)
    d.polygon([(x, y + 10), (x + 30, y), (x + 60, y + 10)], fill=(225, 215, 190))
    d.rectangle([x, y + 10, x + 60, y + 14], fill=(205, 195, 170))
    d.rectangle([x + 2, y + 14, x + 58, y + 46], fill=(240, 232, 210))
    for cxx in (6, 16, 44, 54):
        d.rectangle([x + cxx - 2, y + 15, x + cxx + 1, y + 44], fill=(210, 200, 175))
    # coffre
    vx, vy = x + 30, y + 31
    d.ellipse([vx - 10, vy - 10, vx + 10, vy + 10], fill=(60, 60, 70))
    d.ellipse([vx - 8, vy - 8, vx + 8, vy + 8], fill=(255, 210, 80) if door_open > 0.5 else (140, 140, 155))
    if door_open <= 0.5:
        a = door_open * 12
        for k in range(4):
            ang = a + k * math.pi / 2
            d.line([vx, vy, vx + 6 * math.cos(ang), vy + 6 * math.sin(ang)], fill=(60, 60, 70))
    else:
        for k in range(5):
            bill(img, vx - 7 + (k % 3) * 4, vy - 5 + (k // 3) * 5)
    d.rectangle([x, y + 44, x + 60, y + 46], fill=(190, 180, 155))


# ---------- texte pleine résolution ----------

def draw_rich(d, y, line, size, center=True, x=None, stroke=10):
    """Écrit une ligne ; les mots entre **…** sont en jaune."""
    parts = []
    for i, seg in enumerate(line.split("**")):
        if seg:
            parts.append((seg, YELLOW if i % 2 else WHITE))
    f = font(size)
    total = sum(d.textlength(s, font=f) for s, _ in parts)
    cx = (W - total) / 2 if center else x
    for s, col in parts:
        d.text((cx, y), s, font=f, fill=col, stroke_width=stroke, stroke_fill=(10, 5, 20))
        cx += d.textlength(s, font=f)


def wrap(d, text, size, maxw=960):
    """Coupe un texte en lignes (en gardant les marqueurs ** valides par ligne)."""
    f = font(size)
    words, lines, cur = text.split(" "), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if d.textlength(test.replace("**", ""), font=f) > maxw and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = test
    if cur:
        lines.append(cur)
    # rééquilibre les ** coupés entre deux lignes
    fixed, open_ = [], False
    for ln in lines:
        if open_:
            ln = "**" + ln
        open_ = ln.count("**") % 2 == 1
        if open_:
            ln = ln + "**"
        fixed.append(ln)
    return fixed


def caption(d, text, y=1500, size=72):
    for i, ln in enumerate(wrap(d, text, size)):
        draw_rich(d, y + i * (size + 22), ln, size)


WORD_DELAY = 0.11  # secondes entre deux mots qui apparaissent


def words_caption(d, text, lt, y=1430, size=96, maxw=980):
    """Sous-titres mot par mot (style karaoké). lt = secondes depuis le début de la phrase.
    Les mots entre **…** sont en jaune ; le dernier mot apparu « saute » légèrement."""
    toks = []
    for i, seg in enumerate(text.split("**")):
        for w_ in seg.split():
            toks.append((w_, i % 2 == 1))
    shown = min(len(toks), int(lt / WORD_DELAY) + 1)
    f = font(size)
    space = d.textlength(" ", font=f)
    # mise en page de toutes les lignes (pour que le texte ne bouge pas)
    lines, cur, cw = [], [], 0
    for w_, h in toks:
        ww = d.textlength(w_, font=f)
        if cur and cw + space + ww > maxw:
            lines.append((cur, cw))
            cur, cw = [], 0
        cw = cw + (space if cur else 0) + ww
        cur.append((w_, h, ww))
    if cur:
        lines.append((cur, cw))
    idx = 0
    for li, (ws, lw) in enumerate(lines):
        x = (W - lw) / 2
        for w_, h, ww in ws:
            if idx < shown:
                pop = 1.0 if idx < shown - 1 else ease((lt - idx * WORD_DELAY) / 0.12)
                yy = y + li * (size + 26) + (1 - pop) * 18
                d.text((x, yy), w_, font=f, fill=YELLOW if h else WHITE,
                       stroke_width=12, stroke_fill=(10, 5, 20))
            x += ww + space
            idx += 1


def fx(low, t_since_cut, shake=0.0, t=0.0):
    """Effets sur la petite toile : zoom rapide après chaque coupe + tremblement.
    Renvoie une image de même taille."""
    z = 1 + 0.07 * max(0.0, 1 - t_since_cut / 0.25)
    ox = int(round(shake * math.sin(t * 90)))
    oy = int(round(shake * math.cos(t * 77)))
    if z <= 1.001 and ox == 0 and oy == 0:
        return low
    cw, ch = LW / z, LH / z
    left = (LW - cw) / 2 + ox
    top = (LH - ch) / 2 + oy
    return low.crop((int(left), int(top), int(left + cw), int(top + ch))).resize((LW, LH), Image.NEAREST)


def flash(img, k):
    """Flash blanc (k de 1 à 0)."""
    if k <= 0:
        return img
    return Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), min(1.0, k) * 0.85)


def badge(d, n, k=1.0):
    """Grand numéro d'étape en haut à gauche."""
    f = font(150)
    d.text((70, 150 - (1 - k) * 60), str(n), font=f, fill=YELLOW,
           stroke_width=14, stroke_fill=(10, 5, 20))


# ---------- rendu ----------

def render(out, duration, draw_frame):
    """draw_frame(t) -> PIL Image 1080x1920 RGB."""
    n = int(duration * FPS)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(draw_frame(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    if p.returncode:
        raise SystemExit("ffmpeg a échoué")
