import random

import pygame

from spacedefender.graphics import (
    draw_antialiased_circle,
    draw_antialiased_polygon,
)


SPACE_COLOR = (7, 9, 25)
STAR_COLORS = ((95, 112, 160), (135, 153, 195), (185, 198, 225))


class SpaceBackground:
    def __init__(self, size: tuple[int, int], seed: int = 23) -> None:
        self.surface = pygame.Surface(size)
        self.surface.fill(SPACE_COLOR)
        rng = random.Random(seed)

        for _ in range(size[0] * size[1] // 4200):
            position = (rng.randrange(size[0]), rng.randrange(size[1]))
            radius = rng.choices((1, 2), weights=(9, 1), k=1)[0]
            color = rng.choice(STAR_COLORS)
            draw_antialiased_circle(self.surface, color, position, radius)

        self._draw_planet((135, 355), 27, (39, 51, 82), (70, 84, 119))
        self._draw_ringed_planet((680, 205), 21, (73, 57, 82), (109, 84, 116))

    def _draw_planet(
        self,
        center: tuple[int, int],
        radius: int,
        color: tuple[int, int, int],
        highlight: tuple[int, int, int],
    ) -> None:
        x, y = center
        draw_antialiased_circle(
            self.surface, (17, 22, 43), (x + 3, y + 4), radius + 2
        )
        draw_antialiased_circle(self.surface, color, center, radius)
        pygame.draw.arc(
            self.surface,
            highlight,
            (x - radius + 7, y - radius + 5, radius * 2 - 10, radius * 2 - 10),
            0.6,
            4.4,
            4,
        )
        draw_antialiased_circle(
            self.surface,
            (29, 38, 63),
            (x + radius // 3, y + radius // 3),
            radius // 3,
        )
        draw_antialiased_circle(
            self.surface,
            (32, 42, 69),
            (x - radius // 3, y - radius // 4),
            radius // 5,
        )

    def _draw_ringed_planet(
        self,
        center: tuple[int, int],
        radius: int,
        color: tuple[int, int, int],
        highlight: tuple[int, int, int],
    ) -> None:
        x, y = center
        ring_rect = pygame.Rect(x - radius - 12, y - 7, (radius + 12) * 2, 16)
        pygame.draw.ellipse(self.surface, (49, 41, 65), ring_rect, width=3)
        draw_antialiased_circle(self.surface, color, center, radius)
        pygame.draw.arc(
            self.surface,
            highlight,
            (x - radius + 5, y - radius + 5, (radius - 5) * 2, (radius - 5) * 2),
            0.7,
            4.5,
            4,
        )
        pygame.draw.ellipse(self.surface, (92, 72, 99), ring_rect, width=1)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, (0, 0))


class OceanBackground:
    def __init__(self, size: tuple[int, int]) -> None:
        width, height = size
        self.surface = pygame.Surface(size)
        horizon = int(height * 0.38)
        sky_colors = ((94, 103, 158), (232, 139, 111))
        sea_colors = ((55, 91, 126), (13, 43, 76))
        self._draw_gradient(0, horizon, *sky_colors)
        self._draw_gradient(horizon, height, *sea_colors)

        sun_center = (int(width * 0.72), horizon + 4)
        draw_antialiased_circle(self.surface, (255, 202, 139), sun_center, 35)
        draw_antialiased_circle(self.surface, (255, 222, 164), sun_center, 25)
        pygame.draw.line(
            self.surface, (252, 195, 153), (0, horizon), (width, horizon), 2
        )

        island_color = (43, 67, 78)
        draw_antialiased_polygon(
            self.surface,
            island_color,
            [
                (0, horizon + 3),
                (0, horizon - 18),
                (width // 12, horizon - 31),
                (width // 7, horizon - 12),
                (width // 4, horizon + 2),
            ],
        )
        draw_antialiased_polygon(
            self.surface,
            (53, 73, 78),
            [
                (width * 3 // 5, horizon + 2),
                (width * 2 // 3, horizon - 17),
                (width * 3 // 4, horizon - 29),
                (width * 5 // 6, horizon - 13),
                (width, horizon - 19),
                (width, horizon + 2),
            ],
        )

        self._draw_boat(width // 3, horizon - 7, 0.55)
        self._draw_boat(width * 5 // 6, horizon + 43, 0.8)
        for offset, line_width in ((0, 3), (14, 2), (30, 1)):
            y = horizon + 25 + offset
            half_width = 48 - offset
            pygame.draw.line(
                self.surface,
                (199, 144, 129),
                (sun_center[0] - half_width, y),
                (sun_center[0] + half_width, y),
                line_width,
            )

    def _draw_gradient(
        self,
        top: int,
        bottom: int,
        start: tuple[int, int, int],
        end: tuple[int, int, int],
    ) -> None:
        span = max(1, bottom - top)
        for y in range(top, bottom):
            ratio = (y - top) / span
            color = tuple(
                round(first + (last - first) * ratio)
                for first, last in zip(start, end)
            )
            pygame.draw.line(self.surface, color, (0, y), (self.surface.get_width(), y))

    def _draw_boat(self, x: int, y: int, scale: float) -> None:
        hull = [
            (x - round(24 * scale), y),
            (x + round(24 * scale), y),
            (x + round(17 * scale), y + round(7 * scale)),
            (x - round(17 * scale), y + round(7 * scale)),
        ]
        draw_antialiased_polygon(self.surface, (34, 45, 59), hull)
        pygame.draw.rect(
            self.surface,
            (49, 57, 69),
            (
                x - round(8 * scale),
                y - round(7 * scale),
                round(16 * scale),
                round(7 * scale),
            ),
        )
        pygame.draw.line(
            self.surface,
            (38, 48, 63),
            (x, y - round(7 * scale)),
            (x, y - round(16 * scale)),
            max(1, round(2 * scale)),
        )

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, (0, 0))


class CityBackground:
    def __init__(self, size: tuple[int, int]) -> None:
        width, height = size
        self.surface = pygame.Surface(size)
        horizon = int(height * 0.48)
        sky_colors = ((72, 81, 139), (246, 145, 105))
        self._draw_sky(horizon, *sky_colors)

        sun_center = (width * 3 // 4, horizon + 4)
        draw_antialiased_circle(self.surface, (255, 191, 131), sun_center, 31)
        draw_antialiased_circle(self.surface, (255, 218, 164), sun_center, 21)

        pygame.draw.rect(
            self.surface,
            (74, 81, 107),
            (0, horizon - 34, width, height - horizon + 34),
        )
        self._draw_skyline(width, horizon)
        self._draw_road(width, height)
        pygame.draw.line(
            self.surface, (255, 183, 135), (0, horizon), (width, horizon), 2
        )

    def _draw_sky(
        self,
        horizon: int,
        start: tuple[int, int, int],
        end: tuple[int, int, int],
    ) -> None:
        for y in range(horizon + 1):
            ratio = y / max(1, horizon)
            color = tuple(
                round(first + (last - first) * ratio)
                for first, last in zip(start, end)
            )
            pygame.draw.line(
                self.surface,
                color,
                (0, y),
                (self.surface.get_width(), y),
            )

    def _draw_skyline(self, width: int, horizon: int) -> None:
        far_color = (104, 91, 108)
        near_color = (59, 62, 83)
        far_buildings = [
            (0, 29, 68), (38, 43, 55), (103, 35, 83), (168, 50, 61),
            (240, 37, 75), (301, 48, 58), (370, 33, 80), (432, 50, 64),
            (501, 38, 72), (558, 48, 55), (626, 35, 85), (687, 48, 62),
            (756, 44, 75),
        ]
        for x, building_width, building_height in far_buildings:
            if x >= width:
                continue
            pygame.draw.rect(
                self.surface,
                far_color,
                (x, horizon - building_height, building_width, building_height),
            )

        buildings = [
            (0, 50, 87), (57, 43, 114), (105, 61, 75), (174, 48, 127),
            (228, 60, 94), (296, 45, 120), (347, 65, 81), (420, 53, 136),
            (480, 63, 91), (551, 48, 121), (605, 60, 77), (673, 55, 110),
            (735, 65, 93),
        ]
        for x, building_width, building_height in buildings:
            if x >= width:
                continue
            rect = pygame.Rect(
                x,
                horizon - building_height,
                min(building_width, width - x),
                building_height,
            )
            pygame.draw.rect(self.surface, near_color, rect)
            for window_y in range(rect.top + 10, rect.bottom - 8, 15):
                for window_x in range(rect.left + 8, rect.right - 5, 13):
                    pygame.draw.rect(
                        self.surface,
                        (215, 164, 119),
                        (window_x, window_y, 4, 6),
                    )

    def _draw_road(self, width: int, height: int) -> None:
        road_top = int(height * 0.78)
        pygame.draw.rect(
            self.surface,
            (37, 42, 56),
            (0, road_top, width, height - road_top),
        )
        pygame.draw.line(
            self.surface,
            (195, 159, 131),
            (0, road_top),
            (width, road_top),
            3,
        )
        for x in range(20, width, 105):
            pygame.draw.rect(
                self.surface,
                (220, 187, 145),
                (x, road_top + 45, 48, 4),
            )
        pygame.draw.polygon(
            self.surface,
            (51, 57, 73),
            [
                (0, road_top - 5),
                (width // 3, road_top - 5),
                (width // 2, height),
                (0, height),
            ],
        )
        pygame.draw.polygon(
            self.surface,
            (51, 57, 73),
            [
                (width * 2 // 3, road_top - 5),
                (width, road_top - 5),
                (width, height),
                (width // 2, height),
            ],
        )
        pygame.draw.line(
            self.surface,
            (226, 190, 145),
            (width // 2, road_top + 15),
            (width // 2, height),
            2,
        )

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, (0, 0))
