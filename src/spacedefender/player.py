import pygame

from spacedefender.graphics import (
    draw_antialiased_ellipse,
    draw_antialiased_polygon,
    draw_antialiased_ring,
    draw_antialiased_rounded_rect,
)
from spacedefender.projectile import LaserProjectile, Missile, Projectile
from spacedefender.power_up import PowerUpType


RED = (220, 45, 55)
BLUE = (55, 145, 245)
WHITE = (235, 240, 255)
SHOT_COOLDOWN = 0.25
STARTING_LIVES = 3
RESPAWN_INVULNERABILITY = 1.5
SHIELD_DURATION = 10.0
ENERGY_SPEED_BONUS = 30
MAX_SPEED = 450
MAX_WEAPON_LEVEL = 3
TRANSFORM_SPEED_BONUS = 30
STARTING_TURRETS = 4
MISSILE_EVERY_NORMAL_SHOTS = 5
LASER_COOLDOWN = 0.5


class Player:
    def __init__(self, center: tuple[int, int]) -> None:
        self.spawn_center = center
        self.x, self.y = center
        self.speed = 300
        self.weapon_level = 1
        self.transformed = False
        self.turret_count = 1
        self.missiles_enabled = False
        self.normal_shots_fired = 0
        self.shot_cooldown = 0.0
        self.laser_cooldown = 0.0
        self.lives = STARTING_LIVES
        self.invulnerability_timer = 0.0
        self.shield_timer = 0.0
        self.receive_capsule()

    @property
    def center(self) -> tuple[int, int]:
        return round(self.x), round(self.y)

    @property
    def collision_rect(self) -> pygame.Rect:
        x, y = self.center
        if self.transformed:
            return pygame.Rect(x - 45, y - 47, 90, 90)
        return pygame.Rect(x - 35, y - 38, 70, 67)

    @property
    def is_invulnerable(self) -> bool:
        return self.invulnerability_timer > 0

    def take_hit(self) -> bool:
        if self.is_invulnerable or self.shield_timer > 0 or self.lives <= 0:
            return self.lives > 0

        self.lives -= 1
        if self.lives == 0:
            return False

        self.x, self.y = self.spawn_center
        self.shot_cooldown = 0.0
        self.invulnerability_timer = RESPAWN_INVULNERABILITY
        return True

    def apply_power_up(self, kind: PowerUpType) -> None:
        if kind is PowerUpType.ENERGY:
            self.weapon_level = min(self.weapon_level + 1, MAX_WEAPON_LEVEL)
            self.speed = min(self.speed + ENERGY_SPEED_BONUS, MAX_SPEED)
        elif kind is PowerUpType.SHIELD:
            self.shield_timer = SHIELD_DURATION
        elif kind is PowerUpType.LIFE:
            self.lives += 1

    def restore_life(self) -> None:
        self.lives = min(self.lives + 1, STARTING_LIVES)

    def gain_lives(self, amount: int) -> None:
        self.lives += amount

    def receive_capsule(self) -> None:
        self.turret_count = STARTING_TURRETS
        self.missiles_enabled = True

    def transform(self) -> None:
        if self.transformed:
            return

        self.transformed = True
        self.speed = min(self.speed + TRANSFORM_SPEED_BONUS, MAX_SPEED)

    def update(
        self,
        delta_time: float,
        keys: pygame.key.ScancodeWrapper,
        screen_size: tuple[int, int],
    ) -> None:
        self.shot_cooldown = max(0.0, self.shot_cooldown - delta_time)
        self.laser_cooldown = max(0.0, self.laser_cooldown - delta_time)
        self.invulnerability_timer = max(
            0.0, self.invulnerability_timer - delta_time
        )
        self.shield_timer = max(0.0, self.shield_timer - delta_time)
        horizontal = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
            keys[pygame.K_LEFT] or keys[pygame.K_a]
        )
        vertical = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(
            keys[pygame.K_UP] or keys[pygame.K_w]
        )
        direction = pygame.Vector2(horizontal, vertical)
        if direction.length_squared() > 0:
            direction.normalize_ip()
            self.x += direction.x * self.speed * delta_time
            self.y += direction.y * self.speed * delta_time

        horizontal_margin = 45 if self.transformed else 35
        top_margin = 47 if self.transformed else 38
        bottom_margin = 43 if self.transformed else 29
        self.x = max(
            horizontal_margin,
            min(self.x, screen_size[0] - horizontal_margin),
        )
        self.y = max(top_margin, min(self.y, screen_size[1] - bottom_margin))

    def shoot(self, laser: bool = False) -> list[Projectile] | None:
        if laser:
            if self.laser_cooldown > 0:
                return None

            self.laser_cooldown = LASER_COOLDOWN
            return [LaserProjectile((self.center[0], self.center[1] - 47))]

        if self.shot_cooldown > 0:
            return None

        self.shot_cooldown = SHOT_COOLDOWN
        self.normal_shots_fired += 1
        x, y = self.center[0], self.center[1] - 38
        turret_offsets = (-30, -10, 10, 30)[: self.turret_count]
        projectiles = [
            Projectile(
                (x + offset, y - (8 if abs(offset) > 20 else 0)),
                (offset * 0.004, -1),
            )
            for offset in turret_offsets
        ]
        if self.weapon_level >= 2:
            projectiles.extend(
                Projectile((x + offset, y), (0, -1))
                for offset in (-8, 8)
            )
        if self.weapon_level >= 3:
            projectiles.append(Projectile((x, y), (0, -1)))
        if self.transformed:
            projectiles.extend(
                Projectile((x + offset, y - 8), (offset * 0.004, -1))
                for offset in (-42, 42)
            )

        if (
            self.missiles_enabled
            and self.normal_shots_fired % MISSILE_EVERY_NORMAL_SHOTS == 0
        ):
            projectiles.extend(
                Missile((x + offset, y - 6), (offset * 0.008, -1))
                for offset in (-30, 30)
            )
        return projectiles

    def draw(self, surface: pygame.Surface) -> None:
        x, y = self.center
        if self.transformed:
            red_hull = [
                (x, y - 47), (x + 15, y - 15), (x + 34, y + 15),
                (x + 31, y + 34), (x + 13, y + 29), (x + 7, y + 43),
                (x, y + 37), (x - 7, y + 43), (x - 13, y + 29),
                (x - 31, y + 34), (x - 34, y + 15), (x - 15, y - 15),
            ]
            blue_wings = [
                (x, y - 35), (x + 11, y - 9), (x + 29, y + 20),
                (x + 17, y + 17), (x + 9, y + 33), (x, y + 25),
                (x - 9, y + 33), (x - 17, y + 17), (x - 29, y + 20),
                (x - 11, y - 9),
            ]
            white_fuselage = [
                (x, y - 42), (x + 8, y - 10), (x + 6, y + 27),
                (x, y + 38), (x - 6, y + 27), (x - 8, y - 10),
            ]
        else:
            red_hull = [
                (x, y - 38),
                (x + 13, y - 12),
                (x + 31, y + 10),
                (x + 30, y + 25),
                (x + 13, y + 18),
                (x + 7, y + 29),
                (x, y + 23),
                (x - 7, y + 29),
                (x - 13, y + 18),
                (x - 30, y + 25),
                (x - 31, y + 10),
                (x - 13, y - 12),
            ]
            blue_wings = [
                (x, y - 27),
                (x + 9, y - 7),
                (x + 24, y + 12),
                (x + 13, y + 9),
                (x + 7, y + 20),
                (x, y + 15),
                (x - 7, y + 20),
                (x - 13, y + 9),
                (x - 24, y + 12),
                (x - 9, y - 7),
            ]
            white_fuselage = [
                (x, y - 32),
                (x + 7, y - 7),
                (x + 5, y + 17),
                (x, y + 25),
                (x - 5, y + 17),
                (x - 7, y - 7),
            ]

        draw_antialiased_polygon(surface, RED, red_hull)
        draw_antialiased_polygon(surface, BLUE, blue_wings)
        draw_antialiased_polygon(surface, WHITE, white_fuselage)
        draw_antialiased_ellipse(surface, BLUE, (x - 3, y - 14, 6, 12))
        if self.turret_count:
            turret_offsets = (-30, -10, 10, 30)[: self.turret_count]
            for cannon_x in (x + offset for offset in turret_offsets):
                draw_antialiased_rounded_rect(
                    surface, RED, (cannon_x - 3, y - 8, 6, 17), radius=3
                )
                draw_antialiased_rounded_rect(
                    surface, WHITE, (cannon_x - 2, y - 13, 4, 7), radius=2
                )
        if self.transformed:
            for cannon_x in (x - 42, x + 42):
                draw_antialiased_rounded_rect(
                    surface, RED, (cannon_x - 3, y + 7, 6, 18), radius=3
                )
        if self.shield_timer > 0:
            radius = 52 if self.transformed else 43
            draw_antialiased_ring(surface, (90, 210, 255), (x, y), radius, 3)
            draw_antialiased_ring(surface, (165, 240, 255), (x, y), radius - 4)
