import pygame

from pyparadigm.surface_composition import *

from time import sleep

red_ball = None
green_ball = None
screen = None

class testSurface:
    @classmethod
    def setUp(cls):
        global screen, red_ball, green_ball
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((800, 600))
        red_ball = pygame.Surface((100, 100))
        green_ball = pygame.Surface((100, 100))
        pygame.draw.circle(red_ball, 0xFF0000, (50, 50), 50)
        pygame.draw.circle(green_ball, 0x00FF00, (50, 50), 50)

    @staticmethod
    def layout_surface():
        frame = compose(screen.get_size(), LinLayout("h"))(
            LLItem(2)(red_ball),
            LinLayout("v")(
                green_ball,
                Surface(scale=0.1)(green_ball), 
                green_ball),
            red_ball
        )

        screen.blit(frame, (0, 0))
        pygame.display.flip()
        sleep(3)

    @staticmethod
    def circle_brush_and_padding():
        frame = compose(screen.get_size(), LinLayout("h"))(
            Circle(0x0000FF),
            Padding(0.2, 0.3, 0, 0.4)(Circle(0xFF00FF, 2))
        )
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        sleep(3)

    @staticmethod
    def fill_padding_overlay():
        frame = compose(screen.get_size(), Overlay())(
            Circle(0xFF00FF),
            Padding(0.1, 0.1, 0.1, 0.1)(Fill(0xFF0000)(
                Circle(0xFFFF00))),
            green_ball
        )
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        sleep(3)

    @classmethod
    def test_basics(cls):
        testSurface.layout_surface()
        testSurface.fill_padding_overlay()
        testSurface.circle_brush_and_padding()


