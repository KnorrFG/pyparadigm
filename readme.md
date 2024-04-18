# PyParadigm

PyParadigm is a small library to build paradigms for psychological experiments.
It utilizes pygame, and is installable via pip
    
    pip install pyparadigm

You can find the documentation including an introduction
and a tutorial over at: https://pyparadigm.readthedocs.io/en/latest/index.html

## Changelog

* 1.2.1
    * Replaces pygame.init() with pygame.display.init() in pyparadigms init method,
      so not required modules are not initialized
* 1.2.0
    * Adds the FreeFloatLayout
    * Adds the Title argument to misc.init()
* 1.1.0
    * adds the sleeptime argument to eventlistener.listen_until_return() and
      eventlistener.wait_for_keypresses()
    * Mousproxys can now take handler functions of arity 4. The last argument
      will then be the rect of the MouseProxy. Arity 3 is still allowed
    * fixes a bug, that made a MouseProxy not match the drawArea of a child
      surface
    * Adds an event handler for resize events
    * Adds an event handler for Quit events
* 1.0.9
    * added the keep_aspect_ratio parameter to Surface
    * added normalize parameter to mat_to_surface()
    * added dialog module
    * fixed a bug that would cause a crash, if misc.empty_surface() was used
      with size but without initializing the windows
    * fixes a bug that would miss-align grid layout items, if not all rows had
      the same number of elements
* 1.0.8
    * added misc.rgba for conversion of color codes to pygame.Color with alpha
      channel, useful for text-colors
    * Fixed a bug, that would cause a Gridlayout to crash if 
      a None is added
    * Fixed a bug that would cause crashes when adding iterable objects with a
      draw method to a render object with a single child
    * Added functions:
        * is_left_click()
        * is_key_press()
* 1.0.7
    * fixed a bug in EventListener.wait_for_n_key_presses()
    * fixed a code sample in the tutorial
* 1.0.6
    * added special treatment for Surfaces in MouseProxy, so that the actual visible rect is obtained. For that I added a new method, Surface.compute_render_rect
* 1.0.5
    * Fixed surface_composition.Border.__call__()
    * added EventListener.wait_for_unicode_char() and misc.process_char() for textinput
    * added EventListener.listen_until_return()
    * added Handler class which contains factories for handler functions that can be used with EventListener.Listen()
    * added MouseProxy, EventListener.mouse_area and EventListener.group() for basic mouse support.
* 1.0.4
    * Added EventListener.wait_for_keys_modified
    * Added the extras module containing functions to use numpy arrays and Matplotlib colormaps
* 1.0.3
    * EventListener.wait_for_keys supports varargs now
* 1.0.2:
    * added imports on package level
    * added interactive parameter for misc
* 1.0.1:
    * Added PyPi readme
* 1.0 - release

