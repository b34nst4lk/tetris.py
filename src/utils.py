import os
import sys

from math import pi, cos, sqrt
from typing import Tuple, Union, List

import pygame

from src.settings import DEBUG

Number = Union[int, float]
Point = Tuple[Number, Number]


def clamp(val, minimum, maximum):
    return max(min(maximum, val), minimum)


def distance(point_1: Point, point_2: Point) -> float:
    x1, y1 = point_1
    x2, y2 = point_2

    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distances(points: List[Point]) -> List[float]:
    paired_points = zip(points, points[1:] + points[:1])
    return [distance(*pair) for pair in paired_points]


def lerp(x1: Number, x2: Number, w: Number) -> Number:
    return w * x1 + (1 - w) * x2


def lerp2D(p1: Point, p2: Point, w: Number) -> Point:
    x1, y1 = p1
    x2, y2 = p2
    return (lerp(x1, x2, w), lerp(y1, y2, w))


def incomplete_perimeter_points(points: List[Point], weight: float) -> List[Point]:
    all_distances = distances(points)
    total_perimeter = sum(all_distances)

    covered_distance = weight * total_perimeter
    final_points = [points[0]]

    previous_point = points[0]
    for point, distance in zip(points[1:] + points[:1], all_distances):
        covered_distance -= distance
        if covered_distance >= 0:
            final_points.append(point)
            previous_point = point
            continue
        weight = abs(covered_distance / distance)
        final_points.append(lerp2D(previous_point, point, weight))
        break

    return final_points


def ease_in_sine(weight):
    return 1 - cos((weight * pi) / 2)


def asset_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # type: ignore
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, "src", "assets", relative_path)


def draw_scaffold(screen: pygame.display, rect: pygame.rect.Rect):
    if not DEBUG:
        return

    coords = [
        (rect.x + 1, rect.y + 1),  # top left
        (rect.x + rect.width - 1, rect.y + 1),  # top right
        (rect.x + 1, rect.y + rect.height - 1),  # bottom left
        (rect.x + rect.width - 1, rect.y + rect.height - 1),  # bottom right
    ]

    for i in range(len(coords)):
        for j in range(i, len(coords)):
            pygame.draw.line(screen, (255, 255, 255), coords[i], coords[j])


def draw_outline(screen: pygame.display, rect: pygame.rect.Rect):
    top_left = (rect.x + 1, rect.y + 1)
    top_right = (rect.x + rect.width - 1, rect.y + 1)
    bottom_left = (rect.x + 1, rect.y + rect.height - 1)
    bottom_right = (
        (rect.x + rect.width - 1, rect.y + rect.height - 1),
    )  # bottom right

    coords = [
        (top_left, top_right),
        (top_right, bottom_right),
        (bottom_left, bottom_right),
        (top_left, bottom_left),
    ]

    for i, j in coords:
        pygame.draw.line(screen, (255, 255, 255), i, j)


def draw_progressive_line(
    screen: pygame.display, i: Tuple[int, int], j: Tuple[int, int]
):
    weight = 0
    while weight < 100:
        mid_x = (100 - weight) / 100 * i[0] + weight / 100 * j[0]
        mid_y = (100 - weight) / 100 * i[1] + weight / 100 * j[1]
        pygame.draw.line(screen, (255, 255, 255), i, (mid_x, mid_y))
        weight += 1
        yield weight

    while True:
        pygame.draw.line(screen, (255, 255, 255), i, j)
        yield weight
