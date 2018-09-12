"""misc"""

import pygame
from . import surface_composition as sc

from functools import lru_cache


def display(surface):
    screen = pygame.display.get_surface()
    screen.blit(surface, (0, 0))
    pygame.display.flip()


def slide_show(slides, continue_handler):
    for slide in slides:
        display(slide)
        continue_handler()


def empty_surface(fill_color, size=None):
    """Returns an empty surface filled with fill_color.

    :param fill_color: color to fill the surface with
    :type fill_color: pygame.Color

    :param size: the size of the new surface, if None its created
        to be the same size as the screen
    :type size: int-2-tuple
    """
    sr = pygame.display.get_surface().get_rect()
    surf = pygame.Surface(size or (sr.w, sr.h))
    surf.fill(fill_color)
    return surf
