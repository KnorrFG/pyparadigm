
PyParadigm
==========

PyParadigm is a small library to build paradigms for psychological experiments.
It utilizes pygame, and is installable via pip ::
    
    pip install pyparadigm

You can find the documentation including an introduction
and a tutorial over at: https://pyparadigm.readthedocs.io/en/latest/index.html

Changelog
---------
* 1.0.5
    * Fixed surface_composition.Border.__call__()
    * added EventListener.wait_for_unicode_char() and misc.process_char()
        for textinput
    * added EventListener.listen_until_return()
    * added Handler class which contains factories for handler functions
        that can be used with EventListener.Listen()
    * added MouseProxy, EventListener.mouse_area and EventListener.group()
        for basic mouse support.

* 1.0.4
    * Added EventListener.wait_for_keys_modified
    * Added the extras module containing functions to use numpy arrays
        and Matplotlib colormaps
    
* 1.0.3
    * EventListener.wait_for_keys supports varargs now

* 1.0.2:
    * added imports on package level
    * added interactive parameter for misc

* 1.0.1:
    * Added PyPi readme

* 1.0 - release