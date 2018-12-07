"""A package to build psychological Paradigms. Based on PyGame """
__version__ = '1.0.4'


from .eventlistener import EventConsumerInfo, EventListener
from .misc import init, display, empty_surface, slide_show
from .surface_composition import Border, Circle, Fill, LLItem, LinLayout,\
    Line, Margin, Overlay, Padding,\
    RectangleShaper, Surface, Cross, Font,\
    GridLayout, Text, compose

try:
    __import__("numpy")
    __import__("matplotlib")
    from .extras import  mat_to_surface, apply_color_map, to_24bit_gray
except ImportError:
    pass