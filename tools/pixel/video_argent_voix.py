#!/usr/bin/env python3
"""« 5 règles pour devenir riche dans GTA 6 », calée sur une voix off enregistrée.

Usage : python3 tools/pixel/video_argent_voix.py voix.m4a videos/sortie.mp4
L'enregistrement doit contenir les 16 phrases de SCRIPT, séparées par ~1 s de pause.
"""
import sys, pathlib, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from PIL import Image, ImageDraw
from engine import (LW, LH, W, GROUND_Y, WHITE, font, ease, lerp, sprite, background, coin,
                    money_burst, red_cross, shop, bank, draw_rich, words_caption, fx, flash,
                    badge, render)
from sprites import (PLAYER, PLAYER_WALK, PLAYER_PAL, DEALER, DEALER_PAL, MECHANIC_PAL,
                     BAG, BAG_PAL, PISTOL, PISTOL_PAL, CAR, CAR_PAL, SPORT_PAL)
from voice import build_voice_track
from video_argent import header, big_center, ARROWS, OUTLINE

FEET = GROUND_Y - 8
PY = FEET - 45
CAR_Y = GROUND_Y + 12 - 27

# (n° de scène, texte affiché) — une ligne = une phrase lue
SCRIPT = [
    (0, "Frérot, t'as **GTA 6** ?"),
    (0, "Arrête de perdre ta **thune**. Écoute bien."),
    (1, "**Règle n°1** : ce que tu voles, ça vaut **rien** direct."),
    (1, "Faut le revendre au **receleur**, sinon t'as **zéro**."),
    (2, "**Règle n°2** : commence **petit**."),
    (2, "Les **supérettes**, les **stations-service** : quelques milliers de $, sans prise de tête."),
    (3, "**Règle n°3** : après le **chapitre 2**, tu voles des caisses..."),
    (3, "... et tu les revends à **Moses**."),
    (4, "**Règle n°4** : à la fin du **chapitre 4**, c'est les **coffres des banques**."),
    (4, "Jusqu'à **205 000 $** en 5 minutes. C'est **violent**."),
    (5, "**Règle n°5** : achète **pas** de voiture de luxe au début."),
    (5, "Garde ta **thune** pour ce qui **rapporte**, en vrai."),
    (6, "Et cadeau : le code des **250 000 $**."),
    (6, "Haut, droite, bas, gauche, haut, gauche, bas, droite."),
    (6, "Par contre, il marche qu'après **l'histoire**, hein."),
    (7, "Tous les codes sont sur **Leonida Guide**, lien en bio. Abonne-toi, frérot."),
]
TAIL = 1.2  # secondes gardées après la dernière phrase


def player(img, x, t, walking=False):
    rows = PLAYER_WALK if walking and int(t * 8) % 2 else PLAYER
    sprite(img, rows, PLAYER_PAL, int(x), PY + (0 if walking else int(t * 3) % 2), 3)


# Chaque scène reçoit t (secondes depuis le début de la scène) et L = liste des
# (début, fin) de ses phrases, relatifs au début de la scène.

def intro_low(img, t, L):
    player(img, 72, t)
    for i in range(16):
        coin(img, (i * 37) % 170, int((t * 110 + i * 23) % 150) + 15)


def intro_hi(d, t, L):
    k = ease(t / 0.3)
    draw_rich(d, 330 + (1 - k) * 60, "DEVIENS **RICHE**", 120)
    draw_rich(d, 480 + (1 - k) * 60, "dans GTA 6", 90)


def receleur_low(img, t, L):
    give = L[1][0]
    x = lerp(4, 58, ease(t / 0.9))
    player(img, x, t, walking=t < 0.9)
    sprite(img, DEALER, DEALER_PAL, 128, PY, 3, flip=True)
    bx = int(x) + 30 if t < give else int(lerp(88, 106, ease((t - give) / 0.3)))
    sprite(img, BAG, BAG_PAL, bx, PY + 20, 2)
    if t > give + 0.4:
        money_burst(img, t - give - 0.4, 140, PY, 18, seed=2)


def commerce_low(img, t, L):
    shop(img, 112, FEET - 34)
    x = lerp(4, 62, ease(t / 0.8))
    player(img, x, t, walking=t < 0.8)
    if t > 0.9:
        sprite(img, PISTOL, PISTOL_PAL, int(x) + 33, PY + 22, 2)
    if t > L[1][0]:
        money_burst(img, t - L[1][0], 132, FEET - 30, 12, seed=5)


def voiture_low(img, t, L):
    sprite(img, DEALER, MECHANIC_PAL, 140, PY, 3, flip=True)
    sprite(img, CAR, CAR_PAL, int(lerp(-80, 58, ease(t / 1.0))), CAR_Y, 3)
    if t > L[1][0] + 0.3:
        money_burst(img, t - L[1][0] - 0.3, 156, PY, 18, seed=9)


def banque_low(img, t, L):
    bank(img, 100, FEET - 46, ease((t - 0.2) / 0.8))
    player(img, 20, t)
    if t > L[1][0]:
        money_burst(img, t - L[1][0], 130, FEET - 20, 26, seed=11)


def banque_hi(d, t, L):
    if t > L[1][0]:
        val = int(205000 * ease((t - L[1][0]) / 1.4))
        big_center(d, f"+{val:,} $".replace(",", " "), 330, 120)
        f2 = font(34)
        s = "selon le guide PowerPyx"
        d.text(((W - d.textlength(s, font=f2)) / 2, 480), s, font=f2, fill=WHITE,
               stroke_width=5, stroke_fill=OUTLINE)


def luxe_low(img, t, L):
    sprite(img, CAR, SPORT_PAL, 84, CAR_Y, 3)
    player(img, 14, t)
    if t > 0.9:
        red_cross(img, 120, GROUND_Y - 2, 22, ease((t - 0.9) / 0.2))


def bonus_low(img, t, L):
    player(img, 72, t)
    if t > 0.6:
        money_burst(img, (t - 0.6) % 2, 90, PY, 14, seed=int((t - 0.6) / 2) + 30)


def bonus_hi(d, t, L):
    draw_rich(d, 230, "**BONUS**", 110)
    s, e = L[1]
    if t < s:
        return
    f = font(120)
    shown = min(8, int((t - s) / ((e - s) / 8)) + 1)
    cell = 210
    for i in range(shown):
        row, col = divmod(i, 4)
        x = (W - 4 * cell) / 2 + col * cell
        y = 420 + row * 170
        d.rounded_rectangle([x + 15, y, x + cell - 15, y + 150], radius=30, fill=(26, 16, 38))
        d.text((x + (cell - d.textlength(ARROWS[i], font=f)) / 2, y + 8), ARROWS[i], font=f, fill=WHITE)


def outro_low(img, t, L):
    player(img, 72, t)
    money_burst(img, t % 1.5, 90, PY, 12, seed=int(t / 1.5) + 20)


def outro_hi(d, t, L):
    k = ease(t / 0.3)
    draw_rich(d, 330 + (1 - k) * 50, "Tout est sur", 80)
    draw_rich(d, 450 + (1 - k) * 50, "**Leonida Guide**", 115)


SCENES = [
    dict(low=intro_low, hi=intro_hi),
    dict(low=receleur_low, n=1, shake=lambda t, L: L[1][0] + 0.4 <= t <= L[1][0] + 1.0),
    dict(low=commerce_low, n=2, shake=lambda t, L: L[1][0] <= t <= L[1][0] + 0.5),
    dict(low=voiture_low, n=3, shake=lambda t, L: L[1][0] + 0.3 <= t <= L[1][0] + 0.9),
    dict(low=banque_low, hi=banque_hi, n=4, shake=lambda t, L: L[1][0] <= t <= L[1][0] + 0.8),
    dict(low=luxe_low, n=5),
    dict(low=bonus_low, hi=bonus_hi),
    dict(low=outro_low, hi=outro_hi),
]


def make_drawer(timeline):
    """timeline : (début, fin) de chaque phrase dans la piste voix."""
    total = timeline[-1][1] + TAIL
    starts = []
    for k in range(len(SCENES)):
        first = next(i for i, (sc, _) in enumerate(SCRIPT) if sc == k)
        starts.append(0.0 if k == 0 else timeline[first][0] - 0.05)

    def draw(t):
        k = max(i for i, st in enumerate(starts) if st <= t)
        sc, lt = SCENES[k], t - starts[k]
        idxs = [i for i, (s, _) in enumerate(SCRIPT) if s == k]
        L = [(timeline[i][0] - starts[k], timeline[i][1] - starts[k]) for i in idxs]
        # phrase en cours (la dernière commencée)
        cur = max([j for j, (s, e) in enumerate(L) if s <= lt] or [0])
        text = SCRIPT[idxs[cur]][1]
        s, e = L[cur]
        n_words = len(text.replace("**", "").split())
        delay = max(0.06, (e - s) / max(1, n_words) * 0.85)
        low = Image.new("RGB", (LW, LH))
        background(low, t)
        sc["low"](low, lt, L)
        shake = 2.0 if sc.get("shake") and sc["shake"](lt, L) else 0.0
        low = fx(low, lt - max(0.0, s), shake, t)
        if k > 0:
            low = flash(low, 1 - lt / 0.12)
        hi = low.resize((LW * 6, LH * 6), Image.NEAREST)
        d = ImageDraw.Draw(hi)
        if sc.get("n"):
            header(d)
            badge(d, sc["n"], ease(lt / 0.2))
        if sc.get("hi"):
            sc["hi"](d, lt, L)
        size = 96 if len(text) < 45 else 80
        words_caption(d, text, lt - max(0.0, s), size=size, delay=delay)
        return hi

    return draw, total


if __name__ == "__main__":
    voice_in, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = pathlib.Path(tmp) / "voix.wav"
        timeline = build_voice_track(voice_in, len(SCRIPT), wav)
        draw, total = make_drawer(timeline)
        render(out, total, draw, audio=wav)
    print(f"Vidéo créée : {out} ({total:.1f} s)")
