import pygame

from spacedefender.enemy_projectile import EnemyProjectile
from spacedefender.graphics import (
    draw_antialiased_circle,
    draw_antialiased_ellipse,
    draw_antialiased_polygon,
)


ENEMY_COLOR = (100, 220, 120)
ENEMY_DETAIL_COLOR = (235, 240, 255)
ENEMY_SPEED = 67.5
DESCENT_STEP = 22
SHOT_INTERVAL = 1.8


class Enemy:
    SIZE = (44, 34)

    def __init__(self, center: tuple[int, int]) -> None:
        self.rect = pygame.Rect(0, 0, *self.SIZE)
        self.rect.center = center

    def shoot(self) -> EnemyProjectile:
        return EnemyProjectile(self.rect.midbottom)

    def draw(self, surface: pygame.Surface) -> None:
        x, y = self.rect.center
        shadow = (25, 67, 55)
        dark_green = (45, 122, 79)
        light_green = (155, 229, 143)
        draw_antialiased_polygon(
            surface,
            shadow,
            [(x - 17, y - 2), (x - 22, y + 7), (x - 12, y + 5)],
        )
        draw_antialiased_polygon(
            surface,
            shadow,
            [(x + 17, y - 2), (x + 22, y + 7), (x + 12, y + 5)],
        )
        draw_antialiased_ellipse(surface, shadow, (x - 22, y - 10, 44, 27))
        draw_antialiased_ellipse(surface, ENEMY_COLOR, (x - 20, y - 13, 40, 24))
        draw_antialiased_ellipse(surface, dark_green, (x - 12, y - 12, 24, 15))
        draw_antialiased_ellipse(surface, light_green, (x - 8, y - 11, 16, 8))
        for eye_x in (x - 9, x + 9):
            draw_antialiased_circle(surface, ENEMY_DETAIL_COLOR, (eye_x, y - 2), 3)
            draw_antialiased_circle(surface, (28, 62, 54), (eye_x, y - 2), 1)
        draw_antialiased_polygon(
            surface,
            dark_green,
            [(x - 7, y + 7), (x - 3, y + 11), (x, y + 7), (x + 3, y + 11), (x + 7, y + 7)],
        )


class EnemyFormation:
    def __init__(self, enemies: list[Enemy]) -> None:
        self.enemies = enemies
        self.direction = 1
        self.movement_remainder = 0.0
        self.shot_timer = 0.0
        self.next_shooter = 0

    def update(
        self, delta_time: float, screen_width: int
    ) -> EnemyProjectile | None:
        if not self.enemies:
            return None

        left_edge = min(enemy.rect.left for enemy in self.enemies)
        right_edge = max(enemy.rect.right for enemy in self.enemies)
        next_left = left_edge + self.direction * ENEMY_SPEED * delta_time
        next_right = right_edge + self.direction * ENEMY_SPEED * delta_time
        if next_left < 0 or next_right > screen_width:
            self.direction *= -1
            self.movement_remainder = 0.0
            for enemy in self.enemies:
                enemy.rect.y += DESCENT_STEP
        else:
            self.movement_remainder += self.direction * ENEMY_SPEED * delta_time
            movement = int(self.movement_remainder)
            self.movement_remainder -= movement
            for enemy in self.enemies:
                enemy.rect.x += movement

        self.shot_timer += delta_time
        if self.shot_timer < SHOT_INTERVAL:
            return None

        self.shot_timer -= SHOT_INTERVAL
        shooter = self.enemies[self.next_shooter % len(self.enemies)]
        self.next_shooter += 1
        return shooter.shoot()
