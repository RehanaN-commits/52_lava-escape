import pygame

SPEED = 4

# Task 3: high-powered spring jump
SPRING_VELOCITY = -19


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0
        self.on_ground = False
        self.color = (60, 160, 220)

    def update(self, keys, platforms, width, spring_platforms=None):
        if spring_platforms is None:
            spring_platforms = set()

        dx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED

        if (
            keys[pygame.K_SPACE]
            or keys[pygame.K_w]
            or keys[pygame.K_UP]
        ) and self.on_ground:
            self.vel_y = -13
            self.on_ground = False

        self.vel_y = min(self.vel_y + 0.55, 12)

        self.rect.x = max(
            0,
            min(width - self.rect.width, self.rect.x + dx)
        )

        # Store player's bottom before vertical movement.
        previous_bottom = self.rect.bottom

        self.rect.y += int(self.vel_y)
        self.on_ground = False

        landed_platform = None

        # One-way platform collision.
        # Landing only happens while descending and
        # when crossing the platform's top edge.
        for p in platforms:
            if (
                self.vel_y > 0
                and previous_bottom <= p.top
                and self.rect.bottom >= p.top
                and self.rect.right > p.left
                and self.rect.left < p.right
            ):
                self.rect.bottom = p.top
                self.on_ground = True
                landed_platform = p

                # Task 3:
                # Spring platforms launch the player much higher.
                if id(p) in spring_platforms:
                    self.vel_y = SPRING_VELOCITY
                    self.on_ground = False
                else:
                    self.vel_y = 0

                break

        return landed_platform

    def draw(self, screen, cam_y):
        dr = self.rect.move(
            0,
            -int(cam_y)
        )

        pygame.draw.rect(
            screen,
            self.color,
            dr,
            border_radius=6
        )

        pygame.draw.circle(
            screen,
            (255, 220, 180),
            (dr.centerx, dr.top + 8),
            7
        )