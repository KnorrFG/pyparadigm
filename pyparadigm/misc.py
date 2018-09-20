"""Contains code that did not make it into an own module."""

import pygame
from . import surface_composition as sc

import os
from functools import lru_cache


def init(resolution, pygame_flags=0, display_pos=(0, 0)):
    """Creates a window of given resolution.

    :param resolution: the resolution of the windows as (width, height) in
        pixels
    :type resolution: tuple
    :param pygame_flags: modify the creation of the window.
        For further information see :ref:`creating_a_window`
    :type pygame_flags: int
    :param display_pos: determines the position on the desktop where the
        window is created. In a multi monitor system this can be used to position
        the window on a different monitor. E.g. the monitor to the right of the
        main-monitor would be at position (1920, 0) if the main monitor has the
        width 1920.
    :type display_pos: tuple
    """
    os.environ['SDL_VIDEO_WINDOW_POS'] = "{}, {}".format(*display_pos)
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(resolution, pygame_flags)

def display(surface):
    """Displays a pygame.Surface in the window.
    
    in pygame the window is represented through a surface, on which you can draw
    as on any other pygame.Surface. A refernce to to the screen can be optained
    via the :py:func:`pygame.display.get_surface` function. To display the
    contents of the screen surface in the window :py:func:`pygame.display.flip`
    needs to be called.
    
    :py:func:`display` draws the surface onto the screen surface at the postion
    (0, 0), and then calls :py:func:`flip`.
    
    :param surface: the pygame.Surface to display
    :type surface: pygame.Surface
    """
    screen = pygame.display.get_surface()
    screen.blit(surface, (0, 0))
    pygame.display.flip()


def slide_show(slides, continue_handler):
    """Displays one "slide" after another.

    After displaying a slide, continue_handler is called without arguments.
    When continue_handler returns, the next slide is displayed.

    Usage example ::

        slide_show(text_screens,
                   partial(event_listener.wait_for_n_keypresses, pygame.K_RETURN))  

    (partial is imported from the functools module.) 

    :param slides: pygame.Surfaces to be displayed.
    :type slides: iterable
    :param continue_handler: function, that returns when the next slide should
        be displayed.
    :type continue_handler: callable with arity 0.
    """
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