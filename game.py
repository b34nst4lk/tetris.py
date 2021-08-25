import logging

import pygame
from pygame.rect import Rect

from src.main import (
    Tetriminos,
    game_over,
)

from src.settings import (
    size,
    base_path,
    width,
    height,
    tile_width,
    tile_height,
)

from utils import resource_path

top_border = Rect(0, 0, width, tile_height)
left_border = Rect(0, 0, tile_width, height)
right_border = Rect(width - tile_width, 0, tile_width, height)
bottom_border = Rect(0, height - tile_height, width, tile_height)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(size)

    background_path = resource_path(f"src/assets/Board.png")
    background = pygame.image.load(background_path)
    background = pygame.transform.scale(background, size)

    running = True
    game = Tetriminos(screen)
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    while running:
        screen.blit(background, (0, 0))

        events = pygame.event.get()
        
        hold_down = False
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_ESCAPE, ord("q")}:
                    running = False
                if event.key in {pygame.K_LEFT}:
                    game.move_left()
                if event.key in {pygame.K_RIGHT}:
                    game.move_right()
                if event.key in {pygame.K_DOWN}:
                    game.move_down()
                if event.key in {pygame.K_UP}:
                    game.move_down_and_lock()
       
        game.render()
        if pygame.time.get_ticks() - start_time > 300:
            game.move_down()
            start_time = pygame.time.get_ticks()

        if game.is_game_over():
            game_over()
            running = False

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
