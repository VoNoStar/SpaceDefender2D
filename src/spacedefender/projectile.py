import pygame

from spacedefender.graphics import (
    draw_antialiased_polygon,
    draw_antialiased_rounded_rect,
)


PROJECTILE_COLOR = (100, 220, 255)
PROJECTILE_SPEED = 520


class Projectile:
    def __init__(
        self,
        center: tuple[int, int],
        direction: tuple[float, float] = (0, -1),
    ) -> None:
        self.x, self.y = center
        self.direction = pygame.Vector2(direction).normalize()
        self.rect = pygame.Rect(self.x - 3, self.y - 12, 6, 16)
        self.damage = 1

    def update(self, delta_time: float) -> None:
        self.x += self.direction.x * PROJECTILE_SPEED * delta_time
        self.y += self.direction.y * PROJECTILE_SPEED * delta_time
        self.rect.center = (round(self.x), round(self.y))

    def draw(self, surface: pygame.Surface) -> None:
        draw_antialiased_rounded_rect(surface, PROJECTILE_COLOR, self.rect, radius=3)


class Missile(Projectile):
    def __init__(self, center: tuple[int, int], direction: tuple[float, float]) -> None:
        super().__init__(center, direction)
        self.rect = pygame.Rect(self.x - 5, self.y - 14, 10, 20)

    def draw(self, surface: pygame.Surface) -> None:
        x, y = self.rect.center
        draw_antialiased_polygon(
            surface,
            (255, 160, 65),
            [(x, y - 12), (x + 5, y + 7), (x, y + 4), (x - 5, y + 7)],
        )
        pygame.draw.line(surface, (255, 225, 125), (x, y + 6), (x, y + 12), 2)


class LaserProjectile(Projectile):
    def __init__(self, center: tuple[int, int]) -> None:
        super().__init__(center)
        self.damage = 2
        self.rect = pygame.Rect(self.x - 7, self.y - 28, 14, 36)

    def draw(self, surface: pygame.Surface) -> None:
        draw_antialiased_rounded_rect(surface, (40, 160, 255), self.rect, radius=6)
        draw_antialiased_rounded_rect(
            surface,
            (205, 250, 255),
            self.rect.inflate(-8, -2),
            radius=4,
        )
