# -*- coding: utf-8 -*-

from pathlib import Path

import pygame


# Ablak beállításai
WIDTH = 900
HEIGHT = 600
FPS = 60
MAX_SHOTS = 10
SAVE_FILE = Path("save_data.json")

# Modern, tiszta színpaletta
GREEN = (37, 142, 82)
LIGHT_GREEN = (58, 174, 101)
DARK_GREEN = (22, 98, 61)
WHITE = (248, 250, 252)
BLACK = (15, 23, 42)
BLUE = (37, 99, 235)
SKY_BLUE = (125, 211, 252)
YELLOW = (250, 204, 21)
ORANGE = (249, 115, 22)
RED = (239, 68, 68)
GRAY = (148, 163, 184)
DARK_GRAY = (51, 65, 85)
PANEL = (15, 23, 42)
CARD = (30, 41, 59)
CARD_HOVER = (51, 65, 85)
MINT = (45, 212, 191)
NET_COLOR = (226, 232, 240)
SKIN = (245, 190, 135)

# Pálya és kapu méretei
GOAL_X = 250
GOAL_Y = 80
GOAL_WIDTH = 500
GOAL_HEIGHT = 180
GOAL_LINE_Y = GOAL_Y + GOAL_HEIGHT

# Labda és játékos kezdőadatai
BALL_START = pygame.Vector2(WIDTH // 2, 520)
BALL_RADIUS = 14
PLAYER_POS = pygame.Vector2(WIDTH // 2 - 55, 515)

# Kapus kezdőadatai
KEEPER_START = pygame.Vector2(WIDTH // 2, 205)
KEEPER_WIDTH = 86
KEEPER_HEIGHT = 46

# A nehézség a kapus ügyességét és a lövés pontatlanságát is befolyásolja.
DIFFICULTIES = {
    "konnyu": {
        "label": "Könnyű",
        "keeper_speed": 0.045,
        "keeper_reach": 70,
        "keeper_reads_shot": 0.25,
        "bad_power_error": 75,
    },
    "normal": {
        "label": "Normál",
        "keeper_speed": 0.060,
        "keeper_reach": 95,
        "keeper_reads_shot": 0.45,
        "bad_power_error": 100,
    },
    "nehez": {
        "label": "Nehéz",
        "keeper_speed": 0.078,
        "keeper_reach": 125,
        "keeper_reads_shot": 0.70,
        "bad_power_error": 125,
    },
}

# Választható csapatok. A két szín a mez és a nadrág színe.
TEAMS = {
    "budapest": {"name": "Budapest FC", "shirt": RED, "shorts": WHITE},
    "duna": {"name": "Duna SC", "shirt": BLUE, "shorts": WHITE},
    "alfold": {"name": "Alföld United", "shirt": (22, 163, 74), "shorts": BLACK},
    "balaton": {"name": "Balaton SE", "shirt": SKY_BLUE, "shorts": DARK_GRAY},
    "matra": {"name": "Mátra AC", "shirt": (124, 58, 237), "shorts": WHITE},
}

# A lövés típusa a pontosságot, sebességet és a kapus esélyét is módosítja.
SHOT_TYPES = {
    "power": {
        "name": "Erős lövés",
        "speed_multiplier": 1.35,
        "accuracy_multiplier": 1.30,
        "keeper_read_bonus": -0.08,
        "keeper_reach_bonus": -22,
        "ideal_power": 0.78,
    },
    "placed": {
        "name": "Helyezett lövés",
        "speed_multiplier": 0.92,
        "accuracy_multiplier": 0.55,
        "keeper_read_bonus": 0.10,
        "keeper_reach_bonus": 12,
        "ideal_power": 0.66,
    },
    "panenka": {
        "name": "Panenka",
        "speed_multiplier": 0.66,
        "accuracy_multiplier": 0.80,
        "keeper_read_bonus": 0.24,
        "keeper_reach_bonus": 34,
        "ideal_power": 0.54,
    },
}
