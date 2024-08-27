"""A package to build psychological Paradigms. Based on PyGame """
__version__ = '1.2.2'


from .eventlistener import EventConsumerInfo, EventListener, Handler,\
    MouseProxy, MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT, MOUSE_SCROL_FW,\
    MOUSE_SCROL_BW, is_left_click, is_key_press
from .misc import init, display, empty_surface, slide_show, process_char,\
    rgba, make_transparent_by_mask, make_transparent_by_colorkey
from .surface_composition import Border, Circle, Fill, LLItem, LinLayout,\
    Line, Margin, Overlay, Padding,\
    RectangleShaper, Surface, Cross, Font,\
    GridLayout, Text, compose, FreeFloatLayout, FRect
from .dialogs import string_dialog

try:
    __import__("numpy")
    __import__("matplotlib")
    from .extras import  mat_to_surface, apply_color_map, to_24bit_gray
except ImportError:
    pass
