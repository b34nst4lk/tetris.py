from math import cos, pi

def ease_in_sine(weight):
    return 1 - cos((weight * pi) / 2)
