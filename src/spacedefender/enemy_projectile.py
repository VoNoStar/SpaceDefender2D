import pygame

from spacedefender.graphics import draw_antialiased_rounded_rect


ENEMY_PROJECTILE_COLOR = (255, 170, 70)
ENEMY_PROJECTILE_SPEED = 180
VULCANO_PROJECTILE_SPEED = 300


class EnemyProjectile:
    def __init__(
        self,
        center: tuple[int, int],
        speed: float = ENEMY_PROJECTILE_SPEED,
        direction: tuple[float, float] = (0, 1),
    ) -> None:
        self.x, self.y = center
        self.speed = speed
        self.direction = pygame.Vector2(direction)
        if self.direction.length_squared() == 0:
            self.direction = pygame.Vector2(0, 1)
        else:
            self.direction.normalize_ip()
        self.rect = pygame.Rect(self.x - 3, self.y, 6, 12)

    def update(self, delta_time: float) -> None:
        self.x += self.direction.x * self.speed * delta_time
        self.y += self.direction.y * self.speed * delta_time
        self.rect.center = (round(self.x), round(self.y))

    def draw(self, surface: pygame.Surface) -> None:
        draw_antialiased_rounded_rect(
            surface, ENEMY_PROJECTILE_COLOR, self.rect, radius=3
        )
