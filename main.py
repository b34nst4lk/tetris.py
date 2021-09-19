import pygame

from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod

from src.tetriminos import (
    Matrix,
    TetriminoDisplay,
    TetriminoQueue,
    game_over,
)

from src.settings import (
    WIDTH,
    HEIGHT,
    FPS,
)

from src.utils import asset_resource_path


def calculate_score(lines_cleared: List[int]) -> int:
    total_score = 0
    for i in lines_cleared:
        total_score += int(2 ** (i - 1) * 1000)
    return total_score


@dataclass
class Scene(ABC):
    screen: pygame.display

    def __post_init__(self):
        self.init_widgets()
        self.init_state()
        self.init_assets()
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(FPS)

    @abstractmethod
    def init_widgets(self):
        pass

    @abstractmethod
    def init_state(self):
        pass

    @abstractmethod
    def init_assets(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass


@dataclass
class GameScene(Scene):
    def init_widgets(self):
        self.shape_generator = TetriminoQueue()
        self.stashed_tetrimino = TetriminoDisplay(self.screen, (40, 100))
        self.matrix = Matrix(self.screen, (400, 100), self.shape_generator)
        self.next_tetrimino = TetriminoDisplay(self.screen, (920, 100))

    def init_state(self):
        self.running = True
        self.can_stash = True
        self.locked = False
        self.total_score = 0

        self.start_time = pygame.time.get_ticks()

    def init_assets(self):
        self.font = pygame.font.SysFont("monospace", 50)

    def update(self):
        self.next_tetrimino.set_tetrimino(*self.shape_generator.peek())

        active_tetrimino = self.matrix.get_tetrimino()
        if not self.locked:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in {pygame.K_ESCAPE, ord("q")}:
                        self.running = False
                    if event.key == pygame.K_LEFT:
                        self.matrix.move_left()
                    if event.key == pygame.K_RIGHT:
                        self.matrix.move_right()
                    if event.key == pygame.K_DOWN:
                        self.matrix.move_down()
                    if event.key == pygame.K_SPACE:
                        self.locked = True
                    if event.key == pygame.K_UP:
                        self.matrix.rotate()
                    if event.key == pygame.K_RETURN and self.can_stash:
                        self.can_stash = False
                        stash = self.matrix.stash()
                        self.stashed_tetrimino.set_tetrimino(*stash)

            if pygame.time.get_ticks() - self.start_time > 300:
                self.matrix.move_down()
                self.start_time = pygame.time.get_ticks()

        else:
            self.matrix.move_down()

        if active_tetrimino.placed:
            self.locked = False
            self.can_stash = True
            lines_cleared = self.matrix.clear_lines()
            self.total_score += calculate_score(lines_cleared)

        if self.matrix.is_game_over():
            game_over()
            self.running = False

    def render(self):
        self.screen.fill((0, 0, 0))

        self.matrix.render()
        self.stashed_tetrimino.render()
        self.next_tetrimino.render()
        label = self.font.render(f"{self.total_score}", 1, (255, 255, 255))
        self.screen.blit(label, (460, 50))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 800, HEIGHT + 200))

    # drop_sound = pygame.mixer.Sound(asset_resource_path("drop.wav"))
    # pygame.mixer.music.load(asset_resource_path("bgm.wav"))
    # pygame.mixer.music.play(-1)

    game_scene = GameScene(screen)
    game_scene.run()
    pygame.quit()


if __name__ == "__main__":
    main()
