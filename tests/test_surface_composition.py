import pygame

from pyparadigm.surface_composition import *
from pyparadigm.surface_composition import _text

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
        screen = pygame.display.set_mode((1280, 800))
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
        sleep(1)

    @staticmethod
    def circle_brush_and_padding():
        frame = compose(screen.get_size(), LinLayout("h"))(
            LinLayout("v")(
                LLItem(1), 
                Circle(0x0000FF)
            ),
            Padding(0.2, 0.3, 0, 0.4)(Circle(0xFF00FF, 2))
        )
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        sleep(1)

    @staticmethod
    def fill_padding_overlay_cross_border():
        frame = compose(screen.get_size(), Overlay)(
            Circle(0xFF00FF),
            Padding(0.1, 0.1, 0.1, 0.1)(Fill(0xFF0000)(
                 Padding.from_scale(0.5)(
                     Padding.from_scale(0.5, 1)(
                        Border()(Cross(width=10)))))),
            green_ball
        )
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        sleep(1)

    @staticmethod
    def text_and_grid():
        font = Font(size=60)
        text = lambda text, color, align: Fill(color)(Text(text, font, antialias=True, align=align))
        frame = compose(screen.get_size(), Fill(0xFFFFFF))(GridLayout(
            row_proportions=[2, 1], col_proportions=[1, 2]
        )(
            [text("Top left\nLine2", 0xFF0000, "left"), text("Top right\nLine2Blalalal", 0xFF00FF, "right")],
            [text("Bottom left", 0xFFFF00, "center"), _text("Bottom right", font)]
        ))
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        sleep(1)

    def rectangle_shaper():
        frame = compose(screen.get_size())(
            RectangleShaper(1, 2)(Fill(0xFFFFFF)(
                RectangleShaper(2, 1)(Fill(0xFF)(
                    RectangleShaper()(
                        Fill(0x00FF00)
                    )
                ))
            ))
        )
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        sleep(1)

    @classmethod
    def test_basics(cls):
        testSurface.layout_surface()
        testSurface.fill_padding_overlay_cross_border()
        testSurface.circle_brush_and_padding()
        testSurface.text_and_grid()
        testSurface.rectangle_shaper()


