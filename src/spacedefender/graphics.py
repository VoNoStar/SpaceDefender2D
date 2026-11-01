import pygame
import pygame.gfxdraw


def draw_antialiased_polygon(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    points: list[tuple[int, int]],
) -> None:
    pygame.gfxdraw.filled_polygon(surface, points, color)
    pygame.gfxdraw.aapolygon(surface, points, color)


def draw_antialiased_circle(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    center: tuple[int, int],
    radius: int,
) -> None:
    pygame.gfxdraw.filled_circle(surface, *center, radius, color)
    pygame.gfxdraw.aacircle(surface, *center, radius, color)


def draw_antialiased_ellipse(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    rect: pygame.Rect | tuple[int, int, int, int],
) -> None:
    bounds = pygame.Rect(rect)
    if bounds.width <= 0 or bounds.height <= 0:
        return
    pygame.gfxdraw.filled_ellipse(
        surface,
        bounds.centerx,
        bounds.centery,
        max(1, bounds.width // 2),
        max(1, bounds.height // 2),
        color,
    )
    pygame.gfxdraw.aaellipse(
        surface,
        bounds.centerx,
        bounds.centery,
        max(1, bounds.width // 2),
        max(1, bounds.height // 2),
        color,
    )


def draw_antialiased_ring(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    center: tuple[int, int],
    radius: int,
    width: int = 1,
) -> None:
    pygame.draw.circle(surface, color, center, radius, width=width)
    pygame.gfxdraw.aacircle(surface, *center, radius, color)


def draw_antialiased_rounded_rect(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    rect: pygame.Rect | tuple[int, int, int, int],
    radius: int,
) -> None:
    bounds = pygame.Rect(rect)
    radius = min(radius, bounds.width // 2, bounds.height // 2)
    if radius <= 0:
        pygame.draw.rect(surface, color, bounds)
        return

    pygame.draw.rect(
        surface,
        color,
        (bounds.left + radius, bounds.top, bounds.width - radius * 2, bounds.height),
    )
    pygame.draw.rect(
        surface,
        color,
        (bounds.left, bounds.top + radius, bounds.width, bounds.height - radius * 2),
    )
    for center in (
        (bounds.left + radius, bounds.top + radius),
        (bounds.right - radius - 1, bounds.top + radius),
        (bounds.left + radius, bounds.bottom - radius - 1),
        (bounds.right - radius - 1, bounds.bottom - radius - 1),
    ):
        draw_antialiased_circle(surface, color, center, radius)
