import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from spacedefender.background import CityBackground, OceanBackground
from spacedefender.enemy import Enemy
from spacedefender.enemy_projectile import (
    ENEMY_PROJECTILE_SPEED,
    VULCANO_PROJECTILE_SPEED,
)
from spacedefender.level import (
    TROJAN_WAVE_COUNT,
    TROJANS_PER_WAVE,
    LevelOne,
    LevelThree,
    LevelTwo,
)
from spacedefender.mothership import (
    Mothership,
    MOTHERSHIP_HITS_TO_DEFEAT,
    MOTHERSHIP_PROJECTILE_SPEED,
)
from spacedefender.player import Player
from spacedefender.power_up import PowerUp, PowerUpType
from spacedefender.projectile import LaserProjectile, Missile
from spacedefender.vulcano import VULCANO_HITS_TO_DEFEAT, Vulcano


class LevelOneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_three_waves_each_contain_five_trojans(self) -> None:
        level = LevelOne(800)
        self.assertEqual(len(level.enemies), TROJANS_PER_WAVE)

        for wave_number in range(1, TROJAN_WAVE_COUNT + 1):
            level.enemies.clear()
            level.clear_wave()
            self.assertEqual(level.waves_cleared, wave_number)
            if wave_number < TROJAN_WAVE_COUNT:
                self.assertEqual(len(level.enemies), TROJANS_PER_WAVE)

        self.assertFalse(level.enemies)

    def test_vulcano_spawns_after_three_waves_and_takes_ten_hits(self) -> None:
        level = LevelOne(800)
        self.assertIsNone(level.vulcano)

        for _ in range(TROJAN_WAVE_COUNT):
            level.enemies.clear()
            level.clear_wave()

        self.assertIsNotNone(level.vulcano)
        self.assertGreater(VULCANO_PROJECTILE_SPEED, ENEMY_PROJECTILE_SPEED)

        for _ in range(10):
            shot = level.vulcano.update(0.1, 800, (650, 500))
            if shot is not None:
                break
        self.assertIsNotNone(shot)
        self.assertGreater(shot.direction.x, 0)
        self.assertGreater(shot.direction.y, 0)

        for _ in range(VULCANO_HITS_TO_DEFEAT - 1):
            self.assertFalse(level.damage_vulcano())
        self.assertFalse(level.complete)
        self.assertTrue(level.damage_vulcano())
        self.assertTrue(level.complete)
        self.assertIsNone(level.vulcano)

    def test_level_does_not_complete_until_vulcano_is_defeated(self) -> None:
        level = LevelOne(800)
        for _ in range(TROJAN_WAVE_COUNT):
            level.enemies.clear()
            level.clear_wave()

        self.assertFalse(level.complete)
        level.update(120)
        self.assertFalse(level.complete)

    def test_level_two_has_two_rows_and_two_vulcanos(self) -> None:
        level = LevelTwo(800)
        self.assertEqual(len(level.enemies), TROJANS_PER_WAVE * 2)
        self.assertEqual(
            len({enemy.rect.centery for enemy in level.enemies}),
            2,
        )

        for _ in range(TROJAN_WAVE_COUNT):
            level.enemies.clear()
            level.clear_wave()

        self.assertEqual(len(level.vulcanos), 2)
        for vulcano in tuple(level.vulcanos):
            for _ in range(VULCANO_HITS_TO_DEFEAT):
                level.damage_vulcano(vulcano)
            self.assertNotIn(vulcano, level.vulcanos)

        self.assertTrue(level.complete)

    def test_level_one_completion_transforms_hercules_for_level_two(self) -> None:
        player = Player((400, 505))
        player.take_hit()
        self.assertEqual(player.lives, 2)

        shots_before = player.shoot()
        self.assertEqual(len(shots_before), 4)

        player.transform()
        player.restore_life()
        player.shot_cooldown = 0
        shots_after = player.shoot()
        self.assertTrue(player.transformed)
        self.assertEqual(len(shots_after), 6)
        self.assertEqual(player.speed, 330)
        self.assertEqual(player.lives, 3)
        self.assertEqual(player.collision_rect.size, (90, 90))

    def test_potion_adds_a_life_and_level_transition_bonuses(self) -> None:
        player = Player((400, 505))
        player.take_hit()
        self.assertEqual(player.lives, 2)

        player.restore_life()
        self.assertEqual(player.lives, 3)
        player.restore_life()
        self.assertEqual(player.lives, 3)

        potion = PowerUp((100, 100), PowerUpType.LIFE)
        potion.draw(pygame.Surface((200, 200)))
        player.apply_power_up(potion.kind)
        self.assertEqual(player.lives, 4)

        player.gain_lives(3)
        self.assertEqual(player.lives, 7)

    def test_final_level_has_trojan_waves_vulcanos_and_mothership(self) -> None:
        level = LevelThree(800)
        self.assertEqual(level.wave_count, 5)
        self.assertEqual(len(level.enemies), TROJANS_PER_WAVE * 2)

        for wave_number in range(level.wave_count):
            level.enemies.clear()
            level.clear_wave()
            if wave_number < level.wave_count - 1:
                self.assertEqual(len(level.enemies), TROJANS_PER_WAVE * 2)

        self.assertEqual(len(level.vulcanos), 1)
        first_vulcano = level.vulcanos[0]
        for _ in range(VULCANO_HITS_TO_DEFEAT):
            level.damage_vulcano(first_vulcano)
        self.assertEqual(level.vulcano_waves_cleared, 1)
        self.assertEqual(len(level.vulcanos), 1)

        second_vulcano = level.vulcanos[0]
        for _ in range(VULCANO_HITS_TO_DEFEAT):
            level.damage_vulcano(second_vulcano)
        self.assertEqual(level.vulcano_waves_cleared, 2)
        self.assertIsNotNone(level.mothership)
        self.assertFalse(level.complete)
        mothership = level.mothership
        shot = mothership.update(0.8, 800, (400, 500))
        self.assertIsNotNone(shot)
        self.assertEqual(shot.speed, MOTHERSHIP_PROJECTILE_SPEED)
        mothership.draw(pygame.Surface((800, 600)), pygame.font.Font(None, 22))

        for _ in range(MOTHERSHIP_HITS_TO_DEFEAT - 1):
            self.assertFalse(level.damage_mothership())
        self.assertTrue(level.damage_mothership())
        self.assertIsNone(level.mothership)
        self.assertTrue(level.complete)

    def test_starting_capsule_adds_four_turrets_and_missiles_every_five_shots(self) -> None:
        player = Player((400, 505))
        self.assertEqual(player.turret_count, 4)
        self.assertTrue(player.missiles_enabled)

        shots = []
        for _ in range(5):
            player.shot_cooldown = 0
            shots = player.shoot()

        self.assertEqual(player.normal_shots_fired, 5)
        self.assertEqual(sum(isinstance(shot, Missile) for shot in shots), 2)
        self.assertEqual(
            sum(not isinstance(shot, Missile) for shot in shots),
            4,
        )

    def test_laser_is_separate_and_counts_as_two_mothership_hits(self) -> None:
        player = Player((400, 505))
        normal_shot_count = player.normal_shots_fired
        laser = player.shoot(laser=True)
        self.assertEqual(len(laser), 1)
        self.assertIsInstance(laser[0], LaserProjectile)
        self.assertEqual(laser[0].damage, 2)
        self.assertEqual(player.normal_shots_fired, normal_shot_count)

        level = LevelThree(800)
        for _ in range(level.wave_count):
            level.enemies.clear()
            level.clear_wave()
        for _ in range(level.vulcano_wave_count):
            for _ in range(VULCANO_HITS_TO_DEFEAT):
                level.damage_vulcano(level.vulcanos[0])

        self.assertEqual(
            level.mothership.hits_remaining,
            MOTHERSHIP_HITS_TO_DEFEAT,
        )
        self.assertFalse(level.damage_mothership(laser[0].damage))
        self.assertEqual(level.mothership.hits_remaining, 18)

    def test_ocean_and_city_backgrounds_render_distinct_scenes(self) -> None:
        ocean = OceanBackground((800, 600))
        city = CityBackground((800, 600))
        ocean_surface = pygame.Surface((800, 600))
        city_surface = pygame.Surface((800, 600))
        ocean.draw(ocean_surface)
        city.draw(city_surface)

        self.assertNotEqual(ocean_surface.get_at((400, 300)), city_surface.get_at((400, 300)))
        self.assertNotEqual(ocean_surface.get_at((400, 580)), city_surface.get_at((400, 580)))

    def test_antialiased_game_art_renders(self) -> None:
        surface = pygame.Surface((800, 600))
        font = pygame.font.Font(None, 22)
        player = Player((400, 500))
        player.draw(surface)
        Enemy((200, 100)).draw(surface)
        Vulcano((400, 100)).draw(surface, font)
        Mothership((400, 200)).draw(surface, font)
        PowerUp((300, 300), PowerUpType.LIFE).draw(surface)
        LaserProjectile((400, 400)).draw(surface)

        self.assertNotEqual(surface.get_bounding_rect().size, (0, 0))


if __name__ == "__main__":
    unittest.main()
