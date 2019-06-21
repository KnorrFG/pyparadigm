import pygame

from pyparadigm import *
from pyparadigm.surface_composition import _text

from time import sleep

red_ball = None
green_ball = None
screen = None

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

def text_and_grid():
    font = Font(size=60)
    text = lambda text, color, align: Fill(color)(Text(text, font, antialias=True, align=align))
    frame = compose(screen.get_size(), Fill(0))(GridLayout(
        row_proportions=[2, 1], col_proportions=[1, 2]
    )(
        [text("Top left\nLine2", 0xFF0000, "left"), text("Top right\nLine2Blalalal", 0xFF00FF, "right")],
        [None, text("Bottom right", 0xFFFFFF, "center")]
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

def scaling_to_form():
    img = empty_surface(0xFF0000, (100, 100))
    frame = compose(screen.get_size())(
        Surface(scale=1, keep_aspect_ratio=False)(img)
    )
    display(frame)
    sleep(2)

def test_main():
    global red_ball, green_ball, screen
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((0, 0))
    red_ball = pygame.Surface((100, 100))
    green_ball = pygame.Surface((100, 100))
    pygame.draw.circle(red_ball, 0xFF0000, (50, 50), 50)
    pygame.draw.circle(green_ball, 0x00FF00, (50, 50), 50)

    layout_surface()
    fill_padding_overlay_cross_border()
    circle_brush_and_padding()
    text_and_grid()
    rectangle_shaper()
    scaling_to_form()
