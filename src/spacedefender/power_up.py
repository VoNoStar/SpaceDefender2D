from enum import Enum
import random

import pygame

from spacedefender.graphics import (
    draw_antialiased_circle,
    draw_antialiased_polygon,
)


SPAWN_INTERVAL_MIN = 45.0
SPAWN_INTERVAL_MAX = 75.0
POWER_UP_SPEED = 100
ENERGY_COLOR = (255, 220, 65)
SHIELD_COLOR = (90, 210, 255)
LIFE_COLOR = (245, 105, 145)


class PowerUpType(Enum):
    ENERGY = "ENERGY"
    SHIELD = "SHIELD"
    LIFE = "LIFE"


class PowerUp:
    SIZE = 26

    def __init__(self, center: tuple[int, int], kind: PowerUpType) -> None:
        self.x, self.y = center
        self.kind = kind
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = center

    def update(self, delta_time: float) -> None:
        self.y += POWER_UP_SPEED * delta_time
        self.rect.center = (round(self.x), round(self.y))

    def draw(self, surface: pygame.Surface) -> None:
        colors = {
            PowerUpType.ENERGY: ENERGY_COLOR,
            PowerUpType.SHIELD: SHIELD_COLOR,
            PowerUpType.LIFE: LIFE_COLOR,
        }
        color = colors[self.kind]
        draw_antialiased_circle(surface, color, self.rect.center, self.SIZE // 2)
        if self.kind is PowerUpType.ENERGY:
            x, y = self.rect.center
            bolt = [(x + 2, y - 9), (x - 5, y + 1), (x - 1, y + 1), (x - 3, y + 9), (x + 6, y - 3), (x + 2, y - 3)]
            draw_antialiased_polygon(surface, (55, 55, 75), bolt)
        elif self.kind is PowerUpType.SHIELD:
            x, y = self.rect.center
            shield = [(x, y - 9), (x + 7, y - 6), (x + 6, y + 2), (x, y + 9), (x - 6, y + 2), (x - 7, y - 6)]
            draw_antialiased_polygon(surface, (35, 75, 110), shield)
        else:
            x, y = self.rect.center
            draw_antialiased_circle(surface, (255, 240, 245), (x - 4, y - 3), 5)
            draw_antialiased_circle(surface, (255, 240, 245), (x + 4, y - 3), 5)
            draw_antialiased_polygon(
                surface,
                (255, 240, 245),
                [(x - 9, y), (x + 9, y), (x, y + 9)],
            )


class PowerUpSpawner:
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng if rng is not None else random.Random()
        self.timer = self._next_interval()

    def _next_interval(self) -> float:
        return self.rng.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

    def update(self, delta_time: float, screen_width: int) -> PowerUp | None:
        self.timer -= delta_time
        if self.timer > 0:
            return None

        self.timer = self._next_interval()
        kind = self.rng.choice(list(PowerUpType))
        center_x = self.rng.randint(PowerUp.SIZE, screen_width - PowerUp.SIZE)
        return PowerUp((center_x, -PowerUp.SIZE), kind)
