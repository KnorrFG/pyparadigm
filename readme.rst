
PyParadigm
==========

PyParadigm is a small library to build paradigms for psychological experiments.
It utilizes pygame, and is installable via pip ::
    
    pip install pyparadigm

You can find the documentation including an introduction
and a tutorial over at: https://pyparadigm.readthedocs.io/en/latest/index.html

Changelog
---------
* 1.0.8
    * Fixed a bug, that would cause a Gridlayout to crash if 
        a None is added
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