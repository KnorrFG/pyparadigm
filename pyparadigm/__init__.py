"""A package to build psychological Paradigms. Based on PyGame

Changelog:
    pending:
        * added imports on package level

    1.0.1:
        * Added PyPi readme

    1.0 - release
"""
__version__ = '1.0.1'


from .eventlistener import EventConsumerInfo, EventListener
from .misc import init, display, empty_surface, slide_show
from .surface_composition import Border, Circle, Fill, LLItem, LinLayout,\
                                 Line, Margin, Overlay, Padding,\
                                 RectangleShaper, Surface, Cross, Font,\
                                 GridLayout, Text, compose
