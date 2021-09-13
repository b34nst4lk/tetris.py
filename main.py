import pygame

from src.tetriminos import (
    Game, NextTetrimino,
    TetriminoQueue,
    game_over,
)

from src.settings import (
    WIDTH,
    HEIGHT,
)

from src.utils import asset_resource_path


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 500, HEIGHT + 200))

    # drop_sound = pygame.mixer.Sound(asset_resource_path("drop.wav"))
    # pygame.mixer.music.load(asset_resource_path("bgm.wav"))
    # pygame.mixer.music.play(-1)
    running = True

    shape_generator = TetriminoQueue()

    next_tetrimino = NextTetrimino(screen, (600, 100))
    game = Game(screen, (100, 100), shape_generator)

    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    while running:
        screen.fill((0,0,0))
        events = pygame.event.get()

        next_tetrimino.set_tetrimino(*shape_generator.peek())

        active_tetrimino = game.get_tetrimino()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_ESCAPE, ord("q")}:
                    running = False
                if event.key == pygame.K_LEFT:
                    game.move_left()
                if event.key == pygame.K_RIGHT:
                    game.move_right()
                if event.key == pygame.K_DOWN:
                    game.move_down()
                if event.key == pygame.K_SPACE:
                    game.move_down_and_lock()
                    # drop_sound.play()
                if event.key == pygame.K_UP:
                    game.rotate()

        if pygame.time.get_ticks() - start_time > 300:
            game.move_down()
            start_time = pygame.time.get_ticks()

        if active_tetrimino.locked:
            game.clear_lines()

        screen.fill((0,0,0))
        game.render()
        next_tetrimino.render()
        pygame.display.flip()
        # break

        if game.is_game_over():
            game_over()
            running = False

        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
