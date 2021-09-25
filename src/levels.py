from src.settings import FPS

SNES_LEVELS_AND_FRAME_RATE = {
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

def get_snes_speed(level: int):
    level = min([level, max(SNES_LEVELS_AND_FRAME_RATE)])
    while not SNES_LEVELS_AND_FRAME_RATE.get(level):
        level -= 1
    return SNES_LEVELS_AND_FRAME_RATE[level] / FPS * 1000 
