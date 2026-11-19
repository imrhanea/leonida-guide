"""Sprites pixel art originaux (aucune image tierce).

Chaque sprite est une liste de chaînes : un caractère = un pixel, '.' = transparent.
Les couleurs viennent de la palette passée au dessin.
"""

PLAYER = [
    "....KKKK....",
    "...KKKKKKK..",
    "...SSSSSS...",
    "...SESSES...",
    "...SSSSSS...",
    "....SSSS....",
    "..WWWWWWWW..",
    ".SWWWWWWWWS.",
    ".SWWWWWWWWS.",
    ".SWWWWWWWWS.",
    "..WWWWWWWW..",
    "..BBBBBBBB..",
    "..BBB..BBB..",
    "..BBB..BBB..",
    "..DDD..DDD..",
]
PLAYER_WALK = PLAYER[:12] + [
    ".BBB....BBB.",
    ".BBB....BBB.",
    ".DDD....DDD.",
]
PLAYER_PAL = {"K": (35, 45, 110), "S": (232, 182, 140), "E": (30, 20, 30),
              "W": (40, 185, 175), "B": (50, 70, 140), "D": (30, 30, 34)}

DEALER = [
    "....HHHH....",
    "..HHHHHHHH..",
    "...SSSSSS...",
    "...GGSSGG...",
    "...SSSSSS...",
    "....SSSS....",
    "..PPPYPPPP..",
    ".SPPPYYPPPS.",
    ".SPPPPPPPPS.",
    ".SPPPPPPPPS.",
    "..PPPPPPPP..",
    "..BBBBBBBB..",
    "..BBB..BBB..",
    "..BBB..BBB..",
    "..DDD..DDD..",
]
DEALER_PAL = {"H": (90, 60, 40), "S": (160, 110, 75), "G": (20, 20, 25),
              "P": (120, 60, 170), "Y": (250, 210, 60), "B": (40, 40, 50), "D": (20, 20, 22)}
MECHANIC_PAL = {"H": (200, 60, 50), "S": (205, 150, 110), "G": (20, 20, 25),
                "P": (230, 140, 40), "Y": (230, 140, 40), "B": (60, 60, 70), "D": (20, 20, 22)}

BAG = [
    "...NNNN...",
    "....NN....",
    "..GGGGGG..",
    ".GGGGGGGG.",
    "GGGG$$GGGG",
    "GGG$GGGGGG",
    "GGGG$$GGGG",
    "GGGGGG$GGG",
    ".GGG$$GGG.",
    "..GGGGGG..",
]
BAG_PAL = {"N": (110, 80, 40), "G": (196, 158, 96), "$": (40, 140, 60)}

PISTOL = [
    "MMMMMMMMM",
    "MMMMMMMMM",
    "MMMWM....",
    "MMM......",
    "MMM......",
]
PISTOL_PAL = {"M": (45, 45, 55), "W": (120, 120, 130)}

CAR = [
    "......CCCCCCCCC.........",
    ".....CWWWWCWWWWC........",
    "....CWWWWWCWWWWWC.......",
    "CCCCCCCCCCCCCCCCCCCCCCC.",
    "CCCCCCCCCCCCCCCCCCCCCCCL",
    "CCCCCCCCCCCCCCCCCCCCCCCC",
    "CC.TTT.CCCCCCCCC.TTT.CCC",
    "..TTTTT.........TTTTT...",
    "...TTT...........TTT....",
]
CAR_PAL = {"C": (60, 120, 200), "W": (170, 220, 245), "L": (255, 240, 150), "T": (25, 25, 30)}
SPORT_PAL = {"C": (225, 40, 60), "W": (170, 220, 245), "L": (255, 240, 150), "T": (25, 25, 30)}

PALM = [
    "..LL.....LL...",
    ".LLLL...LLLL..",
    "LLL.LL.LL.LLL.",
    "L.....LL.....L",
    "......TT......",
    "......TT......",
    ".....TT.......",
    ".....TT.......",
    ".....TT.......",
    "......TT......",
    "......TT......",
    "......TT......",
    ".......TT.....",
    ".......TT.....",
    ".......TT.....",
    "......TT......",
    "......TT......",
    "......TT......",
]
PALM_PAL = {"L": (40, 150, 90), "T": (120, 80, 50)}
