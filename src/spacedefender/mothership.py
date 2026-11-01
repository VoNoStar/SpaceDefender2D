import pygame

from spacedefender.enemy_projectile import VULCANO_PROJECTILE_SPEED, EnemyProjectile
from spacedefender.graphics import (
    draw_antialiased_circle,
    draw_antialiased_ellipse,
    draw_antialiased_polygon,
)


MOTHERSHIP_COLOR = (180, 90, 55)
MOTHERSHIP_SPEED = 55
MOTHERSHIP_SHOT_INTERVAL = 0.8
MOTHERSHIP_HITS_TO_DEFEAT = 20
MOTHERSHIP_PROJECTILE_SPEED = VULCANO_PROJECTILE_SPEED + 60


class Mothership:
    SIZE = (150, 68)

    def __init__(self, center: tuple[int, int]) -> None:
        self.rect = pygame.Rect(0, 0, *self.SIZE)
        self.rect.center = center
        self.direction = 1
        self.movement_remainder = 0.0
        self.shot_timer = 0.0
        self.hits_remaining = MOTHERSHIP_HITS_TO_DEFEAT

    def update(
        self,
        delta_time: float,
        screen_width: int,
        player_center: tuple[int, int],
    ) -> EnemyProjectile | None:
        next_left = self.rect.left + self.direction * MOTHERSHIP_SPEED * delta_time
        next_right = self.rect.right + self.direction * MOTHERSHIP_SPEED * delta_time
        if next_left < 0 or next_right > screen_width:
            self.direction *= -1
            self.movement_remainder = 0.0
        else:
            self.movement_remainder += (
                self.direction * MOTHERSHIP_SPEED * delta_time
            )
            movement = int(self.movement_remainder)
            self.movement_remainder -= movement
            self.rect.x += movement

        self.shot_timer += delta_time
        if self.shot_timer < MOTHERSHIP_SHOT_INTERVAL:
            return None

        self.shot_timer -= MOTHERSHIP_SHOT_INTERVAL
        origin = self.rect.midbottom
        direction = (
            player_center[0] - origin[0],
            player_center[1] - origin[1],
        )
        return EnemyProjectile(
            origin,
            MOTHERSHIP_PROJECTILE_SPEED,
            direction,
        )

    def take_hit(self, damage: int = 1) -> bool:
        self.hits_remaining = max(0, self.hits_remaining - damage)
        return self.hits_remaining <= 0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        x, y = self.rect.center
        draw_antialiased_ellipse(
            surface,
            (75, 43, 48),
            (self.rect.left + 12, y - 16, self.rect.width - 24, 42),
        )
        draw_antialiased_polygon(
            surface,
            MOTHERSHIP_COLOR,
            [
                (x - 30, y - 17),
                (x - 58, y - 27),
                (self.rect.left, y - 7),
                (self.rect.left + 12, y + 15),
                (self.rect.right - 12, y + 15),
                (self.rect.right, y - 7),
                (x + 58, y - 27),
                (x + 30, y - 17),
            ],
        )
        draw_antialiased_ellipse(
            surface,
            (235, 155, 85),
            (x - 19, y - 22, 38, 25),
        )
        for window_x in range(self.rect.left + 27, self.rect.right - 20, 24):
            draw_antialiased_circle(
                surface, (255, 224, 140), (window_x, y + 1), 3
            )
        label = font.render(
            f"NAVE NODRIZA {self.hits_remaining}/{MOTHERSHIP_HITS_TO_DEFEAT}",
            True,
            (255, 245, 220),
        )
        surface.blit(label, label.get_rect(midbottom=(x, self.rect.top - 5)))
