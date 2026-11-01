import pygame

from spacedefender.audio import AudioManager
from spacedefender.background import CityBackground, OceanBackground, SpaceBackground
from spacedefender.enemy_projectile import EnemyProjectile
from spacedefender.level import LevelOne, LevelThree, LevelTwo
from spacedefender.player import Player
from spacedefender.power_up import PowerUp, PowerUpSpawner
from spacedefender.projectile import Projectile


WINDOW_SIZE = (800, 600)
WINDOW_TITLE = "Space Defender 2D"
FPS = 60
LEVEL_WIN_DISPLAY_SECONDS = 2.5


def main() -> None:
    pygame.init()
    audio = AudioManager()
    audio.play_battle_music()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(WINDOW_TITLE)
    background = SpaceBackground(WINDOW_SIZE)
    ocean_background = OceanBackground(WINDOW_SIZE)
    city_background = CityBackground(WINDOW_SIZE)
    clock = pygame.time.Clock()
    player = Player((WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] - 95))
    level = LevelOne(WINDOW_SIZE[0])
    projectiles: list[Projectile] = []
    enemy_projectiles: list[EnemyProjectile] = []
    power_ups: list[PowerUp] = []
    power_up_spawner = PowerUpSpawner()
    game_over = False
    level_one_win_timer: float | None = None
    level_two_win_timer: float | None = None
    final_cue_started = False
    message_font = pygame.font.Font(None, 80)
    boss_font = pygame.font.Font(None, 22)
    hud_font = pygame.font.Font(None, 28)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        delta_time = clock.tick(FPS) / 1000
        if level_one_win_timer is not None:
            level_one_win_timer = max(0.0, level_one_win_timer - delta_time)
            if level_one_win_timer == 0:
                level = LevelTwo(WINDOW_SIZE[0])
                background = ocean_background
                projectiles.clear()
                enemy_projectiles.clear()
                level_one_win_timer = None
                audio.play_battle_music()
        if level_two_win_timer is not None:
            level_two_win_timer = max(0.0, level_two_win_timer - delta_time)
            if level_two_win_timer == 0:
                level = LevelThree(WINDOW_SIZE[0])
                background = city_background
                projectiles.clear()
                enemy_projectiles.clear()
                level_two_win_timer = None
                audio.play_battle_music()

        if not game_over and not level.complete:
            keys = pygame.key.get_pressed()
            player.update(delta_time, keys, WINDOW_SIZE)
            if keys[pygame.K_SPACE]:
                laser = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                shots = player.shoot(laser=laser)
                if shots is not None:
                    projectiles.extend(shots)
                    audio.play_shot(laser=laser)

            power_up = power_up_spawner.update(delta_time, WINDOW_SIZE[0])
            if power_up is not None:
                power_ups.append(power_up)
            for power_up in power_ups:
                power_up.update(delta_time)
            collected_power_ups = {
                index
                for index, power_up in enumerate(power_ups)
                if power_up.rect.colliderect(player.collision_rect)
            }
            for index in collected_power_ups:
                player.apply_power_up(power_ups[index].kind)
            power_ups = [
                power_up
                for index, power_up in enumerate(power_ups)
                if index not in collected_power_ups and power_up.rect.top < WINDOW_SIZE[1]
            ]

            enemy_projectiles.extend(level.update(delta_time, player.center))

            for projectile in projectiles:
                projectile.update(delta_time)
            projectiles = [
                projectile
                for projectile in projectiles
                if projectile.rect.bottom > 0
            ]
            for projectile in enemy_projectiles:
                projectile.update(delta_time)
            enemy_projectiles = [
                projectile
                for projectile in enemy_projectiles
                if projectile.rect.top < WINDOW_SIZE[1]
            ]

            hit_enemies = set()
            hit_projectiles = set()
            for projectile_index, projectile in enumerate(projectiles):
                hit_vulcano = False
                for vulcano in level.vulcanos:
                    if projectile.rect.colliderect(vulcano.rect):
                        hit_projectiles.add(projectile_index)
                        level.damage_vulcano(vulcano)
                        hit_vulcano = True
                        break
                if hit_vulcano:
                    continue
                if (
                    level.mothership is not None
                    and projectile.rect.colliderect(level.mothership.rect)
                ):
                    hit_projectiles.add(projectile_index)
                    level.damage_mothership(projectile.damage)
                    continue
                for enemy_index, enemy in enumerate(level.enemies):
                    if (
                        enemy_index not in hit_enemies
                        and projectile.rect.colliderect(enemy.rect)
                    ):
                        hit_enemies.add(enemy_index)
                        hit_projectiles.add(projectile_index)
                        break
            if hit_enemies:
                level.enemies = [
                    enemy
                    for enemy_index, enemy in enumerate(level.enemies)
                    if enemy_index not in hit_enemies
                ]
                level.formation.enemies = level.enemies
                if (
                    not level.enemies
                    and level.waves_cleared < level.wave_count
                ):
                    level.clear_wave()
            if hit_projectiles:
                projectiles = [
                    projectile
                    for index, projectile in enumerate(projectiles)
                    if index not in hit_projectiles
                ]

            if (
                level.complete
                and isinstance(level, LevelOne)
                and level_one_win_timer is None
            ):
                player.transform()
                player.restore_life()
                level_one_win_timer = LEVEL_WIN_DISPLAY_SECONDS
                projectiles.clear()
                enemy_projectiles.clear()
                audio.play_level_clear()
            elif (
                level.complete
                and isinstance(level, LevelTwo)
                and level_two_win_timer is None
            ):
                player.gain_lives(3)
                level_two_win_timer = LEVEL_WIN_DISPLAY_SECONDS
                projectiles.clear()
                enemy_projectiles.clear()
                audio.play_level_clear()
            elif (
                level.complete
                and isinstance(level, LevelThree)
                and not final_cue_started
            ):
                final_cue_started = True
                audio.play_finale()

            enemy_reached_player = any(
                enemy.rect.bottom >= player.collision_rect.top
                for enemy in level.enemies
            )
            if enemy_reached_player:
                game_over = True
            else:
                hit_enemy_projectiles = {
                    index
                    for index, projectile in enumerate(enemy_projectiles)
                    if projectile.rect.colliderect(player.collision_rect)
                }
                if hit_enemy_projectiles:
                    enemy_projectiles = [
                        projectile
                        for index, projectile in enumerate(enemy_projectiles)
                        if index not in hit_enemy_projectiles
                    ]
                    game_over = not player.take_hit()

        background.draw(screen)
        lives_text = hud_font.render(
            f"HÉRCULES - NAVES: {player.lives}", True, (235, 240, 255)
        )
        screen.blit(lives_text, (16, 14))
        upgrades_text = hud_font.render(
            f"ARMAS: {player.weapon_level}  TORRETAS: {player.turret_count}",
            True,
            (235, 240, 255),
        )
        screen.blit(upgrades_text, (16, 40))
        missile_progress = player.normal_shots_fired % 5
        shots_to_missile = 5 if missile_progress == 0 else 5 - missile_progress
        weapons_text = hud_font.render(
            f"MISIL: {shots_to_missile}/5  VELOCIDAD: {player.speed}",
            True,
            (235, 240, 255),
        )
        screen.blit(weapons_text, (16, 66))
        level.draw_hud(screen)
        if player.shield_timer > 0:
            shield_text = hud_font.render(
                f"ESCUDO: {player.shield_timer:.1f}s", True, (90, 210, 255)
            )
            screen.blit(shield_text, (16, 90))
        for enemy in level.enemies:
            enemy.draw(screen)
        for vulcano in level.vulcanos:
            vulcano.draw(screen, boss_font)
        if level.mothership is not None:
            level.mothership.draw(screen, boss_font)
        for power_up in power_ups:
            power_up.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)
        for projectile in enemy_projectiles:
            projectile.draw(screen)
        if not player.is_invulnerable or int(player.invulnerability_timer * 10) % 2:
            player.draw(screen)
        if game_over:
            game_over_text = message_font.render("GAME OVER", True, (255, 75, 75))
            screen.blit(
                game_over_text,
                game_over_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)),
            )
        elif level_one_win_timer is not None:
            complete_text = message_font.render(
                "YOU WIN LEVEL 1!", True, (100, 240, 150)
            )
            screen.blit(
                complete_text,
                complete_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)),
            )
        elif level_two_win_timer is not None:
            complete_text = message_font.render(
                "YOU WIN! NEXT LEVEL!", True, (100, 240, 150)
            )
            screen.blit(
                complete_text,
                complete_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)),
            )
        elif level.complete:
            complete_text = message_font.render(
                "YOU WIN THE GAME!", True, (100, 240, 150)
            )
            screen.blit(
                complete_text,
                complete_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)),
            )
        pygame.display.flip()

    audio.shutdown()
    pygame.quit()


if __name__ == "__main__":
    main()
