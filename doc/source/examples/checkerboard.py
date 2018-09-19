import pygame
from pyparadigm.misc import init, display, empty_surface
from pyparadigm.surface_composition import compose
from pyparadigm.eventlistener import EventListener

def main():
    init((1024, 800))
    frames = [pygame.image.load(f"checkerboard_{i}.png") for i in range(2)]
    event_listener = EventListener()
    display(compose(empty_surface(0xFFFFFF))(Text(
        """Press Return to start.

        Press again to end.""", Font())))
    event_listener.wait_for_n_keypresses(pygame.K_RETURN)
    
    


if __name__ == '__main__':
    main()