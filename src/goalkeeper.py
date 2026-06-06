# -*- coding: utf-8 -*-

import random

import pygame

from .settings import (
    BLUE,
    GOAL_WIDTH,
    GOAL_X,
    KEEPER_HEIGHT,
    KEEPER_WIDTH,
    SKIN,
    WHITE,
)


def clamp(value, minimum, maximum):
    """Egy számot a megadott alsó és felső határ közé szorít."""
    return max(minimum, min(value, maximum))


def smoothstep(value):
    """Kicsit természetesebb mozgást ad az animációknak."""
    return value * value * (3 - 2 * value)


def choose_keeper_target(ball_target, difficulty, shot_type):
    """Kiválasztja, merre vetődik a kapus."""
    read_chance = difficulty["keeper_reads_shot"] + shot_type["keeper_read_bonus"]
    read_chance = clamp(read_chance, 0.05, 0.92)
    reach = difficulty["keeper_reach"] + shot_type["keeper_reach_bonus"]
    reach = max(30, reach)

    # Jobb nehézségen és bizonyos lövéseknél a kapus gyakrabban olvassa a lövést.
    if random.random() < read_chance:
        target_x = ball_target.x + random.uniform(-45, 45)
    else:
        target_x = random.choice([
            GOAL_X + 95,
            450,
            GOAL_X + GOAL_WIDTH - 95,
        ])

    target_x = clamp(target_x, GOAL_X + 70, GOAL_X + GOAL_WIDTH - 70)
    target_y = 205 + random.uniform(-24, 14)
    return pygame.Vector2(target_x, target_y), reach


def draw_goalkeeper(screen, keeper_pos, keeper_start, keeper_target, keeper_progress, keeper_stretch):
    """Kirajzolja a kapust látványosabb vetődéssel."""
    direction = 0
    if keeper_target.x < keeper_start.x - 5:
        direction = -1
    elif keeper_target.x > keeper_start.x + 5:
        direction = 1

    dive = smoothstep(keeper_progress)
    body_w = KEEPER_WIDTH + int(22 * dive)
    body_h = KEEPER_HEIGHT - int(10 * dive)
    body_rect = pygame.Rect(0, 0, body_w, body_h)
    body_rect.center = (int(keeper_pos.x), int(keeper_pos.y))

    pygame.draw.ellipse(screen, (20, 70, 30), (body_rect.x - 14, body_rect.y + 35, body_rect.w + 28, 18))
    pygame.draw.ellipse(screen, BLUE, body_rect)

    head_x = int(keeper_pos.x + direction * 24 * dive)
    head_y = int(keeper_pos.y - 35 + 10 * dive)
    pygame.draw.circle(screen, SKIN, (head_x, head_y), 18)

    arm_y = int(keeper_pos.y)
    reach = 60 + int(keeper_stretch * keeper_progress)

    if direction < 0:
        pygame.draw.line(screen, BLUE, (int(keeper_pos.x), arm_y), (int(keeper_pos.x - reach), arm_y - 34), 11)
        pygame.draw.line(screen, BLUE, (int(keeper_pos.x), arm_y), (int(keeper_pos.x + 46), arm_y + 18), 10)
        pygame.draw.circle(screen, WHITE, (int(keeper_pos.x - reach), arm_y - 34), 10)
    elif direction > 0:
        pygame.draw.line(screen, BLUE, (int(keeper_pos.x), arm_y), (int(keeper_pos.x + reach), arm_y - 34), 11)
        pygame.draw.line(screen, BLUE, (int(keeper_pos.x), arm_y), (int(keeper_pos.x - 46), arm_y + 18), 10)
        pygame.draw.circle(screen, WHITE, (int(keeper_pos.x + reach), arm_y - 34), 10)
    else:
        pygame.draw.line(screen, BLUE, (int(keeper_pos.x - reach // 2), arm_y), (int(keeper_pos.x + reach // 2), arm_y), 11)
        pygame.draw.circle(screen, WHITE, (int(keeper_pos.x - reach // 2), arm_y), 9)
        pygame.draw.circle(screen, WHITE, (int(keeper_pos.x + reach // 2), arm_y), 9)

    pygame.draw.line(screen, BLUE, (int(keeper_pos.x - 20), int(keeper_pos.y + 15)), (int(keeper_pos.x - 45), int(keeper_pos.y + 44)), 9)
    pygame.draw.line(screen, BLUE, (int(keeper_pos.x + 20), int(keeper_pos.y + 15)), (int(keeper_pos.x + 45), int(keeper_pos.y + 44)), 9)
