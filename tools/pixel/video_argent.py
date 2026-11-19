#!/usr/bin/env python3
"""Vidéo pixel art : « 5 règles pour devenir riche dans GTA 6 » (~65 s).

Usage :
  python3 tools/pixel/video_argent.py videos/pixel-argent.mp4
  python3 tools/pixel/video_argent.py videos/x.mp4 --preview 2 10 20   (images fixes)
Écrit aussi le texte de la voix off à côté de la vidéo (.txt).
Infos : uniquement celles vérifiées sur la page argent du site.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from PIL import Image, ImageDraw
from engine import (LW, LH, W, GROUND_Y, WHITE, YELLOW, font, ease, lerp, sprite,
                    background, coin, money_burst, red_cross, shop, bank,
                    draw_rich, caption, badge, render)
from sprites import (PLAYER, PLAYER_WALK, PLAYER_PAL, DEALER, DEALER_PAL, MECHANIC_PAL,
                     BAG, BAG_PAL, PISTOL, PISTOL_PAL, CAR, CAR_PAL, SPORT_PAL)

FEET = GROUND_Y - 8
PY = FEET - 45          # haut d'un personnage (15 lignes x 3)
CAR_Y = GROUND_Y + 12 - 27


def player(img, x, t, walking=False):
    rows = PLAYER_WALK if walking and int(t * 6) % 2 else PLAYER
    bob = 0 if walking else int(t * 2) % 2
    sprite(img, rows, PLAYER_PAL, int(x), PY + bob, 3)


def header(d, text="DEVENIR RICHE DANS GTA 6"):
    f = font(44)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, 70), text, font=f, fill=WHITE, stroke_width=6, stroke_fill=(10, 5, 20))


# ---------------- scènes ----------------

def intro_low(img, t):
    player(img, 72, t)
    for i in range(12):
        coin(img, (i * 37) % 170, int((t * 60 + i * 23) % 140) + 20)


def intro_hi(d, t):
    k = ease(t / 0.6)
    for i, (ln, sz) in enumerate([("5 RÈGLES", 120), ("pour devenir **RICHE**", 84), ("dans GTA 6", 84)]):
        draw_rich(d, 300 + i * 140 + (1 - k) * 60, ln, sz)


def receleur_low(img, t):
    x = lerp(4, 58, ease(t / 3))
    player(img, x, t, walking=t < 3)
    sprite(img, DEALER, DEALER_PAL, 128, PY, 3, flip=True)
    if t < 3.6:
        sprite(img, BAG, BAG_PAL, int(x) + 30, PY + 20, 2)
    else:
        bx = lerp(88, 106, ease((t - 3.6) / 0.6))
        sprite(img, BAG, BAG_PAL, int(bx), PY + 20, 2)
        if t > 4.2:
            money_burst(img, t - 4.2, 140, PY, 16, seed=2)


def commerce_low(img, t):
    shop(img, 112, FEET - 34)
    x = lerp(4, 62, ease(t / 2.5))
    player(img, x, t, walking=t < 2.5)
    if t > 2.5:
        sprite(img, PISTOL, PISTOL_PAL, int(x) + 33, PY + 22, 2)
    if t > 3.5:
        money_burst(img, t - 3.5, 132, FEET - 30, 10, seed=5)


def voiture_low(img, t):
    sprite(img, DEALER, MECHANIC_PAL, 140, PY, 3, flip=True)   # Moses
    sprite(img, CAR, CAR_PAL, int(lerp(-80, 58, ease(t / 3))), CAR_Y, 3)
    if t > 4:
        money_burst(img, t - 4, 156, PY, 16, seed=9)


def banque_low(img, t):
    bank(img, 100, FEET - 46, ease((t - 1) / 2))
    player(img, 20, t)
    if t > 3.2:
        money_burst(img, t - 3.2, 130, FEET - 20, 22, seed=11)


def banque_hi(d, t):
    if t <= 3:
        return
    val = int(205000 * ease((t - 3) / 2.5))
    txt = f"+{val:,} $".replace(",", " ")
    f = font(110)
    d.text(((W - d.textlength(txt, font=f)) / 2, 330), txt, font=f, fill=YELLOW,
           stroke_width=12, stroke_fill=(10, 5, 20))
    f2 = font(34)
    s = "selon le guide PowerPyx"
    d.text(((W - d.textlength(s, font=f2)) / 2, 470), s, font=f2, fill=WHITE,
           stroke_width=5, stroke_fill=(10, 5, 20))


def luxe_low(img, t):
    sprite(img, CAR, SPORT_PAL, 84, CAR_Y, 3)
    player(img, 14, t)
    if t > 2.5:
        red_cross(img, 120, GROUND_Y - 2, 22, ease((t - 2.5) / 0.4))


def outro_low(img, t):
    player(img, 72, t)
    money_burst(img, t % 2.5, 90, PY, 12, seed=int(t / 2.5) + 20)


def outro_hi(d, t):
    k = ease(t / 0.5)
    y = 300
    for ln, sz in [("Toutes les astuces GTA 6", 70), ("sont sur", 70),
                   ("**Leonida Guide**", 110), ("(lien en bio)", 56)]:
        draw_rich(d, y + (1 - k) * 50, ln, sz)
        y += sz + 40


SCENES = [
    dict(dur=4.5, low=intro_low, hi=intro_hi,
         subs=[(0, "Tu galères à te faire de l'**argent** dans GTA 6 ? Voici **5 règles**.")]),
    dict(dur=11, low=receleur_low, n=1,
         subs=[(0, "Règle n°1 : ce que tu voles ne vaut **RIEN** tout de suite."),
               (4.5, "Il faut le revendre à un **receleur** pour toucher l'argent.")]),
    dict(dur=11, low=commerce_low, n=2,
         subs=[(0, "Règle n°2 : commence par les **petits commerces**."),
               (4.5, "Supérettes, stations-service : quelques milliers de $, **sans préparation**.")]),
    dict(dur=11, low=voiture_low, n=3,
         subs=[(0, "Règle n°3 : après le **chapitre 2**, vole des voitures..."),
               (4.5, "... et revends-les à **Moses**.")]),
    dict(dur=11, low=banque_low, hi=banque_hi, n=4,
         subs=[(0, "Règle n°4 : à la fin du **chapitre 4**, vise les coffres des banques."),
               (5, "Jusqu'à **205 000 $** en 5 minutes !")]),
    dict(dur=11, low=luxe_low, n=5,
         subs=[(0, "Règle n°5 : n'achète **PAS** de voiture de luxe au début."),
               (4.5, "Garde ton argent pour ce qui **rapporte**.")]),
    dict(dur=5, low=outro_low, hi=outro_hi,
         subs=[(0, "Abonne-toi pour la suite !")]),
]


def make_drawer():
    starts, acc = [], 0.0
    for s in SCENES:
        starts.append(acc)
        acc += s["dur"]

    def draw(t):
        idx = max(i for i, st in enumerate(starts) if st <= t)
        sc, lt = SCENES[idx], t - starts[idx]
        low = Image.new("RGB", (LW, LH))
        background(low, t)
        sc["low"](low, lt)
        hi = low.resize((LW * 6, LH * 6), Image.NEAREST)
        d = ImageDraw.Draw(hi)
        if sc.get("n"):
            header(d)
            badge(d, sc["n"], ease(lt / 0.4))
        if sc.get("hi"):
            sc["hi"](d, lt)
        caption(d, [txt for st, txt in sc["subs"] if st <= lt][-1])
        return hi

    return draw, acc


def voiceover_text():
    out, acc = [], 0.0
    for s in SCENES:
        for st, txt in s["subs"]:
            m, sec = divmod(int(acc + st), 60)
            out.append(f"[{m}:{sec:02d}] {txt.replace('**', '')}")
        acc += s["dur"]
    return "\n".join(out)


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
