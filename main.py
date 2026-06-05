import math
import random
from array import array

import pygame


# Ablak beallitasai
WIDTH = 900
HEIGHT = 600
FPS = 60

# Szinek
GREEN = (47, 150, 64)
LIGHT_GREEN = (62, 175, 78)
DARK_GREEN = (33, 112, 48)
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
BLUE = (55, 100, 220)
SKY_BLUE = (116, 183, 255)
YELLOW = (245, 210, 65)
ORANGE = (245, 145, 45)
RED = (220, 55, 55)
GRAY = (120, 120, 120)
DARK_GRAY = (45, 45, 45)
NET_COLOR = (218, 232, 245)
SKIN = (245, 190, 135)

# Palya es kapu meretei
GOAL_X = 250
GOAL_Y = 80
GOAL_WIDTH = 500
GOAL_HEIGHT = 180
GOAL_LINE_Y = GOAL_Y + GOAL_HEIGHT

# Labda es jatekos kezdoadatai
BALL_START = pygame.Vector2(WIDTH // 2, 520)
BALL_RADIUS = 14
PLAYER_POS = pygame.Vector2(WIDTH // 2 - 55, 515)

# Kapus kezdoadatai
KEEPER_START = pygame.Vector2(WIDTH // 2, 205)
KEEPER_WIDTH = 86
KEEPER_HEIGHT = 46

MAX_SHOTS = 10

# A nehezseg a kapus ugyesseget es a loves pontatlansagat is befolyasolja.
DIFFICULTIES = {
    "konnyu": {
        "label": "Konnyu",
        "keeper_speed": 0.045,
        "keeper_reach": 70,
        "keeper_reads_shot": 0.25,
        "bad_power_error": 75,
    },
    "normal": {
        "label": "Normal",
        "keeper_speed": 0.060,
        "keeper_reach": 95,
        "keeper_reads_shot": 0.45,
        "bad_power_error": 100,
    },
    "nehez": {
        "label": "Nehez",
        "keeper_speed": 0.078,
        "keeper_reach": 125,
        "keeper_reads_shot": 0.70,
        "bad_power_error": 125,
    },
}


def clamp(value, minimum, maximum):
    """Egy szamot a megadott also es felso hatar koze szorit."""
    return max(minimum, min(value, maximum))


def smoothstep(value):
    """Kicsit termeszetesebb mozgast ad az animacioknak."""
    return value * value * (3 - 2 * value)


def make_tone(frequency, duration, volume=0.35, wave="sine"):
    """Egyszeru hangot keszit fajl nelkul, csak Python kodbol."""
    sample_rate = 44100
    sample_count = int(sample_rate * duration)
    samples = array("h")

    for index in range(sample_count):
        time = index / sample_rate
        fade = 1 - index / sample_count

        if wave == "square":
            value = 1 if math.sin(math.tau * frequency * time) > 0 else -1
        else:
            value = math.sin(math.tau * frequency * time)

        samples.append(int(value * volume * fade * 32767))

    return pygame.mixer.Sound(buffer=samples.tobytes())


class PenaltyGame:
    def __init__(self):
        # A mixer elore beallitasa segit, hogy a generalt hangok jol szoljanak.
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("Tizenegyesrugo jatek")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("arial", 24)
        self.small_font = pygame.font.SysFont("arial", 19)
        self.big_font = pygame.font.SysFont("arial", 44, bold=True)

        self.state = "menu"
        self.difficulty_key = "normal"
        self.menu_buttons = []

        # Latvanyeffektek allapotai
        self.flash_alpha = 0
        self.flash_color = WHITE
        self.transition_alpha = 255
        self.shake_timer = 0
        self.shake_strength = 0
        self.particles = []

        self.sounds = self.create_sounds()
        self.reset_match()

    @property
    def difficulty(self):
        """Rovidites, hogy ne kelljen mindig a szotarban keresni."""
        return DIFFICULTIES[self.difficulty_key]

    def create_sounds(self):
        """Letrehozza a jatek rovid hangjait. Hiba eseten csendben fut tovabb."""
        try:
            return {
                "shoot": make_tone(180, 0.12, 0.35, "square"),
                "goal": make_tone(660, 0.35, 0.35),
                "save": make_tone(95, 0.22, 0.45, "square"),
                "miss": make_tone(240, 0.30, 0.25),
            }
        except pygame.error:
            return {}

    def play_sound(self, name):
        """Biztonsagos hanglejatszas: ha nincs hang, nem tortenik semmi."""
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def reset_match(self):
        """Uj 10 loveses jatekot indit."""
        self.goals = 0
        self.saves = 0
        self.misses = 0
        self.total_shots = 0
        self.message = "Celozz egerrel, allitsd be az erot, majd SPACE vagy bal klikk!"
        self.message_timer = 0
        self.power = 0.5
        self.power_direction = 1
        self.particles = []
        self.reset_round()

    def reset_round(self):
        """Egyetlen loveshez allitja vissza a labdat es a kapust."""
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
        """Allapotvaltas kis sotet atuszas effekttel."""
        self.state = new_state
        self.transition_alpha = 255

    def start_game(self, difficulty_key):
        """A menubol elinditja a jatekot a valasztott nehezseggel."""
        self.difficulty_key = difficulty_key
        self.reset_match()
        self.change_state("playing")

    def restart_game(self):
        """R billentyure ujrakezdi a meccset."""
        if self.state == "menu":
            return
        self.reset_match()
        self.change_state("playing")

    def start_shot(self):
        """Elinditja a loves animaciojat."""
        if self.state != "playing" or self.shooting or self.round_finished:
            return

        self.play_sound("shoot")
        self.shooting = True
        self.round_finished = False
        self.result_checked = False
        self.result = ""
        self.ball_start = self.ball_pos.copy()
        self.ball_progress = 0.0
        self.shake_timer = 6
        self.shake_strength = 3

        # Az idealis ero 70% korul van. Tul gyenge vagy tul eros loves pontatlanabb.
        ideal_power = 0.70
        power_error = abs(self.power - ideal_power)
        max_error = self.difficulty["bad_power_error"] * power_error

        target_x = self.aim_pos.x + random.uniform(-max_error, max_error)
        target_y = self.aim_pos.y + random.uniform(-max_error * 0.55, max_error * 0.55)
        self.ball_target = pygame.Vector2(target_x, target_y)

        # Eros loves gyorsabb, gyenge loves lassabb.
        self.ball_speed = 0.026 + self.power * 0.030
        self.choose_keeper_target()

    def choose_keeper_target(self):
        """Kivalasztja, merre vetodik a kapus."""
        read_chance = self.difficulty["keeper_reads_shot"]
        reach = self.difficulty["keeper_reach"]

        # Jobb nehezsegen a kapus gyakrabban olvassa a loves iranyat.
        if random.random() < read_chance:
            target_x = self.ball_target.x + random.uniform(-45, 45)
        else:
            target_x = random.choice([
                GOAL_X + 95,
                WIDTH // 2,
                GOAL_X + GOAL_WIDTH - 95,
            ])

        target_x = clamp(target_x, GOAL_X + 70, GOAL_X + GOAL_WIDTH - 70)
        target_y = 205 + random.uniform(-24, 14)

        self.keeper_start = self.keeper_pos.copy()
        self.keeper_target = pygame.Vector2(target_x, target_y)
        self.keeper_progress = 0.0
        self.keeper_speed = self.difficulty["keeper_speed"]
        self.keeper_stretch = reach

    def update_playing(self):
        """Frissiti a celzast, erosavot es lovesanimaciot."""
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if not self.shooting and not self.round_finished:
            self.aim_pos.x = clamp(mouse_x, GOAL_X - 100, GOAL_X + GOAL_WIDTH + 100)
            self.aim_pos.y = clamp(mouse_y, GOAL_Y + 18, GOAL_LINE_Y + 95)

            # Az erosav automatikusan mozog. A loves pillanataban levo ertek szamit.
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

            ball_t = smoothstep(self.ball_progress)
            keeper_t = smoothstep(self.keeper_progress)

            self.ball_pos = self.ball_start.lerp(self.ball_target, ball_t)
            self.keeper_pos = self.keeper_start.lerp(self.keeper_target, keeper_t)
            self.ball_spin += self.ball_speed * 10

            if self.ball_progress >= 1.0 and not self.result_checked:
                self.check_result()

        if self.round_finished:
            self.message_timer -= 1
            if self.message_timer <= 0:
                if self.total_shots >= MAX_SHOTS:
                    self.change_state("game_over")
                else:
                    self.reset_round()

    def update_effects(self):
        """Frissiti a villanast, atuszast, razkodast es apro konfettiket."""
        self.flash_alpha = max(0, self.flash_alpha - 12)
        self.transition_alpha = max(0, self.transition_alpha - 14)
        self.shake_timer = max(0, self.shake_timer - 1)

        for particle in self.particles:
            particle["pos"] += particle["vel"]
            particle["vel"].y += 0.18
            particle["life"] -= 1

        self.particles = [particle for particle in self.particles if particle["life"] > 0]

    def create_goal_particles(self):
        """Golnal kis konfetti-szeru reszecskeket dob a kapu ele."""
        for _ in range(36):
            self.particles.append({
                "pos": pygame.Vector2(random.randint(GOAL_X + 40, GOAL_X + GOAL_WIDTH - 40), GOAL_Y + 20),
                "vel": pygame.Vector2(random.uniform(-3.0, 3.0), random.uniform(-5.0, -1.5)),
                "color": random.choice([YELLOW, ORANGE, WHITE, RED]),
                "life": random.randint(30, 55),
            })

    def check_result(self):
        """Eldonti, hogy gol, vedes vagy melle loves tortent."""
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
            self.result = "MELLE!"
            self.flash_color = GRAY
            self.flash_alpha = 90
            self.play_sound("miss")
        elif keeper_rect.colliderect(ball_rect):
            self.saves += 1
            self.result = "VEDES!"
            self.flash_color = SKY_BLUE
            self.flash_alpha = 120
            self.shake_timer = 12
            self.shake_strength = 5
            self.play_sound("save")
        else:
            self.goals += 1
            self.result = "GOOOL!"
            self.flash_color = YELLOW
            self.flash_alpha = 185
            self.shake_timer = 15
            self.shake_strength = 6
            self.create_goal_particles()
            self.play_sound("goal")

        self.message = self.result
        self.message_timer = 95

    def handle_event(self, event):
        """Kezeli a billentyuzetet es az egeret."""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_r:
                self.restart_game()
            if self.state == "menu":
                if event.key == pygame.K_1:
                    self.start_game("konnyu")
                elif event.key == pygame.K_2:
                    self.start_game("normal")
                elif event.key == pygame.K_3:
                    self.start_game("nehez")
            elif self.state == "playing" and event.key == pygame.K_SPACE:
                self.start_shot()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "menu":
                self.handle_menu_click(event.pos)
            elif self.state == "playing":
                self.start_shot()
            elif self.state == "game_over":
                self.change_state("menu")

        return True

    def handle_menu_click(self, mouse_pos):
        """Megnezi, hogy a jatekos melyik menu gombra kattintott."""
        for rect, difficulty_key in self.menu_buttons:
            if rect.collidepoint(mouse_pos):
                self.start_game(difficulty_key)

    def draw_field(self):
        """Kirajzolja a latvanyosabb palyat, vonalakat es a kaput."""
        # Egbolt es tavoli lelato egyszeru hatterkent.
        self.screen.fill(SKY_BLUE)
        pygame.draw.rect(self.screen, (38, 78, 120), (0, 0, WIDTH, 58))
        for x in range(0, WIDTH, 36):
            color = RED if (x // 36) % 2 == 0 else WHITE
            pygame.draw.rect(self.screen, color, (x, 16, 24, 28))

        # Fuves palya csikokkal es enyhe perspektivaval.
        pygame.draw.polygon(self.screen, GREEN, [(0, 58), (WIDTH, 58), (WIDTH, HEIGHT), (0, HEIGHT)])
        for x in range(-80, WIDTH, 90):
            points = [
                (x + 40, 58),
                (x + 118, 58),
                (x + 210, HEIGHT),
                (x - 30, HEIGHT),
            ]
            pygame.draw.polygon(self.screen, LIGHT_GREEN if (x // 90) % 2 == 0 else DARK_GREEN, points)

        pygame.draw.line(self.screen, WHITE, (0, 410), (WIDTH, 410), 3)
        pygame.draw.circle(self.screen, WHITE, (WIDTH // 2, 410), 86, 3)
        pygame.draw.circle(self.screen, WHITE, (WIDTH // 2, 410), 5)

        # Tizenhatos es buntetoterulet jelzes.
        pygame.draw.rect(self.screen, WHITE, (170, 58, 560, 265), 3)
        pygame.draw.arc(self.screen, WHITE, (345, 300, 210, 140), math.pi, math.tau, 3)
        pygame.draw.circle(self.screen, WHITE, (int(BALL_START.x), int(BALL_START.y)), 4)

        self.draw_goal_net()

    def draw_goal_net(self):
        """Reszletesebb kapuhalot rajzol hatso melyseggel."""
        back_offset = 28
        back_rect = pygame.Rect(GOAL_X + back_offset, GOAL_Y - back_offset, GOAL_WIDTH - back_offset * 2, GOAL_HEIGHT)
        front_rect = pygame.Rect(GOAL_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT)

        pygame.draw.rect(self.screen, (200, 215, 230), back_rect, 3)

        # Halo vizszintes, fuggoleges es atlos szalakkal.
        for x in range(GOAL_X + 25, GOAL_X + GOAL_WIDTH, 25):
            pygame.draw.line(self.screen, NET_COLOR, (x, GOAL_Y), (x - 18, GOAL_LINE_Y), 1)
        for y in range(GOAL_Y + 20, GOAL_LINE_Y, 20):
            pygame.draw.line(self.screen, NET_COLOR, (GOAL_X, y), (GOAL_X + GOAL_WIDTH, y - 10), 1)
        for x in range(GOAL_X - 40, GOAL_X + GOAL_WIDTH, 38):
            pygame.draw.line(self.screen, (198, 216, 232), (x, GOAL_LINE_Y), (x + 90, GOAL_Y), 1)

        # Vastag kapufa es felso lec.
        pygame.draw.rect(self.screen, WHITE, front_rect, 6)
        pygame.draw.line(self.screen, GRAY, (GOAL_X + 7, GOAL_LINE_Y + 6), (GOAL_X + GOAL_WIDTH - 7, GOAL_LINE_Y + 6), 4)

    def draw_player(self):
        """Egyszeru rugo jatekosfigura a labda mogott."""
        x = int(PLAYER_POS.x)
        y = int(PLAYER_POS.y)
        kick = self.ball_progress if self.shooting else 0
        leg_swing = int(20 * math.sin(kick * math.pi))

        pygame.draw.ellipse(self.screen, (20, 70, 30), (x - 32, y + 28, 70, 14))
        pygame.draw.circle(self.screen, SKIN, (x, y - 72), 17)
        pygame.draw.rect(self.screen, RED, (x - 20, y - 55, 40, 50), border_radius=8)
        pygame.draw.line(self.screen, SKIN, (x - 18, y - 42), (x - 42, y - 22), 7)
        pygame.draw.line(self.screen, SKIN, (x + 18, y - 42), (x + 38, y - 18), 7)
        pygame.draw.line(self.screen, BLUE, (x - 10, y - 5), (x - 26, y + 30), 8)
        pygame.draw.line(self.screen, BLUE, (x + 10, y - 5), (x + 23 + leg_swing, y + 30), 8)
        pygame.draw.circle(self.screen, BLACK, (x - 27, y + 34), 5)
        pygame.draw.circle(self.screen, BLACK, (x + 25 + leg_swing, y + 34), 5)

    def draw_keeper(self):
        """Kirajzolja a kapust latvanyosabb vetodessel."""
        direction = 0
        if self.keeper_target.x < self.keeper_start.x - 5:
            direction = -1
        elif self.keeper_target.x > self.keeper_start.x + 5:
            direction = 1

        dive = smoothstep(self.keeper_progress)
        body_w = KEEPER_WIDTH + int(22 * dive)
        body_h = KEEPER_HEIGHT - int(10 * dive)
        body_rect = pygame.Rect(0, 0, body_w, body_h)
        body_rect.center = (int(self.keeper_pos.x), int(self.keeper_pos.y))

        pygame.draw.ellipse(self.screen, (20, 70, 30), (body_rect.x - 14, body_rect.y + 35, body_rect.w + 28, 18))
        pygame.draw.ellipse(self.screen, BLUE, body_rect)

        head_x = int(self.keeper_pos.x + direction * 24 * dive)
        head_y = int(self.keeper_pos.y - 35 + 10 * dive)
        pygame.draw.circle(self.screen, SKIN, (head_x, head_y), 18)

        arm_y = int(self.keeper_pos.y)
        reach = 60 + int(self.keeper_stretch * self.keeper_progress)
        glove_color = WHITE

        if direction < 0:
            pygame.draw.line(self.screen, BLUE, (int(self.keeper_pos.x), arm_y), (int(self.keeper_pos.x - reach), arm_y - 34), 11)
            pygame.draw.line(self.screen, BLUE, (int(self.keeper_pos.x), arm_y), (int(self.keeper_pos.x + 46), arm_y + 18), 10)
            pygame.draw.circle(self.screen, glove_color, (int(self.keeper_pos.x - reach), arm_y - 34), 10)
        elif direction > 0:
            pygame.draw.line(self.screen, BLUE, (int(self.keeper_pos.x), arm_y), (int(self.keeper_pos.x + reach), arm_y - 34), 11)
            pygame.draw.line(self.screen, BLUE, (int(self.keeper_pos.x), arm_y), (int(self.keeper_pos.x - 46), arm_y + 18), 10)
            pygame.draw.circle(self.screen, glove_color, (int(self.keeper_pos.x + reach), arm_y - 34), 10)
        else:
            pygame.draw.line(self.screen, BLUE, (int(self.keeper_pos.x - reach // 2), arm_y), (int(self.keeper_pos.x + reach // 2), arm_y), 11)
            pygame.draw.circle(self.screen, glove_color, (int(self.keeper_pos.x - reach // 2), arm_y), 9)
            pygame.draw.circle(self.screen, glove_color, (int(self.keeper_pos.x + reach // 2), arm_y), 9)

        pygame.draw.line(self.screen, BLUE, (int(self.keeper_pos.x - 20), int(self.keeper_pos.y + 15)), (int(self.keeper_pos.x - 45), int(self.keeper_pos.y + 44)), 9)
        pygame.draw.line(self.screen, BLUE, (int(self.keeper_pos.x + 20), int(self.keeper_pos.y + 15)), (int(self.keeper_pos.x + 45), int(self.keeper_pos.y + 44)), 9)

    def draw_ball(self):
        """Kirajzolja a labdat, amely loves kozben forog es tavolodik."""
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
        """Kirajzolja a celkeresztet es a loves iranyat."""
        if self.shooting or self.round_finished:
            return

        x = int(self.aim_pos.x)
        y = int(self.aim_pos.y)
        pygame.draw.circle(self.screen, YELLOW, (x, y), 17, 3)
        pygame.draw.line(self.screen, YELLOW, (x - 25, y), (x + 25, y), 2)
        pygame.draw.line(self.screen, YELLOW, (x, y - 25), (x, y + 25), 2)
        pygame.draw.line(self.screen, ORANGE, (int(BALL_START.x), int(BALL_START.y)), (x, y), 2)

    def draw_power_bar(self):
        """Kirajzolja a lovesero csikot."""
        bar_x = 260
        bar_y = 475
        bar_w = 380
        bar_h = 22

        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=8)
        fill_w = int(bar_w * self.power)

        # A kozepes-eros loves a legjobb, ezt sarga jelolo mutatja.
        pygame.draw.rect(self.screen, ORANGE, (bar_x, bar_y, fill_w, bar_h), border_radius=8)
        ideal_x = bar_x + int(bar_w * 0.70)
        pygame.draw.line(self.screen, YELLOW, (ideal_x, bar_y - 5), (ideal_x, bar_y + bar_h + 5), 3)
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

        label = self.small_font.render("Lovesero", True, WHITE)
        self.screen.blit(label, (bar_x, bar_y - 28))

    def draw_score(self):
        """Kirajzolja az aktualis allast."""
        score = (
            f"Loves: {self.total_shots}/{MAX_SHOTS}   Golok: {self.goals}   "
            f"Vedesek: {self.saves}   Melle: {self.misses}   "
            f"Szint: {self.difficulty['label']}"
        )
        score_surface = self.font.render(score, True, WHITE)
        pygame.draw.rect(self.screen, (0, 0, 0), (14, 12, 650, 42), border_radius=8)
        self.screen.blit(score_surface, (24, 20))

        if self.result:
            message_surface = self.big_font.render(self.message, True, YELLOW)
        else:
            message_surface = self.font.render(self.message, True, WHITE)

        message_rect = message_surface.get_rect(center=(WIDTH // 2, 555))
        pygame.draw.rect(self.screen, BLACK, message_rect.inflate(28, 14), border_radius=8)
        self.screen.blit(message_surface, message_rect)

    def draw_particles(self):
        """Kirajzolja a gol utani apro reszecskeket."""
        for particle in self.particles:
            pos = particle["pos"]
            pygame.draw.circle(self.screen, particle["color"], (int(pos.x), int(pos.y)), 4)

    def draw_menu(self):
        """Kezdomenu nehezsegi szintekkel."""
        self.draw_field()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 70))
        self.screen.blit(overlay, (0, 0))

        title = self.big_font.render("Tizenegyesrugo jatek", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        subtitle = self.font.render("Valassz nehezseget: 1, 2, 3 vagy kattintas", True, WHITE)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 205)))

        self.menu_buttons = []
        button_data = [("konnyu", "1 - Konnyu"), ("normal", "2 - Normal"), ("nehez", "3 - Nehez")]
        for index, (difficulty_key, text) in enumerate(button_data):
            rect = pygame.Rect(0, 0, 230, 54)
            rect.center = (WIDTH // 2, 285 + index * 72)
            self.menu_buttons.append((rect, difficulty_key))
            color = ORANGE if difficulty_key == self.difficulty_key else DARK_GRAY
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
            label = self.font.render(text, True, WHITE)
            self.screen.blit(label, label.get_rect(center=rect.center))

        hint = self.small_font.render("ESC: kilepes   R: ujrakezdes jatek kozben", True, WHITE)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 535)))

    def draw_game_over(self):
        """Jatek vege kepernyo vegso osszesitessel."""
        self.draw_field()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 85))
        self.screen.blit(overlay, (0, 0))

        title = self.big_font.render("Jatek vege", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 145)))

        accuracy = 0
        if self.total_shots > 0:
            accuracy = round(self.goals / self.total_shots * 100)

        lines = [
            f"Nehezseg: {self.difficulty['label']}",
            f"Osszes loves: {self.total_shots}",
            f"Golok: {self.goals}",
            f"Vedesek: {self.saves}",
            f"Melle lovesek: {self.misses}",
            f"Golpontossag: {accuracy}%",
        ]

        for index, line in enumerate(lines):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, 225 + index * 38)))

        restart = self.font.render("R: uj jatek   Kattintas: menu   ESC: kilepes", True, YELLOW)
        self.screen.blit(restart, restart.get_rect(center=(WIDTH // 2, 520)))

    def draw_playing(self):
        """Kirajzolja a jatek kozbeni kepernyot."""
        self.draw_field()
        self.draw_aim()
        self.draw_keeper()
        self.draw_player()
        self.draw_ball()
        self.draw_particles()
        self.draw_power_bar()
        self.draw_score()

    def draw_effect_overlays(self):
        """Kirajzolja a villanast es az allapotvaltas sotet atuszasat."""
        if self.flash_alpha > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((*self.flash_color, self.flash_alpha))
            self.screen.blit(flash, (0, 0))

        if self.transition_alpha > 0:
            transition = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            transition.fill((0, 0, 0, self.transition_alpha))
            self.screen.blit(transition, (0, 0))

    def get_screen_offset(self):
        """Kis kepernyorazkodast ad vissza golnal vagy vedesnel."""
        if self.shake_timer <= 0:
            return (0, 0)
        return (
            random.randint(-self.shake_strength, self.shake_strength),
            random.randint(-self.shake_strength, self.shake_strength),
        )

    def update(self):
        """Az aktualis jatekallapot szerint frissit."""
        if self.state == "playing":
            self.update_playing()
        self.update_effects()

    def draw(self):
        """Az aktualis jatekallapot szerint rajzol."""
        offset = self.get_screen_offset()

        # Egy ideiglenes feluletre rajzolunk, igy egyszeruen razhato az egesz kep.
        original_screen = self.screen
        scene = pygame.Surface((WIDTH, HEIGHT))
        self.screen = scene

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_playing()
        elif self.state == "game_over":
            self.draw_game_over()

        self.screen = original_screen
        self.screen.fill(BLACK)
        self.screen.blit(scene, offset)
        self.draw_effect_overlays()
        pygame.display.flip()

    def run(self):
        """A jatek fo ciklusa."""
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


if __name__ == "__main__":
    game = PenaltyGame()
    game.run()
