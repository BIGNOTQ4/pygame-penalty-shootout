# -*- coding: utf-8 -*-

import pygame

from . import ui
from .settings import (
    CARD,
    GRAY,
    HEIGHT,
    MAX_SHOTS,
    MINT,
    ORANGE,
    PANEL,
    RED,
    SHOT_TYPES,
    SKY_BLUE,
    TEAMS,
    WHITE,
    WIDTH,
    YELLOW,
)


def draw_menu(screen, fonts, draw_field, game):
    """Kirajzolja a főmenüt, és feltölti a kattintható gombok listáját."""
    draw_field()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 86))
    screen.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(50, 54, 800, 500)
    ui.draw_panel(screen, panel_rect, color=PANEL, alpha=228, border_color=(94, 234, 212))

    ui.draw_text(screen, "Tizenegyes játék", fonts["big"], WHITE, center=(WIDTH // 2, 105))
    ui.draw_text(screen, "Állítsd össze a csapatot és a lövési stílust", fonts["small"], GRAY, center=(WIDTH // 2, 142))
    ui.draw_text(
        screen,
        f"Rekord: {game.high_score['best_goals']} gól   Legjobb pontosság: {game.high_score['best_accuracy']}%",
        fonts["small"],
        MINT,
        center=(WIDTH // 2, 174),
    )

    game.menu_buttons = []
    ui.draw_text(screen, "Nehézség", fonts["normal"], WHITE, topleft=(92, 214))
    difficulty_data = [("konnyu", "1  Könnyű"), ("normal", "2  Normál"), ("nehez", "3  Nehéz")]
    for index, (difficulty_key, text) in enumerate(difficulty_data):
        rect = pygame.Rect(92 + index * 170, 250, 150, 44)
        game.menu_buttons.append((rect, "difficulty", difficulty_key))
        ui.draw_button(screen, rect, text, fonts["small"], active=difficulty_key == game.difficulty_key)

    ui.draw_text(screen, "Csapat", fonts["normal"], WHITE, topleft=(92, 315))
    for index, (team_key, team_data) in enumerate(TEAMS.items()):
        rect = pygame.Rect(92 + index * 150, 352, 132, 48)
        game.menu_buttons.append((rect, "team", team_key))
        ui.draw_button(screen, rect, team_data["name"], fonts["small"], active=team_key == game.team_key)
        pygame.draw.circle(screen, team_data["shirt"], (rect.x + 18, rect.centery), 8)
        pygame.draw.circle(screen, team_data["shorts"], (rect.x + 34, rect.centery), 8)

    ui.draw_text(screen, "Lövéstípus", fonts["normal"], WHITE, topleft=(92, 420))
    for index, (shot_key, shot_data) in enumerate(SHOT_TYPES.items()):
        rect = pygame.Rect(92 + index * 190, 456, 170, 44)
        game.menu_buttons.append((rect, "shot_type", shot_key))
        ui.draw_button(screen, rect, shot_data["name"], fonts["small"], active=shot_key == game.shot_type_key)

    start_rect = pygame.Rect(640, 242, 170, 56)
    exit_rect = pygame.Rect(640, 500, 170, 42)
    game.menu_buttons.append((start_rect, "start", None))
    game.menu_buttons.append((exit_rect, "exit", None))
    ui.draw_button(screen, start_rect, "Meccs indítása", fonts["small"], active=True)
    ui.draw_button(screen, exit_rect, "Kilépés", fonts["small"])

    hint = "ENTER: indítás   1-3: nehézség   SPACE / bal klikk: lövés játék közben"
    ui.draw_text(screen, hint, fonts["small"], GRAY, center=(WIDTH // 2, 575))


def draw_game_over(screen, fonts, draw_field, game):
    """Kirajzolja a játék vége képernyőt és a végső összesítést."""
    if not game.high_score_checked:
        game.update_high_score()
        game.high_score_checked = True

    draw_field()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 96))
    screen.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(130, 70, 640, 470)
    ui.draw_panel(screen, panel_rect, color=PANEL, alpha=232, border_color=(250, 204, 21))
    ui.draw_text(screen, "Játék vége", fonts["huge"], YELLOW, center=(WIDTH // 2, 130))

    accuracy = game.get_accuracy()
    setup = f"{game.team['name']}   |   {game.shot_type['name']}   |   {game.difficulty['label']}"
    ui.draw_text(screen, setup, fonts["small"], GRAY, center=(WIDTH // 2, 178))
    ui.draw_text(screen, game.get_final_rating(), fonts["normal"], WHITE, center=(WIDTH // 2, 205))

    cards = [
        ("Összes lövés", game.total_shots, WHITE),
        ("Gól", game.goals, YELLOW),
        ("Védés", game.saves, SKY_BLUE),
        ("Mellé", game.misses, RED),
        ("Pontosság", f"{accuracy}%", MINT),
        ("Rekord", f"{game.high_score['best_goals']} gól", ORANGE),
    ]

    for index, (label, value, accent) in enumerate(cards):
        col = index % 3
        row = index // 3
        rect = pygame.Rect(190 + col * 205, 245 + row * 92, 170, 76)
        ui.draw_stat_card(screen, rect, label, value, accent, fonts)

    best_line = f"Legjobb pontosság: {game.high_score['best_accuracy']}%"
    ui.draw_text(screen, best_line, fonts["small"], MINT, center=(WIDTH // 2, 425))

    game.game_over_buttons = []
    button_data = [
        (pygame.Rect(212, 456, 180, 48), "restart", "Új játék"),
        (pygame.Rect(410, 456, 150, 48), "menu", "Menü"),
        (pygame.Rect(578, 456, 150, 48), "exit", "Kilépés"),
    ]
    for rect, action, text in button_data:
        game.game_over_buttons.append((rect, action))
        ui.draw_button(screen, rect, text, fonts["normal"], active=action == "restart")
