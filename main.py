import pygame

from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from src.levels import SNES

from src.tetriminos import (
    Matrix,
    TetriminoDisplay,
    TetriminoQueue,
    Text,
    ReactiveText,
)

from src.settings import (
    WIDTH,
    HEIGHT,
    FPS,
)

from utils.io import asset_resource_path


def calculate_score(lines_cleared: List[int]) -> int:
    total_score = 0
    for i in lines_cleared:
        total_score += int(2 ** (i - 1) * 1000)
    return total_score


@dataclass
class Scene(ABC):
    screen: pygame.display

    def __post_init__(self):
        self.init_assets()
        self.init_state()
        self.init_widgets()
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            next_scene, params = self.update()
            if next_scene:
                return next_scene, params
            self.render()
            pygame.display.flip()
            self.clock.tick(FPS)
        return None, None

    def init_widgets(self):
        pass

    def init_state(self):
        pass

    def init_assets(self):
        pass

    def update(self) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_ESCAPE, ord("q")}:
                    self.running = False
        return None, None

    @abstractmethod
    def render(self):
        pass


@dataclass
class GameScene(Scene):
    def init_widgets(self):
        self.shape_generator = TetriminoQueue()
        self.stashed_tetrimino = TetriminoDisplay(self.screen, (400, 100))
        self.matrix = Matrix(self.screen, (400, 260), self.shape_generator)
        self.next_tetrimino = TetriminoDisplay(self.screen, (720, 100))
        self.score_text = ReactiveText(
            self.screen, (560, 100), (160, 60), self.font, "0"
        )
        self.level_text = Text(
            self.screen, (560, 160), (160, 60), self.font, f"Level {self.level}"
        )

        self.mousables = [self.score_text]

    def init_state(self):
        self.running = True
        self.can_stash = True
        self.locked = False
        self.total_score = 0
        self.lines_cleared = 0

        self.start_time = pygame.time.get_ticks()

    def init_assets(self):
        self.font = pygame.font.SysFont("monospace", 34)

    @property
    def level(self) -> int:
        return self.lines_cleared // 10

    def update(self):
        self.next_tetrimino.set_tetrimino(*self.shape_generator.peek())

        active_tetrimino = self.matrix.get_tetrimino()
        if not self.locked:
            for event in pygame.event.get():
                if event.type in {
                    pygame.MOUSEMOTION,
                    pygame.MOUSEBUTTONUP,
                    pygame.MOUSEBUTTONDOWN,
                }:
                    for subscriber in self.mousables:
                        subscriber.push(event)
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
                    # if event.key == ord("s"):
                    #     self.matrix.rotate()
                    if event.key == ord("a"):
                        self.matrix.rotate(-1)
                    if event.key == pygame.K_RETURN and self.can_stash:
                        self.can_stash = False
                        stash = self.matrix.stash()
                        self.stashed_tetrimino.set_tetrimino(*stash)

            if pygame.time.get_ticks() - self.start_time > SNES.ticks(self.level):
                self.matrix.move_down()
                self.start_time = pygame.time.get_ticks()

        else:
            self.matrix.move_down()

        lines_cleared = 0
        if active_tetrimino.placed:
            self.locked = False
            self.can_stash = True
            lines_cleared = self.matrix.clear_lines()

        if lines_cleared:
            self.lines_cleared += sum(lines_cleared)
            self.total_score += SNES.score(lines_cleared, 0, self.level)
            self.score_text.set_text(self.total_score)
            self.level_text.set_text(f"Level {self.level}")

        if self.matrix.is_game_over():
            self.running = False
            return "game_over", {"score": self.total_score}

        return None, None

    def render(self):
        self.screen.fill((0, 0, 0))

        self.matrix.render()
        self.stashed_tetrimino.render()
        self.next_tetrimino.render()
        self.score_text.render()
        self.level_text.render()


@dataclass
class GameOverScene(Scene):
    score: int

    def init_assets(self):
        self.font = pygame.font.SysFont("monospace", 50)

    def init_widgets(self):
        self.game_over = ReactiveText(
            self.screen, (500, 500), (160, 120), self.font, "GAME OVER"
        )
        self.score_text = Text(
            self.screen, (500, 700), (160, 120), self.font, str(self.score)
        )

    def render(self):
        self.game_over.render()
        self.score_text.render()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 800, HEIGHT + 400))

    # drop_sound = pygame.mixer.Sound(asset_resource_path("drop.wav"))
    # pygame.mixer.music.load(asset_resource_path("bgm.wav"))
    # pygame.mixer.music.play(-1)

    scenes = {
        "game": GameScene,
        "game_over": GameOverScene,
    }

    next_scene_key, params = "game", {}
    running = True
    while running:
        scene = scenes[next_scene_key](screen, **params)
        print(next_scene_key)
        next_scene_key, params = scene.run()
        if not next_scene_key:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
