COLOR_BLACK = (0, 0, 0)
COLOR_BRIGHT_WHITE = (255, 255, 255)
COLOR_MEDIUM_WHITE = (63, 63, 63)
COLOR_WHITE = (1, 1, 1)

COLOR_BLUE = (0, 127, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)


def opacity(color: tuple, opacity: float) -> tuple:
    """Return a given color with a given opacity."""
    return tuple(int(color[i] * opacity) for i in range(3))


def random():
    """Return a random color."""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
