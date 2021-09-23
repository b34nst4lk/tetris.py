import os
import sys

import pygame

def asset_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # type: ignore
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, "src", "assets", relative_path)

def draw_outline(screen: pygame.display, rect: pygame.rect.Rect):
    coords = [
        (rect.x + 1 , rect.y + 1), # top left
        (rect.x + rect.width - 1, rect.y + 1), # top right
        (rect.x + 1, rect.y + rect.height - 1), # bottom left
        (rect.x + rect.width - 1, rect.y + rect.height - 1), # bottom right
    ] 

    for i in range(len(coords)):
        for j in range(i, len(coords)):
            pygame.draw.line(screen, (255,255,255), coords[i], coords[j])
