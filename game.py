import pygame

from src.main import (
    Tetriminos,
    game_over,
)

from src.settings import (
    SIZE,
)

from src.utils import asset_resource_path

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(SIZE)

    background_path = asset_resource_path("Board.png")
    background = pygame.image.load(background_path)
    background = pygame.transform.scale(background, SIZE)
    
    drop_sound = pygame.mixer.Sound(asset_resource_path("drop.wav"))
    pygame.mixer.music.load(asset_resource_path("bgm.wav"))
    pygame.mixer.music.play(-1)
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
                    drop_sound.play()
                if event.key in {pygame.K_SPACE}:
                    game.rotate()
       
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
