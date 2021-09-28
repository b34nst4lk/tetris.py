from typing import List
from abc import ABC, abstractmethod

from src.settings import FPS


class Mode(ABC):
    @staticmethod
    @abstractmethod
    def ticks(level: int):
        pass

    @staticmethod
    @abstractmethod
    def score(lines_cleared: List[int], soft_drops: int):
        pass


class GameBoy(Mode):
    pass


class SNES(Mode):
    LEVELS_AND_FRAME_RATE = {
        0: 48,
        1: 43,
        2: 38,
        3: 33,
        4: 28,
        5: 23,
        6: 18,
        7: 13,
        8: 8,
        9: 6,
        10: 5,
        13: 4,
        16: 3,
        19: 2,
        29: 1,
    }

    LINES_CLEAR_SCORE = {
        1: 40,
        2: 100,
        3: 300,
        4: 1200,
    }

    @staticmethod
    def level(total_lines_cleared: int) -> int:
        return total_lines_cleared // 10

    @staticmethod
    def ticks(level: int):
        level = min([level, max(SNES.LEVELS_AND_FRAME_RATE)])
        while not SNES.LEVELS_AND_FRAME_RATE.get(level):
            level -= 1
        return SNES.LEVELS_AND_FRAME_RATE[level] / FPS * 1000

    @staticmethod
    def score(lines_cleared: List[int], soft_drops: int, level: int) -> int:
        total_lines_cleared = sum(lines_cleared)
        score = SNES.LINES_CLEAR_SCORE[total_lines_cleared] * (level + 1)
        return score
