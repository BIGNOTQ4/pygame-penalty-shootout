# -*- coding: utf-8 -*-

import math

import pygame

from .settings import BLACK, PLAYER_POS, SKIN, WHITE


def draw_player(screen, team, ball_progress, shooting):
    """Egyszerű rúgó játékosfigura a labda mögött."""
    x = int(PLAYER_POS.x)
    y = int(PLAYER_POS.y)
    kick = ball_progress if shooting else 0
    leg_swing = int(20 * math.sin(kick * math.pi))
    shirt_color = team["shirt"]
    shorts_color = team["shorts"]

    pygame.draw.ellipse(screen, (20, 70, 30), (x - 32, y + 28, 70, 14))
    pygame.draw.circle(screen, SKIN, (x, y - 72), 17)
    pygame.draw.rect(screen, shirt_color, (x - 20, y - 55, 40, 50), border_radius=8)
    pygame.draw.line(screen, WHITE, (x - 12, y - 50), (x - 12, y - 10), 3)
    pygame.draw.line(screen, WHITE, (x + 12, y - 50), (x + 12, y - 10), 3)
    pygame.draw.line(screen, SKIN, (x - 18, y - 42), (x - 42, y - 22), 7)
    pygame.draw.line(screen, SKIN, (x + 18, y - 42), (x + 38, y - 18), 7)
    pygame.draw.line(screen, shorts_color, (x - 10, y - 5), (x - 26, y + 30), 8)
    pygame.draw.line(screen, shorts_color, (x + 10, y - 5), (x + 23 + leg_swing, y + 30), 8)
    pygame.draw.circle(screen, BLACK, (x - 27, y + 34), 5)
    pygame.draw.circle(screen, BLACK, (x + 25 + leg_swing, y + 34), 5)
