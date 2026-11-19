#!/usr/bin/env python3
"""Vidéo pixel art RAPIDE : « 5 règles pour devenir riche dans GTA 6 » (~38 s).

Rythme TikTok : une règle toutes les ~5 s, sous-titres mot par mot, zoom à chaque phrase,
tremblement quand l'argent jaillit, flash entre les scènes.

Usage :
  python3 tools/pixel/video_argent.py videos/pixel-argent.mp4
  python3 tools/pixel/video_argent.py videos/x.mp4 --preview 2 10 20   (images fixes)
Écrit aussi le texte de la voix off (.txt) à côté de la vidéo.
Infos : uniquement celles vérifiées sur la page argent du site.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from PIL import Image, ImageDraw
from engine import (LW, LH, W, GROUND_Y, WHITE, YELLOW, font, ease, lerp, sprite,
                    background, coin, money_burst, red_cross, shop, bank,
                    draw_rich, words_caption, fx, flash, badge, render)
from sprites import (PLAYER, PLAYER_WALK, PLAYER_PAL, DEALER, DEALER_PAL, MECHANIC_PAL,
                     BAG, BAG_PAL, PISTOL, PISTOL_PAL, CAR, CAR_PAL, SPORT_PAL)

FEET = GROUND_Y - 8
PY = FEET - 45          # haut d'un personnage (15 lignes x 3)
CAR_Y = GROUND_Y + 12 - 27
OUTLINE = (10, 5, 20)


def player(img, x, t, walking=False):
    rows = PLAYER_WALK if walking and int(t * 8) % 2 else PLAYER
    bob = 0 if walking else int(t * 3) % 2
    sprite(img, rows, PLAYER_PAL, int(x), PY + bob, 3)


def header(d, text="DEVENIR RICHE DANS GTA 6"):
    f = font(44)
    d.text(((W - d.textlength(text, font=f)) / 2, 70), text, font=f, fill=WHITE,
           stroke_width=6, stroke_fill=OUTLINE)


def big_center(d, text, y, size, color=YELLOW):
    f = font(size)
    d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=color,
           stroke_width=12, stroke_fill=OUTLINE)


# ---------------- scènes (actions dans la 1re seconde) ----------------
# shake(t) : intensité du tremblement à l'instant t de la scène

def intro_low(img, t):
    player(img, 72, t)
    for i in range(16):
        coin(img, (i * 37) % 170, int((t * 110 + i * 23) % 150) + 15)


def intro_hi(d, t):
    k = ease(t / 0.3)
    draw_rich(d, 330 + (1 - k) * 60, "DEVIENS **RICHE**", 120)
    draw_rich(d, 480 + (1 - k) * 60, "dans GTA 6", 90)


def receleur_low(img, t):
    x = lerp(4, 58, ease(t / 0.9))
    player(img, x, t, walking=t < 0.9)
    sprite(img, DEALER, DEALER_PAL, 128, PY, 3, flip=True)
    if t < 3.4:
        sprite(img, BAG, BAG_PAL, int(x) + 30, PY + 20, 2)
    else:
        sprite(img, BAG, BAG_PAL, int(lerp(88, 106, ease((t - 3.4) / 0.3))), PY + 20, 2)
    if t > 3.8:
        money_burst(img, t - 3.8, 140, PY, 18, seed=2)


def commerce_low(img, t):
    shop(img, 112, FEET - 34)
    x = lerp(4, 62, ease(t / 0.8))
    player(img, x, t, walking=t < 0.8)
    if t > 0.9:
        sprite(img, PISTOL, PISTOL_PAL, int(x) + 33, PY + 22, 2)
    if t > 1.4:
        money_burst(img, t - 1.4, 132, FEET - 30, 12, seed=5)


def voiture_low(img, t):
    sprite(img, DEALER, MECHANIC_PAL, 140, PY, 3, flip=True)   # Moses
    sprite(img, CAR, CAR_PAL, int(lerp(-80, 58, ease(t / 1.0))), CAR_Y, 3)
    if t > 3.4:
        money_burst(img, t - 3.4, 156, PY, 18, seed=9)


def banque_low(img, t):
    bank(img, 100, FEET - 46, ease((t - 0.2) / 0.8))
    player(img, 20, t)
    if t > 1.0:
        money_burst(img, t - 1.0, 130, FEET - 20, 26, seed=11)


def banque_hi(d, t):
    if t > 1.0:
        val = int(205000 * ease((t - 1.0) / 1.6))
        big_center(d, f"+{val:,} $".replace(",", " "), 330, 120)
        f2 = font(34)
        s = "selon le guide PowerPyx"
        d.text(((W - d.textlength(s, font=f2)) / 2, 480), s, font=f2, fill=WHITE,
               stroke_width=5, stroke_fill=OUTLINE)


def luxe_low(img, t):
    sprite(img, CAR, SPORT_PAL, 84, CAR_Y, 3)
    player(img, 14, t)
    if t > 1.2:
        red_cross(img, 120, GROUND_Y - 2, 22, ease((t - 1.2) / 0.2))


def bonus_low(img, t):
    player(img, 72, t)
    if t > 0.6:
        money_burst(img, (t - 0.6) % 2, 90, PY, 14, seed=int((t - 0.6) / 2) + 30)


ARROWS = ["↑", "→", "↓", "←", "↑", "←", "↓", "→"]


def bonus_hi(d, t):
    draw_rich(d, 230, "**BONUS**", 110)
    if t > 1.0:
        f = font(120)
        shown = min(8, int((t - 1.0) / 0.18) + 1)
        cell = 210
        for i in range(shown):
            row, col = divmod(i, 4)
            x = (W - 4 * cell) / 2 + col * cell
            y = 420 + row * 170
            d.rounded_rectangle([x + 15, y, x + cell - 15, y + 150], radius=30, fill=(26, 16, 38))
            a = ARROWS[i]
            d.text((x + (cell - d.textlength(a, font=f)) / 2, y + 8), a, font=f, fill=WHITE)


def outro_low(img, t):
    player(img, 72, t)
    money_burst(img, t % 1.5, 90, PY, 12, seed=int(t / 1.5) + 20)


def outro_hi(d, t):
    k = ease(t / 0.3)
    draw_rich(d, 330 + (1 - k) * 50, "Tout est sur", 80)
    draw_rich(d, 450 + (1 - k) * 50, "**Leonida Guide**", 115)


SCENES = [
    dict(dur=2.6, low=intro_low, hi=intro_hi,
         subs=[(0, "Tu veux devenir **riche** ?"), (1.3, "Voici **5 règles**.")]),
    dict(dur=5.6, low=receleur_low, n=1, shake=(3.8, 4.4),
         subs=[(0, "Ce que tu voles"), (1.2, "ne vaut **RIEN**..."),
               (2.4, "tant que tu ne passes pas"), (3.6, "chez le **receleur** !")]),
    dict(dur=5.2, low=commerce_low, n=2, shake=(1.4, 1.9),
         subs=[(0, "Commence petit :"), (1.2, "les **supérettes**"),
               (2.4, "et les **stations-service**."), (3.6, "**Sans préparation** !")]),
    dict(dur=5.4, low=voiture_low, n=3, shake=(3.4, 4.0),
         subs=[(0, "Après le **chapitre 2**..."), (1.4, "vole des voitures"),
               (2.5, "et revends-les"), (3.5, "à **Moses** !")]),
    dict(dur=5.6, low=banque_low, hi=banque_hi, n=4, shake=(1.0, 1.8),
         subs=[(0, "Fin du **chapitre 4** :"), (1.3, "les **coffres des banques**."),
               (2.9, "Jusqu'à **205 000 $**"), (4.1, "en **5 minutes** !")]),
    dict(dur=5.0, low=luxe_low, n=5,
         subs=[(0, "Et surtout..."), (1.0, "pas de **voiture de luxe**"),
               (2.4, "au début !"), (3.4, "Garde ton **argent**.")]),
    dict(dur=5.2, low=bonus_low, hi=bonus_hi,
         subs=[(0, "Le code des **250 000 $**"), (2.8, "marche après **l'histoire** !")]),
    dict(dur=3.2, low=outro_low, hi=outro_hi,
         subs=[(0, "Tous les codes et astuces"), (1.5, "**lien en bio** !")]),
]


def make_drawer():
    starts, acc = [], 0.0
    for s in SCENES:
        starts.append(acc)
        acc += s["dur"]

    def draw(t):
        idx = max(i for i, st in enumerate(starts) if st <= t)
        sc, lt = SCENES[idx], t - starts[idx]
        sub_start, sub = [(st, txt) for st, txt in sc["subs"] if st <= lt][-1]
        low = Image.new("RGB", (LW, LH))
        background(low, t)
        sc["low"](low, lt)
        sh = sc.get("shake")
        shake = 2.0 if sh and sh[0] <= lt <= sh[1] else 0.0
        low = fx(low, lt - sub_start, shake, t)
        low = flash(low, 1 - lt / 0.12) if idx > 0 else low
        hi = low.resize((LW * 6, LH * 6), Image.NEAREST)
        d = ImageDraw.Draw(hi)
        if sc.get("n"):
            header(d)
            badge(d, sc["n"], ease(lt / 0.2))
        if sc.get("hi"):
            sc["hi"](d, lt)
        words_caption(d, sub, lt - sub_start)
        return hi

    return draw, acc


def voiceover_text():
    out, acc = [], 0.0
    for s in SCENES:
        for st, txt in s["subs"]:
            out.append(f"[{acc + st:5.1f} s] {txt.replace('**', '')}")
        acc += s["dur"]
    return ("Voix off (à lire vite, ou « Texte en voix » CapCut en vitesse x1,2 à x1,3) :\n\n"
            + "\n".join(out))


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "videos/pixel-argent.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    draw, total = make_drawer()
    if "--preview" in sys.argv:
        for a in sys.argv[sys.argv.index("--preview") + 1:]:
            draw(float(a)).save(out.with_name(f"preview_{a}.png"))
    else:
        render(out, total, draw)
        out.with_suffix(".txt").write_text(voiceover_text() + "\n", encoding="utf-8")
        print(f"Vidéo créée : {out} ({total:.1f} s)")
