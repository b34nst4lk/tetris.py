import pygame

def draw_scaffold(screen: pygame.display, rect: pygame.rect.Rect):
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
