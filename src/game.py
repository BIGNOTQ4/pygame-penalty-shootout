# -*- coding: utf-8 -*-

import math
import random

import pygame

from . import goalkeeper, menu, player, save_manager, sounds, ui
from .settings import (
    BALL_RADIUS,
    BALL_START,
    BLACK,
    CARD,
    DARK_GRAY,
    DARK_GREEN,
    DIFFICULTIES,
    FPS,
    GOAL_HEIGHT,
    GOAL_LINE_Y,
    GOAL_WIDTH,
    GOAL_X,
    GOAL_Y,
    GRAY,
    GREEN,
    HEIGHT,
    KEEPER_HEIGHT,
    KEEPER_START,
    KEEPER_WIDTH,
    LIGHT_GREEN,
    MAX_SHOTS,
    MINT,
    NET_COLOR,
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


class PenaltyGame:
    """A teljes játékot összefogó osztály."""

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("Tizenegyes játék")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = ui.create_fonts()

        self.state = "menu"
        self.difficulty_key = "normal"
        self.team_key = "budapest"
        self.shot_type_key = "placed"
        self.menu_buttons = []
        self.game_over_buttons = []
        self.high_score = save_manager.load_save_data()
        self.high_score_checked = False

        self.flash_alpha = 0
        self.flash_color = WHITE
        self.transition_alpha = 255
        self.shake_timer = 0
        self.shake_strength = 0
        self.particles = []

        self.sounds = sounds.create_sounds()
        self.reset_match()

    @property
    def difficulty(self):
        """A kiválasztott nehézség adatait adja vissza."""
        return DIFFICULTIES[self.difficulty_key]

    @property
    def team(self):
        """A kiválasztott csapat adatait adja vissza."""
        return TEAMS[self.team_key]

    @property
    def shot_type(self):
        """A kiválasztott lövéstípus adatait adja vissza."""
        return SHOT_TYPES[self.shot_type_key]

    def reset_match(self):
        """Új 10 lövéses játékot indít."""
        self.goals = 0
        self.saves = 0
        self.misses = 0
        self.total_shots = 0
        self.high_score_checked = False
        self.message = "Célozz egérrel, időzítsd a lövéserőt, majd lőj!"
        self.message_timer = 0
        self.power = 0.5
        self.power_direction = 1
        self.particles = []
        self.reset_round()

    def reset_round(self):
        """Egyetlen lövéshez állítja vissza a labdát és a kapust."""
        self.ball_pos = BALL_START.copy()
        self.ball_start = BALL_START.copy()
        self.ball_target = BALL_START.copy()
        self.ball_progress = 0.0
        self.ball_speed = 0.035
        self.ball_spin = 0.0

        self.keeper_pos = KEEPER_START.copy()
        self.keeper_start = KEEPER_START.copy()
        self.keeper_target = KEEPER_START.copy()
        self.keeper_progress = 0.0
        self.keeper_speed = self.difficulty["keeper_speed"]
        self.keeper_stretch = 0

        self.aim_pos = pygame.Vector2(WIDTH // 2, GOAL_LINE_Y - 70)
        self.shooting = False
        self.round_finished = False
        self.result_checked = False
        self.result = ""

    def change_state(self, new_state):
        """Állapotváltás kis sötét átúszás effekttel."""
        self.state = new_state
        self.transition_alpha = 255

    def start_game(self, difficulty_key):
        """A menüből elindítja a játékot a választott nehézséggel."""
        self.difficulty_key = difficulty_key
        self.reset_match()
        self.change_state("playing")

    def restart_game(self):
        """R billentyűre újrakezdi a meccset."""
        if self.state == "menu":
            return
        self.reset_match()
        self.change_state("playing")

    def start_shot(self):
        """Elindítja a lövés animációját."""
        if self.state != "playing" or self.shooting or self.round_finished:
            return

        sounds.play_sound(self.sounds, "shoot")
        self.shooting = True
        self.round_finished = False
        self.result_checked = False
        self.result = ""
        self.ball_start = self.ball_pos.copy()
        self.ball_progress = 0.0
        self.shake_timer = 6
        self.shake_strength = 3

        ideal_power = self.shot_type["ideal_power"]
        power_error = abs(self.power - ideal_power)
        max_error = self.difficulty["bad_power_error"] * power_error
        max_error *= self.shot_type["accuracy_multiplier"]

        target_x = self.aim_pos.x + random.uniform(-max_error, max_error)
        target_y = self.aim_pos.y + random.uniform(-max_error * 0.55, max_error * 0.55)
        if self.shot_type_key == "panenka":
            target_y -= 18

        self.ball_target = pygame.Vector2(target_x, target_y)
        self.ball_speed = (0.026 + self.power * 0.030) * self.shot_type["speed_multiplier"]
        self.choose_keeper_target()

    def choose_keeper_target(self):
        """Bekéri a kapusmodultól, merre vetődjön a kapus."""
        target, reach = goalkeeper.choose_keeper_target(self.ball_target, self.difficulty, self.shot_type)
        self.keeper_start = self.keeper_pos.copy()
        self.keeper_target = target
        self.keeper_progress = 0.0
        self.keeper_speed = self.difficulty["keeper_speed"]
        self.keeper_stretch = reach

    def update_playing(self):
        """Frissíti a célzást, erősávot és lövésanimációt."""
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if not self.shooting and not self.round_finished:
            self.aim_pos.x = goalkeeper.clamp(mouse_x, GOAL_X - 100, GOAL_X + GOAL_WIDTH + 100)
            self.aim_pos.y = goalkeeper.clamp(mouse_y, GOAL_Y + 18, GOAL_LINE_Y + 95)

            self.power += self.power_direction * 0.014
            if self.power >= 1.0:
                self.power = 1.0
                self.power_direction = -1
            elif self.power <= 0.05:
                self.power = 0.05
                self.power_direction = 1

        if self.shooting:
            self.ball_progress = min(1.0, self.ball_progress + self.ball_speed)
            self.keeper_progress = min(1.0, self.keeper_progress + self.keeper_speed)

            ball_t = goalkeeper.smoothstep(self.ball_progress)
            keeper_t = goalkeeper.smoothstep(self.keeper_progress)

            self.ball_pos = self.ball_start.lerp(self.ball_target, ball_t)
            self.keeper_pos = self.keeper_start.lerp(self.keeper_target, keeper_t)
            self.ball_spin += self.ball_speed * 10

            if self.ball_progress >= 1.0 and not self.result_checked:
                self.check_result()

        if self.round_finished:
            self.message_timer -= 1
            if self.message_timer <= 0:
                if self.total_shots >= MAX_SHOTS:
                    if not self.high_score_checked:
                        self.update_high_score()
                        self.high_score_checked = True
                    self.change_state("game_over")
                else:
                    self.reset_round()

    def update_effects(self):
        """Frissíti a villanást, átúszást, rázkódást és apró konfettiket."""
        self.flash_alpha = max(0, self.flash_alpha - 12)
        self.transition_alpha = max(0, self.transition_alpha - 14)
        self.shake_timer = max(0, self.shake_timer - 1)

        for particle in self.particles:
            particle["pos"] += particle["vel"]
            particle["vel"].y += 0.18
            particle["life"] -= 1

        self.particles = [particle for particle in self.particles if particle["life"] > 0]

    def create_goal_particles(self):
        """Gólnál kis konfetti-szerű részecskéket dob a kapu elé."""
        for _ in range(36):
            self.particles.append({
                "pos": pygame.Vector2(random.randint(GOAL_X + 40, GOAL_X + GOAL_WIDTH - 40), GOAL_Y + 20),
                "vel": pygame.Vector2(random.uniform(-3.0, 3.0), random.uniform(-5.0, -1.5)),
                "color": random.choice([YELLOW, ORANGE, WHITE, RED]),
                "life": random.randint(30, 55),
            })

    def check_result(self):
        """Eldönti, hogy gól, védés vagy mellé lövés történt."""
        self.result_checked = True
        self.round_finished = True
        self.shooting = False
        self.total_shots += 1

        ball_in_goal = (
            GOAL_X < self.ball_pos.x < GOAL_X + GOAL_WIDTH
            and GOAL_Y < self.ball_pos.y < GOAL_LINE_Y
        )

        keeper_rect = pygame.Rect(0, 0, KEEPER_WIDTH + self.keeper_stretch, KEEPER_HEIGHT)
        keeper_rect.center = (int(self.keeper_pos.x), int(self.keeper_pos.y))
        ball_rect = pygame.Rect(0, 0, BALL_RADIUS * 2, BALL_RADIUS * 2)
        ball_rect.center = (int(self.ball_pos.x), int(self.ball_pos.y))

        if not ball_in_goal:
            self.misses += 1
            self.result = "Mellé!"
            self.flash_color = GRAY
            self.flash_alpha = 90
            sounds.play_sound(self.sounds, "miss")
        elif keeper_rect.colliderect(ball_rect):
            self.saves += 1
            self.result = "Védés!"
            self.flash_color = SKY_BLUE
            self.flash_alpha = 120
            self.shake_timer = 12
            self.shake_strength = 5
            sounds.play_sound(self.sounds, "save")
        else:
            self.goals += 1
            self.result = "GÓÓÓL!"
            self.flash_color = YELLOW
            self.flash_alpha = 185
            self.shake_timer = 15
            self.shake_strength = 6
            self.create_goal_particles()
            sounds.play_sound(self.sounds, "goal")

        self.message = self.result
        self.message_timer = 95

    def update_high_score(self):
        """A meccs végén frissíti a rekordokat, ha jobb eredmény született."""
        accuracy = self.get_accuracy()
        changed = False

        if self.goals > self.high_score["best_goals"]:
            self.high_score["best_goals"] = self.goals
            changed = True

        if accuracy > self.high_score["best_accuracy"]:
            self.high_score["best_accuracy"] = accuracy
            changed = True

        if changed:
            save_manager.save_high_score(self.high_score)

    def get_accuracy(self):
        """Százalékos gólpontosságot számol."""
        if self.total_shots == 0:
            return 0
        return round(self.goals / self.total_shots * 100)

    def get_final_rating(self):
        """Rövid szöveges értékelést ad a megszerzett gólok alapján."""
        if self.goals >= 9:
            return "Világklasszis teljesítmény!"
        if self.goals >= 7:
            return "Remek sorozat, hidegvérű befejezésekkel."
        if self.goals >= 5:
            return "Stabil meccs, van mire építeni."
        if self.goals >= 3:
            return "Harcos próbálkozás, több pontosság kell."
        return "Nehéz nap volt a tizenegyesponton."

    def handle_event(self, event):
        """Kezeli a billentyűzetet és az egeret."""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_r:
                self.restart_game()
            if self.state == "menu":
                if event.key == pygame.K_1:
                    self.difficulty_key = "konnyu"
                elif event.key == pygame.K_2:
                    self.difficulty_key = "normal"
                elif event.key == pygame.K_3:
                    self.difficulty_key = "nehez"
                elif event.key == pygame.K_RETURN:
                    self.start_game(self.difficulty_key)
            elif self.state == "playing" and event.key == pygame.K_SPACE:
                self.start_shot()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "menu":
                return self.handle_menu_click(event.pos)
            if self.state == "playing":
                self.start_shot()
            elif self.state == "game_over":
                return self.handle_game_over_click(event.pos)

        return True

    def handle_menu_click(self, mouse_pos):
        """Megnézi, hogy a játékos melyik menü gombra kattintott."""
        for rect, action, value in self.menu_buttons:
            if rect.collidepoint(mouse_pos):
                if action == "difficulty":
                    self.difficulty_key = value
                elif action == "team":
                    self.team_key = value
                elif action == "shot_type":
                    self.shot_type_key = value
                elif action == "start":
                    self.start_game(self.difficulty_key)
                elif action == "exit":
                    return False
        return True

    def handle_game_over_click(self, mouse_pos):
        """Kezeli a játék vége képernyő gombjait."""
        for rect, action in self.game_over_buttons:
            if rect.collidepoint(mouse_pos):
                if action == "restart":
                    self.restart_game()
                elif action == "menu":
                    self.change_state("menu")
                elif action == "exit":
                    return False
        return True

    def draw_field(self):
        """Kirajzolja a látványosabb pályát, vonalakat és a kaput."""
        self.screen.fill(SKY_BLUE)
        pygame.draw.rect(self.screen, (38, 78, 120), (0, 0, WIDTH, 58))
        for x in range(0, WIDTH, 36):
            color = RED if (x // 36) % 2 == 0 else WHITE
            pygame.draw.rect(self.screen, color, (x, 16, 24, 28))

        pygame.draw.polygon(self.screen, GREEN, [(0, 58), (WIDTH, 58), (WIDTH, HEIGHT), (0, HEIGHT)])
        for x in range(-80, WIDTH, 90):
            points = [(x + 40, 58), (x + 118, 58), (x + 210, HEIGHT), (x - 30, HEIGHT)]
            pygame.draw.polygon(self.screen, LIGHT_GREEN if (x // 90) % 2 == 0 else DARK_GREEN, points)

        pygame.draw.line(self.screen, WHITE, (0, 410), (WIDTH, 410), 3)
        pygame.draw.circle(self.screen, WHITE, (WIDTH // 2, 410), 86, 3)
        pygame.draw.circle(self.screen, WHITE, (WIDTH // 2, 410), 5)
        pygame.draw.rect(self.screen, WHITE, (170, 58, 560, 265), 3)
        pygame.draw.arc(self.screen, WHITE, (345, 300, 210, 140), math.pi, math.tau, 3)
        pygame.draw.circle(self.screen, WHITE, (int(BALL_START.x), int(BALL_START.y)), 4)
        self.draw_goal_net()

    def draw_goal_net(self):
        """Részletesebb kapuhálót rajzol hátsó mélységgel."""
        back_offset = 28
        back_rect = pygame.Rect(GOAL_X + back_offset, GOAL_Y - back_offset, GOAL_WIDTH - back_offset * 2, GOAL_HEIGHT)
        front_rect = pygame.Rect(GOAL_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT)

        pygame.draw.rect(self.screen, (200, 215, 230), back_rect, 3)
        for x in range(GOAL_X + 25, GOAL_X + GOAL_WIDTH, 25):
            pygame.draw.line(self.screen, NET_COLOR, (x, GOAL_Y), (x - 18, GOAL_LINE_Y), 1)
        for y in range(GOAL_Y + 20, GOAL_LINE_Y, 20):
            pygame.draw.line(self.screen, NET_COLOR, (GOAL_X, y), (GOAL_X + GOAL_WIDTH, y - 10), 1)
        for x in range(GOAL_X - 40, GOAL_X + GOAL_WIDTH, 38):
            pygame.draw.line(self.screen, (198, 216, 232), (x, GOAL_LINE_Y), (x + 90, GOAL_Y), 1)

        pygame.draw.rect(self.screen, WHITE, front_rect, 6)
        pygame.draw.line(self.screen, GRAY, (GOAL_X + 7, GOAL_LINE_Y + 6), (GOAL_X + GOAL_WIDTH - 7, GOAL_LINE_Y + 6), 4)

    def draw_ball(self):
        """Kirajzolja a labdát, amely lövés közben forog és távolodik."""
        scale = 1.0 - self.ball_progress * 0.35
        radius = max(8, int(BALL_RADIUS * scale))
        center = (int(self.ball_pos.x), int(self.ball_pos.y))

        pygame.draw.ellipse(self.screen, (20, 70, 30), (center[0] - radius, center[1] + radius - 2, radius * 2, 8))
        pygame.draw.circle(self.screen, WHITE, center, radius)
        pygame.draw.circle(self.screen, BLACK, center, radius, 2)

        angle = self.ball_spin
        for i in range(5):
            point_angle = angle + i * math.tau / 5
            px = center[0] + int(math.cos(point_angle) * radius * 0.55)
            py = center[1] + int(math.sin(point_angle) * radius * 0.55)
            pygame.draw.circle(self.screen, BLACK, (px, py), max(2, radius // 5))

    def draw_aim(self):
        """Kirajzolja a célkeresztet és a lövés irányát."""
        if self.shooting or self.round_finished:
            return

        x = int(self.aim_pos.x)
        y = int(self.aim_pos.y)
        pygame.draw.circle(self.screen, YELLOW, (x, y), 17, 3)
        pygame.draw.line(self.screen, YELLOW, (x - 25, y), (x + 25, y), 2)
        pygame.draw.line(self.screen, YELLOW, (x, y - 25), (x, y + 25), 2)
        pygame.draw.line(self.screen, ORANGE, (int(BALL_START.x), int(BALL_START.y)), (x, y), 2)

    def draw_power_bar(self):
        """Kirajzolja a modern lövéserő csíkot."""
        bar_x = 260
        bar_y = 475
        bar_w = 380
        bar_h = 24

        ui.draw_panel(self.screen, pygame.Rect(bar_x - 24, bar_y - 48, bar_w + 48, 84), color=PANEL, alpha=180)
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=12)
        fill_w = int(bar_w * self.power)

        ideal_power = self.shot_type["ideal_power"]
        fill_color = MINT if abs(self.power - ideal_power) <= 0.12 else ORANGE
        pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_w, bar_h), border_radius=12)
        ideal_x = bar_x + int(bar_w * ideal_power)
        pygame.draw.line(self.screen, YELLOW, (ideal_x, bar_y - 5), (ideal_x, bar_y + bar_h + 5), 3)
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=12)

        ui.draw_text(self.screen, "Lövéserő", self.fonts["small"], WHITE, topleft=(bar_x, bar_y - 31))
        ui.draw_text(self.screen, "ideális", self.fonts["small"], YELLOW, center=(ideal_x, bar_y + 43))

    def draw_score(self):
        """Kirajzolja az aktuális állást tagolt stat panelen."""
        panel_rect = pygame.Rect(16, 12, 868, 78)
        ui.draw_panel(self.screen, panel_rect, color=PANEL, alpha=210)

        stats = [
            ("Összes lövés", f"{self.total_shots}/{MAX_SHOTS}", WHITE),
            ("Gól", self.goals, YELLOW),
            ("Védés", self.saves, SKY_BLUE),
            ("Mellé", self.misses, RED),
            ("Szint", self.difficulty["label"], MINT),
        ]

        for index, (label, value, color) in enumerate(stats):
            x = 38 + index * 170
            ui.draw_text(self.screen, label, self.fonts["small"], GRAY, topleft=(x, 22), shadow=False)
            ui.draw_text(self.screen, str(value), self.fonts["normal"], color, topleft=(x, 42))

        detail = f"{self.team['name']}   |   {self.shot_type['name']}"
        ui.draw_text(self.screen, detail, self.fonts["small"], MINT, center=(WIDTH // 2, 76), shadow=False)

        message_font = self.fonts["big"] if self.result else self.fonts["normal"]
        message_color = YELLOW if self.result else WHITE
        message_surface = message_font.render(self.message, True, message_color)
        message_rect = message_surface.get_rect(center=(WIDTH // 2, 555))
        pygame.draw.rect(self.screen, BLACK, message_rect.inflate(34, 16), border_radius=12)
        ui.draw_text(self.screen, self.message, message_font, message_color, center=(WIDTH // 2, 555))

    def draw_particles(self):
        """Kirajzolja a gól utáni apró részecskéket."""
        for particle in self.particles:
            pos = particle["pos"]
            pygame.draw.circle(self.screen, particle["color"], (int(pos.x), int(pos.y)), 4)

    def draw_playing(self):
        """Kirajzolja a játék közbeni képernyőt."""
        self.draw_field()
        self.draw_aim()
        goalkeeper.draw_goalkeeper(self.screen, self.keeper_pos, self.keeper_start, self.keeper_target, self.keeper_progress, self.keeper_stretch)
        player.draw_player(self.screen, self.team, self.ball_progress, self.shooting)
        self.draw_ball()
        self.draw_particles()
        self.draw_power_bar()
        self.draw_score()

    def draw_effect_overlays(self):
        """Kirajzolja a villanást és az állapotváltás sötét átúszását."""
        if self.flash_alpha > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((*self.flash_color, self.flash_alpha))
            self.screen.blit(flash, (0, 0))

        if self.transition_alpha > 0:
            transition = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            transition.fill((0, 0, 0, self.transition_alpha))
            self.screen.blit(transition, (0, 0))

    def get_screen_offset(self):
        """Kis képernyőrázkódást ad vissza gólnál vagy védésnél."""
        if self.shake_timer <= 0:
            return (0, 0)
        return (
            random.randint(-self.shake_strength, self.shake_strength),
            random.randint(-self.shake_strength, self.shake_strength),
        )

    def update(self):
        """Az aktuális játékállapot szerint frissít."""
        if self.state == "playing":
            self.update_playing()
        self.update_effects()

    def draw(self):
        """Az aktuális játékállapot szerint rajzol."""
        offset = self.get_screen_offset()

        original_screen = self.screen
        scene = pygame.Surface((WIDTH, HEIGHT))
        self.screen = scene

        if self.state == "menu":
            menu.draw_menu(self.screen, self.fonts, self.draw_field, self)
        elif self.state == "playing":
            self.draw_playing()
        elif self.state == "game_over":
            menu.draw_game_over(self.screen, self.fonts, self.draw_field, self)

        self.screen = original_screen
        self.screen.fill(BLACK)
        self.screen.blit(scene, offset)
        self.draw_effect_overlays()
        pygame.display.flip()

    def run(self):
        """A játék fő ciklusa."""
        running = True
        while running:
            for event in pygame.event.get():
                running = self.handle_event(event)
                if not running:
                    break

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
