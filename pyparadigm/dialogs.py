"""This module contains dialogues, which will query user input"""
from functools import lru_cache

import contextlib
with contextlib.redirect_stdout(None):
    import pygame

from . import surface_composition as psc
from . import eventlistener as pel
from . import misc


def _center_renderer(elem):
    misc.display(psc.compose(pygame.display.get_surface())(
        psc.Padding.from_scale(0.5)(elem)))


def _base_dialog(caption, input, fill_color=0xFFFFFF):
    return psc.Border(width=10)(
        psc.Fill(fill_color)(
            psc.Padding(0.05, 0.05, 0.1, 0.1)(
                psc.LinLayout("v")(
                    caption,
                    psc.LinLayout("v")(
                        psc.Surface(psc.Margin(0, 1, 1, 0))(input),
                        psc.LLItem(0.01)(psc.Line("h")))))))


@lru_cache()
def _text_converter(s):
    return psc.Text(s, psc.Font(size=50), antialias=True)


def string_dialog(caption: str, renderer: callable = _center_renderer,
                  el: pel.EventListener = None, text_renderer=_text_converter):
    """Will display a dialog which gets a string as input from the user.
    By default the dialog will be rendered to the screen directly, to control
    the target pass a callable as renderer which takes a single argument, which
    is an element tree. This will be called by string_dialog to display itself.
    You can pass an eventlistener instance, which will then be used in case you
    got some important permanent handlers that must be run. You can pass a
    function that converts a string to something that can be used within
    compose() with the text_renderer to control the optic of the text"""
    el = el or pel.EventListener()
    buffer = ""
    while True:
        renderer(_base_dialog(text_renderer(caption), text_renderer(buffer)))
        key = el.wait_for_unicode_char()
        if key == "\x1b": # Str representation of ESC
            return None
        elif key == "\x0D": # Return
            return buffer
        else:
            buffer = misc.process_char(buffer, key)

    
