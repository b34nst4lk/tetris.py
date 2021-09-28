from math import sqrt
from typing import Union, Tuple, List

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
