import math
import random
import pygame

from game.player import Player
from game.world import generate_platforms, draw_lava, PLATFORM_COLOR


WIDTH, HEIGHT = 500, 640
FPS = 60
BG = (20, 15, 30)
GROUND_Y = HEIGHT + 200

# Task 2
CRUMBLE_FRAMES = 45
FRAGILE_CHANCE = 0.30

# Task 3
SPRING_CHANCE = 0.20


class GameEngine:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Lava Escape"
        )

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace",
            24,
            bold=True
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            42,
            bold=True
        )

        self.reset()

    def reset(self):
        self.platforms = generate_platforms(
            WIDTH,
            GROUND_Y
        )

        self.player = Player(
            WIDTH // 2 - 16,
            GROUND_Y - 50
        )

        self.cam_y = 0
        self.lava_y = GROUND_Y + 60
        self.lava_rise = 0.4

        self.score = 0
        self.game_over = False
        self.won = False

        self.top_y = self.platforms[-1].y
        self.frame = 0

        # ------------------------------------------------
        # TASK 2: Fragile platforms
        # ------------------------------------------------

        self.fragile_platforms = {
            id(p)
            for p in self.platforms[1:]
            if random.random() < FRAGILE_CHANCE
        }

        self.crumble_timers = {
            id(p): None
            for p in self.platforms
            if id(p) in self.fragile_platforms
        }

        # ------------------------------------------------
        # TASK 3: Spring platforms
        # ------------------------------------------------

        self.spring_platforms = {
            id(p)
            for p in self.platforms[1:]
            if (
                id(p) not in self.fragile_platforms
                and random.random() < SPRING_CHANCE
            )
        }

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):
                self.reset()

        return True

    def update(self):
        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()

        # Player returns the platform landed on.
        landed = self.player.update(
            keys,
            self.platforms,
            WIDTH,
            self.spring_platforms
        )

        # ------------------------------------------------
        # TASK 2: Start crumbling after landing
        # ------------------------------------------------

        if (
            landed is not None
            and id(landed) in self.fragile_platforms
        ):
            if self.crumble_timers[id(landed)] is None:
                self.crumble_timers[id(landed)] = CRUMBLE_FRAMES

        target = (
            self.player.rect.centery
            - HEIGHT // 2
        )

        if target < self.cam_y:
            self.cam_y = target

        self.lava_y -= self.lava_rise

        self.lava_rise = min(
            1.2,
            self.lava_rise + 0.0003
        )

        self.score = max(
            0,
            (GROUND_Y - self.player.rect.y) // 10
        )

        # ------------------------------------------------
        # TASK 2: Crumbling countdown
        # ------------------------------------------------

        removed = []

        for p in self.platforms:

            timer = self.crumble_timers.get(
                id(p)
            )

            if timer is not None:

                timer -= 1

                self.crumble_timers[id(p)] = timer

                if timer <= 0:
                    removed.append(p)

        for p in removed:

            self.platforms.remove(p)

            self.fragile_platforms.discard(
                id(p)
            )

            self.crumble_timers.pop(
                id(p),
                None
            )

            # A removed fragile platform cannot
            # remain a spring platform.
            self.spring_platforms.discard(
                id(p)
            )

        self.frame += 1

        if self.player.rect.bottom >= self.lava_y:
            self.game_over = True

        if self.player.rect.top <= self.top_y - 20:
            self.won = True

    def draw(self):
        self.screen.fill(BG)

        for p in self.platforms:

            timer = self.crumble_timers.get(
                id(p)
            )

            offset_x = 0
            offset_y = 0

            # ------------------------------------------------
            # TASK 2: Shake fragile platforms
            # ------------------------------------------------

            if timer is not None:

                shake = (
                    2
                    + (CRUMBLE_FRAMES - timer) // 15
                )

                offset_x = int(
                    math.sin(
                        self.frame * 1.8 + id(p)
                    ) * shake
                )

                offset_y = int(
                    math.sin(
                        self.frame * 2.3 + id(p)
                    )
                )

            dr = p.move(
                offset_x,
                offset_y - int(self.cam_y)
            )

            # ------------------------------------------------
            # TASK 3: Draw spring platforms differently
            # ------------------------------------------------

            if id(p) in self.spring_platforms:

                spring_color = (
                    70,
                    220,
                    110
                )

                pygame.draw.rect(
                    self.screen,
                    spring_color,
                    dr,
                    border_radius=4
                )

                # Spring symbol.
                spring_y = dr.top - 7

                pygame.draw.line(
                    self.screen,
                    (230, 240, 120),
                    (
                        dr.centerx - 8,
                        spring_y
                    ),
                    (
                        dr.centerx - 4,
                        spring_y - 5
                    ),
                    2
                )

                pygame.draw.line(
                    self.screen,
                    (230, 240, 120),
                    (
                        dr.centerx - 4,
                        spring_y - 5
                    ),
                    (
                        dr.centerx,
                        spring_y
                    ),
                    2
                )

                pygame.draw.line(
                    self.screen,
                    (230, 240, 120),
                    (
                        dr.centerx,
                        spring_y
                    ),
                    (
                        dr.centerx + 4,
                        spring_y - 5
                    ),
                    2
                )

                pygame.draw.line(
                    self.screen,
                    (230, 240, 120),
                    (
                        dr.centerx + 4,
                        spring_y - 5
                    ),
                    (
                        dr.centerx + 8,
                        spring_y
                    ),
                    2
                )

            else:

                pygame.draw.rect(
                    self.screen,
                    PLATFORM_COLOR,
                    dr,
                    border_radius=4
                )

            # ------------------------------------------------
            # TASK 2: Draw cracks
            # ------------------------------------------------

            if timer is not None:

                crack_x = (
                    dr.left
                    + dr.width // 2
                )

                pygame.draw.line(
                    self.screen,
                    (35, 25, 20),
                    (
                        crack_x,
                        dr.top + 2
                    ),
                    (
                        crack_x - 7,
                        dr.bottom - 2
                    ),
                    2
                )

                pygame.draw.line(
                    self.screen,
                    (35, 25, 20),
                    (
                        crack_x,
                        dr.top + 2
                    ),
                    (
                        crack_x + 8,
                        dr.bottom - 3
                    ),
                    2
                )

        self.player.draw(
            self.screen,
            self.cam_y
        )

        draw_lava(
            self.screen,
            self.lava_y,
            self.cam_y,
            WIDTH,
            HEIGHT,
            self.frame
        )

        sc = self.font.render(
            f"Height: {self.score}m  R=Restart",
            True,
            (220, 200, 180)
        )

        self.screen.blit(
            sc,
            (8, 10)
        )

        if self.game_over:
            self._msg(
                "LAVA GOT YOU!",
                (220, 80, 40)
            )

        if self.won:
            self._msg(
                "ESCAPED!",
                (80, 220, 100)
            )

        pygame.display.flip()

    def _msg(self, text, color):
        ov = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        ov.fill(
            (0, 0, 0, 150)
        )

        self.screen.blit(
            ov,
            (0, 0)
        )

        m = self.big_font.render(
            text,
            True,
            color
        )

        s = self.font.render(
            "Press R to Play Again",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            m,
            (
                WIDTH // 2
                - m.get_width() // 2,
                HEIGHT // 2 - 40
            )
        )

        self.screen.blit(
            s,
            (
                WIDTH // 2
                - s.get_width() // 2,
                HEIGHT // 2 + 20
            )
        )

    def run(self):
        running = True

        while running:

            running = self.handle_events()

            self.update()
            self.draw()

            self.clock.tick(FPS)

        pygame.quit()