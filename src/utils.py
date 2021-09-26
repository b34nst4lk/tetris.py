import os
import sys

from typing import Tuple

import pygame

from src.settings import DEBUG

def clamp(val, minimum, maximum):
    return max(min(maximum, val), minimum)

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
        (rect.x + 1 , rect.y + 1), # top left
        (rect.x + rect.width - 1, rect.y + 1), # top right
        (rect.x + 1, rect.y + rect.height - 1), # bottom left
        (rect.x + rect.width - 1, rect.y + rect.height - 1), # bottom right
    ] 

    for i in range(len(coords)):
        for j in range(i, len(coords)):
            pygame.draw.line(screen, (255,255,255), coords[i], coords[j])

def draw_outline(screen: pygame.display, rect: pygame.rect.Rect):
    top_left = (rect.x + 1 , rect.y + 1)
    top_right = (rect.x + rect.width - 1, rect.y + 1)
    bottom_left = (rect.x + 1, rect.y + rect.height - 1)
    bottom_right = (rect.x + rect.width - 1, rect.y + rect.height - 1), # bottom right

    coords = [
        (top_left, top_right),
        (top_right, bottom_right),
        (bottom_left, bottom_right),
        (top_left, bottom_left),
    ]

    for i, j in coords:
        pygame.draw.line(screen, (255,255,255), i, j)

def draw_progressive_line(screen: pygame.display, i: Tuple[int, int], j: Tuple[int, int]):
    weight = 0
    while weight < 100:
        mid_x = (100 - weight)/100 * i[0] + weight/100 * j[0]
        mid_y = (100 - weight)/100 * i[1] + weight/100 * j[1]
        pygame.draw.line(screen, (255,255,255), i, (mid_x, mid_y))
        weight += 1
        yield weight


    while True:
        pygame.draw.line(screen, (255,255,255), i, j)
        yield weight
