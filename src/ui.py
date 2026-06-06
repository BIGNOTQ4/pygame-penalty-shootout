# -*- coding: utf-8 -*-

import pygame

from .settings import CARD, CARD_HOVER, GRAY, MINT, PANEL, WHITE, YELLOW


def load_font(size, bold=False):
    """Magyar karaktereket támogató fontot tölt be.

    Windows alatt a Segoe UI az első választás, de más rendszeren az Arial
    vagy a DejaVu Sans is jó tartalék. Mindhárom kezeli az ő és ű betűket.
    """
    font_path = pygame.font.match_font("segoeui,segoe ui,arial,dejavusans", bold=bold)
    if font_path:
        return pygame.font.Font(font_path, size)
    return pygame.font.SysFont("arial", size, bold=bold)


def create_fonts():
    """Egy helyen készíti el a játékban használt betűméreteket."""
    return {
        "tiny": load_font(15),
        "small": load_font(18),
        "normal": load_font(23),
        "medium": load_font(30, bold=True),
        "big": load_font(48, bold=True),
        "huge": load_font(64, bold=True),
    }


def draw_text(screen, text, font, color, center=None, topleft=None, shadow=True):
    """Szöveget rajzol árnyékkal, hogy a pályán is jól olvasható legyen."""
    if shadow:
        shadow_surface = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect()
        if center:
            shadow_rect.center = (center[0] + 2, center[1] + 3)
        elif topleft:
            shadow_rect.topleft = (topleft[0] + 2, topleft[1] + 3)
        screen.blit(shadow_surface, shadow_rect)

    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = center
    elif topleft:
        rect.topleft = topleft
    screen.blit(surface, rect)
    return rect


def draw_panel(screen, rect, color=PANEL, alpha=215, border_color=(71, 85, 105)):
    """Áttetsző, lekerekített panelt rajzol árnyékkal."""
    shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 80), shadow.get_rect(), border_radius=18)
    screen.blit(shadow, (rect.x + 6, rect.y + 8))

    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*color, alpha), panel.get_rect(), border_radius=18)
    pygame.draw.rect(panel, (*border_color, 210), panel.get_rect(), 2, border_radius=18)
    screen.blit(panel, rect.topleft)


def draw_button(screen, rect, text, font, active=False):
    """Szép gomb hover effekttel. Visszaadja, hogy az egér felette van-e."""
    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)

    if active:
        color = (20, 184, 166)
        border = YELLOW
    elif hovered:
        color = CARD_HOVER
        border = MINT
    else:
        color = CARD
        border = GRAY

    shadow_rect = rect.move(0, 6)
    pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=12)
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, border, rect, 2, border_radius=12)

    if active:
        # Egy vékony belső keret egyértelműbbé teszi, melyik opció aktív.
        inner_rect = rect.inflate(-8, -8)
        pygame.draw.rect(screen, (204, 251, 241), inner_rect, 1, border_radius=9)

    draw_text(screen, text, font, WHITE, center=rect.center)
    return hovered


def draw_stat_card(screen, rect, label, value, accent, fonts):
    """Kis statisztika kártya címkével és nagy számmal."""
    draw_panel(screen, rect, color=CARD, alpha=230, border_color=(71, 85, 105))
    pygame.draw.circle(screen, accent, (rect.x + 22, rect.y + 25), 6)
    draw_text(screen, label, fonts["small"], GRAY, topleft=(rect.x + 38, rect.y + 16))
    draw_text(screen, str(value), fonts["medium"], WHITE, center=(rect.centerx, rect.y + 62))
