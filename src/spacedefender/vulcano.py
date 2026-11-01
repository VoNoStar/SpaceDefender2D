import pygame

from spacedefender.enemy_projectile import (
    VULCANO_PROJECTILE_SPEED,
    EnemyProjectile,
)
from spacedefender.graphics import (
    draw_antialiased_circle,
    draw_antialiased_ellipse,
    draw_antialiased_polygon,
)


VULCANO_COLOR = (195, 65, 225)
VULCANO_SPEED = 75
VULCANO_SHOT_INTERVAL = 0.65
VULCANO_HITS_TO_DEFEAT = 10


class Vulcano:
    SIZE = (76, 48)

    def __init__(self, center: tuple[int, int]) -> None:
        self.rect = pygame.Rect(0, 0, *self.SIZE)
        self.rect.center = center
        self.direction = 1
        self.movement_remainder = 0.0
        self.shot_timer = 0.0
        self.hits_remaining = VULCANO_HITS_TO_DEFEAT

    def update(
        self,
        delta_time: float,
        screen_width: int,
        player_center: tuple[int, int],
    ) -> EnemyProjectile | None:
        next_left = self.rect.left + self.direction * VULCANO_SPEED * delta_time
        next_right = self.rect.right + self.direction * VULCANO_SPEED * delta_time
        if next_left < 0 or next_right > screen_width:
            self.direction *= -1
            self.movement_remainder = 0.0
        else:
            self.movement_remainder += self.direction * VULCANO_SPEED * delta_time
            movement = int(self.movement_remainder)
            self.movement_remainder -= movement
            self.rect.x += movement

        self.shot_timer += delta_time
        if self.shot_timer < VULCANO_SHOT_INTERVAL:
            return None

        self.shot_timer -= VULCANO_SHOT_INTERVAL
        origin = self.rect.midbottom
        direction = (
            player_center[0] - origin[0],
            player_center[1] - origin[1],
        )
        return EnemyProjectile(
            origin,
            VULCANO_PROJECTILE_SPEED,
            direction,
        )

    def take_hit(self) -> bool:
        self.hits_remaining -= 1
        return self.hits_remaining <= 0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        x, y = self.rect.center
        draw_antialiased_ellipse(
            surface,
            (75, 35, 108),
            (self.rect.left + 3, self.rect.top + 5, self.rect.width - 6, self.rect.height - 4),
        )
        draw_antialiased_ellipse(
            surface,
            VULCANO_COLOR,
            (self.rect.left, self.rect.top, self.rect.width, self.rect.height - 5),
        )
        draw_antialiased_ellipse(
            surface,
            (226, 130, 241),
            (x - 22, y - 18, 44, 21),
        )
        draw_antialiased_polygon(
            surface,
            (245, 220, 255),
            [
                (x - 22, y - 4),
                (x - 17, y - 12),
                (x - 12, y - 4),
            ],
        )
        draw_antialiased_polygon(
            surface,
            (245, 220, 255),
            [
                (x + 12, y - 4),
                (x + 17, y - 12),
                (x + 22, y - 4),
            ],
        )
        draw_antialiased_circle(surface, (255, 246, 202), (x, y + 8), 3)
        pygame.draw.arc(
            surface,
            (249, 183, 255),
            (x - 27, y - 15, 54, 29),
            0.1,
            3.0,
            2,
        )
        label = font.render(
            f"VULCANO {self.hits_remaining}/{VULCANO_HITS_TO_DEFEAT}",
            True,
            (255, 255, 255),
        )
        surface.blit(label, label.get_rect(midbottom=(self.rect.centerx, self.rect.top - 5)))
