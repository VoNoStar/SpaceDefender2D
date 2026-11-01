import pygame

from spacedefender.enemy import Enemy, EnemyFormation
from spacedefender.enemy_projectile import EnemyProjectile
from spacedefender.mothership import Mothership
from spacedefender.vulcano import Vulcano


TROJAN_WAVE_COUNT = 3
TROJANS_PER_WAVE = 5
VULCANO_CENTER_Y = 90


def create_trojan_wave(screen_width: int, rows: int = 1) -> list[Enemy]:
    return [
        Enemy(
            (
                screen_width * column // (TROJANS_PER_WAVE + 1),
                75 + row * 50,
            )
        )
        for row in range(rows)
        for column in range(1, TROJANS_PER_WAVE + 1)
    ]


class Level:
    number = 1
    wave_count = TROJAN_WAVE_COUNT
    trojan_rows = 1
    vulcano_count = 1
    vulcano_wave_count = 1
    has_mothership = False

    def __init__(self, screen_width: int) -> None:
        self.screen_width = screen_width
        self.wave_number = 1
        self.waves_cleared = 0
        self.vulcano_waves_cleared = 0
        self.enemies = create_trojan_wave(screen_width, self.trojan_rows)
        self.formation = EnemyFormation(self.enemies)
        self.vulcanos: list[Vulcano] = []
        self.mothership: Mothership | None = None
        self.complete = False
        self.font = pygame.font.Font(None, 22)

    @property
    def vulcano(self) -> Vulcano | None:
        return self.vulcanos[0] if self.vulcanos else None

    def update(
        self,
        delta_time: float,
        player_center: tuple[int, int] = (400, 500),
    ) -> list[EnemyProjectile]:
        if self.complete:
            return []

        shots: list[EnemyProjectile] = []
        trojan_shot = self.formation.update(delta_time, self.screen_width)
        if trojan_shot is not None:
            shots.append(trojan_shot)

        for vulcano in self.vulcanos:
            vulcano_shot = vulcano.update(delta_time, self.screen_width, player_center)
            if vulcano_shot is not None:
                shots.append(vulcano_shot)

        if self.mothership is not None:
            mothership_shot = self.mothership.update(
                delta_time, self.screen_width, player_center
            )
            if mothership_shot is not None:
                shots.append(mothership_shot)

        return shots

    def clear_wave(self) -> None:
        if self.enemies:
            return

        self.waves_cleared += 1
        if self.waves_cleared < self.wave_count:
            self.wave_number += 1
            self.enemies = create_trojan_wave(self.screen_width, self.trojan_rows)
            self.formation = EnemyFormation(self.enemies)
        else:
            self._spawn_vulcano_wave()

    def _spawn_vulcano_wave(self) -> None:
        spacing = self.screen_width // (self.vulcano_count + 1)
        self.vulcanos = [
            Vulcano((spacing * (index + 1), VULCANO_CENTER_Y))
            for index in range(self.vulcano_count)
        ]

    def damage_vulcano(self, target: Vulcano | None = None) -> bool:
        if target is None:
            target = self.vulcano
        if target is None or target not in self.vulcanos:
            return False

        defeated = target.take_hit()
        if defeated:
            self.vulcanos.remove(target)
            if not self.vulcanos:
                self.vulcano_waves_cleared += 1
                if self.vulcano_waves_cleared < self.vulcano_wave_count:
                    self._spawn_vulcano_wave()
                elif self.has_mothership:
                    self.mothership = Mothership(
                        (self.screen_width // 2, VULCANO_CENTER_Y)
                    )
                else:
                    self.complete = True
        return defeated

    def damage_mothership(self, damage: int = 1) -> bool:
        if self.mothership is None:
            return False

        defeated = self.mothership.take_hit(damage)
        if defeated:
            self.mothership = None
            self.complete = True
        return defeated

    def draw_hud(self, surface: pygame.Surface) -> None:
        level_text = self.font.render(f"NIVEL: {self.number}", True, (235, 240, 255))
        surface.blit(level_text, (16, 94))
        if self.waves_cleared < self.wave_count:
            wave_label = f"TROYANOS: {self.waves_cleared + 1}/{self.wave_count}"
        elif self.vulcano_waves_cleared < self.vulcano_wave_count:
            wave_label = (
                f"VULCANOS: {self.vulcano_waves_cleared + 1}/"
                f"{self.vulcano_wave_count}"
            )
        else:
            wave_label = "MEDUSA"
        wave_text = self.font.render(wave_label, True, (235, 240, 255))
        surface.blit(wave_text, (16, 116))

class LevelOne(Level):
    pass


class LevelTwo(Level):
    number = 2
    trojan_rows = 2
    vulcano_count = 2


class LevelThree(Level):
    number = 3
    wave_count = 5
    trojan_rows = 2
    vulcano_count = 1
    vulcano_wave_count = 2
    has_mothership = True
