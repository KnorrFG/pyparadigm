"""The Eventlistener wraps pygames event-loop.

The Core method is the listen() method.
It gathers the events that have piled up in pygame so far
and processes them acording to handler functions.
This allows for a main-loop free script design, which is more suited for
experimental paradigms.
In a typical experiment the script just waits for a userinput and does nothing,
or only a very few things in between. Approaching this need with a main
event-loop requires the implementation of some sort of statemachine, which again
requires quite some code.

The EventListener enables one to write scripts in a time-linear manner, and only
dab into local event-loops whenever neccessary throught the listen-function.

There are a few pre-implemented methods, which cover most of those use-cases in
the developement of experimental paradigms.

* wait_for_keypress() will return once a key was pressed n times.
* wait_for_keys_timed_out() will wait for one of multiple possible keys, 
    but return after the given timeout in any case
* and wait_for_seconds will simply wait the given time, but in the mean-time run
  what ever handlers were passed to the EventListener.

By default, there is one permanent handler, which will call exit(1) when 
Ctrl + c is pressed.
"""
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    
from pygame import (KMOD_LSHIFT, KMOD_RSHIFT, KMOD_SHIFT, KMOD_CAPS,
                    KMOD_LCTRL, KMOD_RCTRL, KMOD_CTRL, KMOD_LALT, KMOD_RALT,
                    KMOD_ALT, KMOD_LMETA, KMOD_RMETA, KMOD_META, KMOD_NUM, KMOD_MODE)

from enum import Enum

import time
import itertools as itt


class EventConsumerInfo(Enum):
    """Can be returned by event-handler functions to communicate with the listener.
    For Details see EventListener"""
    DONT_CARE = 0
    CONSUMED = 1


def _is_iterable(val):
    try:
        some_object_iterator = iter(val)
        return True
    except TypeError as te:
        return False


class EventListener(object):
    """
    :param permanent_handlers: iterable of permanent handlers
    :type permanent_handlers: iterable
    :param use_ctrl_c_handler: specifies whether a handler that quits the
        script when ctrl + c is pressed should be used
    :type use_ctrl_c_handler: Bool
    """

    _mod_keys = {KMOD_LSHIFT, KMOD_RSHIFT, KMOD_SHIFT, KMOD_CAPS,
                 KMOD_LCTRL, KMOD_RCTRL, KMOD_CTRL, KMOD_LALT, KMOD_RALT,
                 KMOD_ALT, KMOD_LMETA, KMOD_RMETA, KMOD_META, KMOD_NUM, KMOD_MODE}

    @staticmethod
    def _contained_modifiers(mods, mods_of_interes=_mod_keys):
        return frozenset(mod for mod in mods_of_interes if mod & mods)

    @staticmethod
    def _exit_on_ctrl_c(event):
        if event.type == pygame.KEYDOWN \
                and event.key == pygame.K_c \
                and pygame.key.get_mods() & pygame.KMOD_CTRL:
            pygame.quit()
            exit(1)
        else:
            return EventConsumerInfo.DONT_CARE

    def __init__(self, permanent_handlers=None, use_ctrl_c_handler=True):
        self._current_q = []
        if use_ctrl_c_handler:
            self.permanent_handlers = (
                EventListener._exit_on_ctrl_c,
            )
            if permanent_handlers:
                self.permanent_handlers += permanent_handlers
        else:
            self.permanent_handlers = permanent_handlers or []

    def _get_q(self):
        self._current_q = itt.chain(self._current_q, pygame.event.get())
        return self._current_q

    def listen(self, temporary_handlers=None):
        """When listen() is called all queued pygame.Events will be passed to all
        registered listeners. There are two ways to register a listener:

        1. as a permanent listener, that is always executed for every event. These
            are registered by passing the handler-functions during construction

        2. as a temporary listener, that will only be executed during the current
            call to listen(). These are registered by passing the handler functions
            as arguments to listen()

        When a handler is called it can provoke three different reactions through
        its return value.

        1. It can return EventConsumerInfo.DONT_CARE in which case the EventListener
            will pass the event to the next handler in line, or go to the next event,
            if the last handler was called.

        2. It can return EventConsumerInfo.CONSUMED in which case the event will not
            be passed to following handlers, and the next event in line will be
            processed.

        3. It can return anything else (including None, which will be returned if no
            return value is specified) in this case the listen()-method will return
            the result of the handler.

        Therefore all permanent handlers should usually return
        EventConsumerInfo.DONT_CARE
        """
        if temporary_handlers:
            funcs = self.permanent_handlers + temporary_handlers
        else:
            funcs = self.permanent_handlers

        for event in self._get_q():
            for func in funcs:
                ret = func(event)
                if ret == EventConsumerInfo.CONSUMED:
                    break
                if ret == EventConsumerInfo.DONT_CARE:
                    continue
                else:
                    return ret

    def wait_for_n_keypresses(self, key, n=1):
        """Waits till one key was pressed n times.

        :param key: the key to be pressed as defined by pygame. E.g.
            pygame.K_LEFT for the left arrow key
        :type key: int
        :param n: number of repetitions till the function returns
        :type n: int
        """
        my_const = "key_consumed"
        counter = 0

        def keypress_listener(e): return my_const \
            if e.type == pygame.KEYDOWN and e.key == key \
            else EventConsumerInfo.DONT_CARE

        while counter < n:
            if self.listen((keypress_listener,)) == my_const:
                counter += 1

    def wait_for_keys(self, *keys, timeout=0):
        """Waits until one of the specified keys was pressed, and returns 
        which key was pressed.

        :param keys: iterable of integers of pygame-keycodes, or simply 
            multiple keys passed via multiple arguments
        :type keys: iterable
        :param timeout: number of seconds to wait till the function returns
        :type timeout: float

        :returns: The keycode of the pressed key, or None in case of timeout
        :rtype: int
        """
        if len(keys) == 1 and _is_iterable(keys[0]):
            keys = keys[0]

        listeners = tuple(lambda e, key=key: key
                          if e.type == pygame.KEYDOWN and e.key == key
                          else EventConsumerInfo.DONT_CARE
                          for key in keys)

        start = time.time()
        while timeout == 0 or time.time() - start < timeout:
            res = self.listen(listeners)
            if res in keys:
                return res

        return None

    def wait_for_keys_modified(self, *keys, modifiers_to_check=_mod_keys,
                               timeout=0):
        """The same as wait_for_keys, but returns a frozen_set which contains 
        the pressed key, and the modifier keys.

        :param modifiers_to_check: iterable of modifiers for which the function
            will check whether they are pressed

        :type modifiers: Iterable[int]"""

        set_mods = pygame.key.get_mods()
        return frozenset.union(
            frozenset([self.wait_for_keys(*keys, timeout=timeout)]),
            EventListener._contained_modifiers(set_mods, modifiers_to_check))

    def wait_for_seconds(self, seconds):
        """basically time.sleep() but in the mean-time the permanent handlers 
        are executed"""
        start = time.time()
        while time.time() - start < seconds:
            self.listen()
