A tutorial
==========

Installation
------------

As most python libraries, PyParadigm can be installed via pip: ::

    pip install pyparadigm

And thats it.

Overview
--------

PyParadigm is split into 3 modules:
    * :doc:`surfacecomposition` which allows to create
        pygame.Surfaces , which is the class representing images, in a
        declarative way.
    * :doc:`eventlistener` which allows to react to user input
    * :doc:`misc` which just contains a few utility functions


.. _creating_a_window:

Creating a Window
-----------------
In the simplest scenario, creating a window is nothing but a call to the
:py:func:`init` function from :doc:`the misc module <misc>`, which only takes
one parameter: a 2-tuple with the prefered resolution. E.g. ``init((800,
600))``. However, most of the time, this is not, what you will want. 
Usually you want to create a Full-screen, or borderless window (which looks like
fullscreen, if it has the size of the screen, but behaves a little different).
For these scenarios, you can use the pygame_flags argument. 
One of the things that :py:func:`init` does is calling
`pygame.display.set_mode()
<https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode>`_, which
is the pygame function that created the window, and the flags argument is passed
through. Here a short list of flags you will care about the most:

* ``pygame.FULLSCREEN`` which will create a full-screen window.
* ``pygame.NOFRAME`` which creates a window without window-frame. This looks
    like fullscreen, if the created window has the same resolution as the desktop,
    and is placed at (0, 0).

By default, the CPU will be used to render the images. This should suffice for
most paradigms. If, however, your paradigm is to computationally intensive, and
requires a GPU, you can use pygame.HWSURFACE, usually in combination with
pygame.DOUBLEBUF and pygame.FULLSCREEN, you can combine multiple flags with the
``|`` operator. E.g:

.. code-block:: python

    init((1920, 1080), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

A warning: Creating a hardware accelerated window in other systems than Windows 
can be problematic.


.. _creating_surfaces:

Creating Surfaces
-----------------
The basic idea is to avoid worrying about absolute positions. Using
:py:func:`compose` an image-structure can be described as a tree of elements.
E.g.:

.. code-block:: python

    image = compose(target_surface)(
        LinLayout("h")(
            Circle(0xFF0000),
            Circle(0x00FF00)
        )
    )

Here the available space (which is the size of target_surface) would divided 
horizontally into 2 parts of equal size. Then a red circle will be drawn into
the left area and blue one in the right area. The trees can get arbitrarily
complex, and I recommend to take a look at the :doc:`examples<examples>`

Here is a list of the different elements that can be used within
:py:func:`compose`

* Containers with multiple children: 
    * :py:class:`LinLayout` Aranges items in a horizontal or vertical line
    * :py:func:`GridLayout` Aranges items in a grid
    * :py:class:`Overlay` Draws its children on top of each other
* Wrapper, which take a single child:
    * :py:class:`Padding` Creates a padding around its child
    * :py:class:`LLItem` Only usable within a LinLayout, defines proportions of
        Items within a LinLayout
    * :py:class:`Surface` Is actually a primitive, it wraps pygame.Surfaces.
        E.g. loaded stimuli from files, or Texts, which are also generated as
        Surfaces. All pygame.Surfaces in a Tree are wrapped in Surface objects
        automatically. But it can be done manually to change placement or scaling options
    * :py:class:`RectangleShaper` Closely related to :py:class:`Padding`. It
        will create horizontal or vertical padding to create a child-shape with
        desired aspect ratio.
    * :py:class:`Fill` Fills the assigned area with a given color before
        rendering its child. Can also be used without child.
    * :py:class:`Border` Creates a border around its area. Can also be used
        without child
* Primitives that don't take any children:
    * :py:class:`Circle` Draws a circle in the assigned area
    * :py:func:`Cross` Draws a cross within the assigned area
    * :py:class:`Line` Draws a line within the assigned area
    * :py:func:`Text` Creates a pygame.Surface containing the passed text. The
        text can be multi line, left-/ or right-aligned or centered. It takes a
        pygame.Font as additional argument.

Children are generally passed vial the :py:func:`__call__` operator of the
object. E.g. ``LinLayout("h")(child1, child2, child3)``
Whenever something only takes a single child the child can be a container, and
this way it is possible to add multiple children whenever only one child is
allowed. Also compose itself allows only one child, which gets the whole image
as target area, but since a lot of compose calls would have a container as child
compose allows a second argument, which can be any component that takes at least
one child (except for Surface). The above example could also be written like this:
    
.. code-block:: python

    image = compose(target_surface, LinLayout("h"))(
            Circle(0xFF0000),
            Circle(0x00FF00)
    )

The first argument to :py:func:`compose` can either be a surface to render on
(like above) or a 2-tuple with width and height. In the second case a new
surface with the specified dimensions would be created. To get a desired
background color for the newly created surface the root component should be a
:py:class:`Fill` object.

The most common case though would be

.. code-block:: python

    image = compose(empty_surface(color), LinLayout("h"))(
            Circle(0xFF0000),
            Circle(0x00FF00)
    )

:py:func:`empty_surface` is part of the :doc:`misc-module</misc>` and will create
a new surface which is automatically filled with the given color. As second
argument a size for the new surface can be specified. If the size argument is
omitted the created surface will automatically have the size of the display.

To display saved images, use :py:func:`pygame.image.load`, and just use the
loaded pygame.Surface in compose.

Creating Text
~~~~~~~~~~~~~
:py:func:`Text` is not an object with a draw-method, but a function that returns
a pygame.Surface which contains the text on a transparent background.
Since a pygame.Surface is automatically wrapped into a
:py:class:`surface_composition.Surface` object, it can be used like any other object.
Which means it will be centered in the available space, and scaled down if the
available space is smaller than the text, but not scaled up otherwise.
You can wrap it explicitly in a :py:class:`surface_composition.Surface` to
change scaling and positioning behavior.

Text takes a pygame.Font as second argument, which can also be used to set the
size, and modifiers i.e. bold and italic.
Also Text supports multi-line texts which will be aligned according to the
align-parameter.
To load a font, the :py:func:`Font` function can be used. If called without
parameters, e.g. 

.. code-block:: python

    Text("Hello\nWordl!", Font())

It will use the default system font with size=20 and without any modifiers.
Usually most text within a paradigm uses the same font settings, therefore it's
recommended to define a function with according parameters. e.g.

.. code-block:: python

    instruction_text = lambda s: Text(s, Font("arial", bold=True, size=30))

A tip for performance
~~~~~~~~~~~~~~~~~~~~~
Commonly a paradigm is composed of a hand full of screens, which are always the
same except for the current information. E.g in the
:ref:`IteCh example<examples_itech>` there is a function make_offer() which will
create the offer screen, and takes the details of the offer as arguments.
If it can happen, that such a function is called multiple times with the same
arguments, it is recommended to use
`functools.lru_cache <https://docs.python.org/3/library/functools.html#functools.lru_cache>`_
as annotator. This way the screen will only be computed once for every unique
parameter combination, and after the first call the result will be returned from
cache, which lowers computation time.

The reason this was not done in the :ref:`IteCh example<examples_itech>` was,
that :py:func:`make_offer` was never called twice for a unique parameter combination.


Reacting to user input
----------------------
For input :doc:`eventlistener` is used.
Which handles the corresponding pygame events. When the user presses a key, a
pygame.Event is generated and added to the event queue. The
:py:class:`EventListener`'s :py:func:`listen` method will query all 
pending events from the event-queue and process them according to
handler-functions. It has already three methods that should suffice for most
needs:

* :py:func:`wait_for_n_keypresses` which will return once a specified key was
    pressed n times.
* :py:func:`wait_for_keys` which will return once one of a list of given keys
    was pressed, and return the pressed key. It also supports a timeout; when the
    timeout is reached without a user pressing one of the keys, ``None`` is
    returned.
* :py:func:`wait_for_seconds`. Will return after n seconds. Use this method
    instead of :py:func:`time.sleep`, so events will be processed in the mean time.

I recommend taking a look at the implementation of these 3 methods, to see how
to use the :py:func:`listen`-method to implement your own handlers. The source
can be viewed from the :doc:`module documentation page <eventlistener>`, there
you can also find in-depth explanations on how to use the EventListener class.


The Misc-Module
---------------
The misc module contains everything that was handy enough to be part of
PyParadigm, but was not big enough for its own module.
It contains the following functions:

* :py:func:`init` which needs to be called before any other call to a member of
    PyParadgim, and creates the pygame window in which the contents will be displayed.
* :py:func:`display` which can be used to conveniently display a pygame surface
    that has the size of the pygame window.
* :py:func:`slide_show` which takes a list of pygame.Surfaces which are supposed
    to have the same size as the display window, and a handler function, that is
    supposed to return once the next slide should be shown. Handy to display
    multi-page text.
* :py:func:`empty_surface` which creates a new pygame.Surface of the given size
    (or of the size of the pygame window, if no size was specified), and
    automatically fills it with a given background color.

Next Step
---------
The next step now would be to take a look the :doc:`the examples <examples>` to
see how to apply what you just learned.


