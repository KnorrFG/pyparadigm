import pygame
from pyparadigm.misc import init, display, empty_surface
from pyparadigm.surface_composition import compose, Surface, Text, Font
from pyparadigm.eventlistener import EventListener
from functools import lru_cache
from itertools import cycle

def render_frame(screen, frame):
    # This time we dont use :py:func:`misc.display` and instead draw directly
    # onto the screen, and call flip() then to display it. Usually we would want
    # to generate a screen with a function (with lru_cache), and then use
    # :py:func:`misc.display` to blit the different screens. This way every
    # screen is only computed once. This time though, no screens are computed,
    # it is simply displaying an existing image, and no screens are reused.
    compose(screen)(Surface(scale=1)(frame))
    pygame.display.flip()


def main():
    # we want to display the two states with 2Hz, therefore the timeout is 1/2s
    timeout = 0.5
    # initialize a window, and get a reference to the pygame.Surface
    # representing the screen.
    screen = init((1024, 800))
    # Load the frames. When loading a pygame.Surface from a file, you should
    # always call convert() on it, this will change the image format to optimize
    # performance. If you have an image that uses transparent pixels, use
    # convert_alpha() instead.
    # We use itertools.cycle to get an iterator that will alternate between the
    # images, see the python-doc (https://docs.python.org/3/library/itertools.html)
    frames = cycle([pygame.image.load(f"checkerboard_{i}.png").convert() 
                        for i in range(2)])
    # Create an EventListener object. No additional handlers needed here.
    event_listener = EventListener()
    # Display an initial text
    display(compose(empty_surface(0xFFFFFF))(Text(
        """Press Return to start.

        Press again to end.""", Font(size=60))))
    # Wait for the return key
    event_listener.wait_for_n_keypresses(pygame.K_RETURN)
    key = None
    # Repeat until return is pressed again
    while key == None:
        # display one of the two checkerboard images
        render_frame(screen, next(frames))
        # wait for timeout seconds for RETURN to be pressed. If RETURN is
        # pressed :py:meth:`EventListener.wait_for_keys` will return
        # pygame.K_RETURN otherwise it will return NONE
        key = event_listener.wait_for_keys([pygame.K_RETURN], timeout)
    


if __name__ == '__main__':
    main()