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
In the simplest option to create a window is nothing but a call to the
:py:func:`init` function of the :doc:`Misc-Module <misc>`, which only takes
one parameter: a 2-tuple with the prefered resolution. E.g. ``init((800,
600))``. However, most of the time, this is not exactly what you want. 
Usually you want to create a full-screen or borderless window (which looks like
fullscreen, if it has the size of the screen, but behaves a little different).
For these scenarios, you can use the pygame_flags argument. 
One of the things that :py:func:`init` does is calling
`pygame.display.set_mode()
<https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode>`_, which
is the pygame function that creates the window, and the flags argument is passed
through. Here, a short list of flags you will care about the most:

* ``pygame.FULLSCREEN`` which will create a full-screen window.
* ``pygame.NOFRAME`` which creates a window without window-frame. This looks
    like fullscreen if the created window has the same resolution as the desktop
    and is placed at (0, 0).

By default, the CPU will be used to render the images. This should suffice for
most paradigms. If, however, your paradigm is computationally very intensive and
requires a GPU you could use pygame.HWSURFACE, usually in combination with
pygame.DOUBLEBUF and pygame.FULLSCREEN, you can combine multiple flags with the
``|`` operator. E.g:

.. code-block:: python

    init((1920, 1080), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

A warning: Creating a hardware accelerated window in other systems than Windows 
can be problematic.
Now we can worry about how to fill this screen.

.. _creating_surfaces:

Creating Surfaces
-----------------
An important concept here is to avoid worrying about absolute positions. Using
:py:func:`compose`, an image-structure can be described as a tree of elements.
E.g.:

.. code-block:: python

    image = compose(target_surface)(
        LinLayout("h")(
            Circle(0xFF0000, width=1),
            Circle(0x00FF00, width=1)
        )
    )

Here, the available space (which is the size of ``target_surface``) is divided
horizontally (``"h"``) into 2 parts of equal size. Generally, the space is
equally divided between the children if not explicitly modified. Then, a red
circle will be drawn into the left area and a blue one in the right area. The
trees can get arbitrarily complex, and I recommend to take a look at the
:doc:`examples<examples>`

Here is a list of the different elements that can be used within
:py:func:`compose`

* Containers with multiple children: 
    * :py:class:`LinLayout` arranges items in a horizontal or vertical line
    * :py:func:`GridLayout` arranges items in a grid
    * :py:class:`Overlay` draws its children on top of each other
* Wrappers, which take a single child:
    * :py:class:`Padding` creates a padding around its child 
    * :py:class:`LLItem` is only usable within a :py:class:`LinLayout` and defines
        proportions of items within a :py:class:`LinLayout`
    * :py:class:`Surface` wraps pygame.Surfaces.
        E.g. loaded stimuli from files or texts, which are also generated as
        Surfaces. All pygame.Surfaces in a tree are wrapped in
        :py:class:`Surface` objects automatically. It can also be done manually
        to change placement or scaling options.
    * :py:class:`RectangleShaper` is closely related to :py:class:`Padding`. It
        will create horizontal or vertical padding to create a child-shape with a
        desired aspect ratio.
    * :py:class:`Fill` fills the assigned area with a given color before
        rendering its child. Can also be used without child.
    * :py:class:`Border` creates a border around its area. Can also be used
        without child.
* Primitives that don't take any children:
    * :py:class:`Circle` draws a circle in the assigned area
    * :py:func:`Cross` draws a cross within the assigned area
    * :py:class:`Line` draws a line within the assigned area
    * :py:func:`Text` creates a pygame.Surface containing the passed text. The
        text can be multi-line, left-/ or right-aligned or centered. It takes a
        pygame.Font as additional argument.

Children are generally passed via the :py:func:`__call__` operator of the
object. E.g. ``LinLayout("h")(child1, child2, child3)`` Whenever something only
takes a single child, the child can be a container. This way, it is possible to
add multiple children whenever only one child is allowed. :py:func:`compose`
itself allows only one child, which gets the whole image as target area. But
since a lot of :py:func:`compose` calls would have a container as its child,
:py:func:`compose` allows a second argument, which can be any component that
takes at least one child (except for Surface). The above example could also be
written like this:
    
.. code-block:: python

    image = compose(target_surface, LinLayout("h"))(
            Circle(0xFF0000),
            Circle(0x00FF00)
    )

The first argument to :py:func:`compose` can either be a pygame.Surface to
render on (like above) or a 2-tuple with width and height. In the second case, a
new pygame.Surface with the specified dimensions would be created. To get a desired
background color for the newly created surface the root component should be a
:py:class:`Fill` object.

The most common case though would be

.. code-block:: python

    image = compose(empty_surface(color), LinLayout("h"))(
            Circle(0xFF0000),
            Circle(0x00FF00)
    )

:py:func:`empty_surface` is part of the :doc:`Misc-Module <misc>` and will
create a new pygame.Surface which is automatically filled with the given color.
A size for the new surface can be specified as second argument. If the size
argument is omitted, the created pygame.Surface will automatically have the size of the
display.

To display saved images, use :py:func:`pygame.image.load` and just use the
loaded pygame.Surface in compose.

Creating Text
~~~~~~~~~~~~~
:py:func:`Text` is not an object with a :py:meth:`_draw`-method but a function that returns
a pygame.Surface, which contains the text on a transparent background.
Since a pygame.Surface is automatically wrapped into a
:py:class:`surface_composition.Surface` object, it can be used like any other object.
This means that it will be centered in the available space and scaled down if the
available space is smaller than the text, but not scaled up otherwise.
You can wrap it explicitly in a :py:class:`surface_composition.Surface` to
change scaling and positioning behavior.

:py:func:`Text` takes a pygame.Font as second argument, which can also be used to set the
size, and modifiers i.e. bold and italic.
Also Text supports multi-line texts which will be aligned according to the
align-parameter.
To load a font, the :py:func:`Font` function can be used. If called without
parameters, it will use the default system font with size=20 and without any modifiers, e.g.: 

.. code-block:: python

    Text("Hello\nWordl!", Font())


Usually most text within a paradigm uses the same font settings. Therefore, it's
recommended to define a function with according parameters. e.g.:

.. code-block:: python

    instruction_text = lambda s: Text(s, Font("arial", bold=True, size=30))

A tip for performance
~~~~~~~~~~~~~~~~~~~~~
Commonly, a paradigm is composed of a hand full of screens, which are the
same except for the specific content. E.g in the
:ref:`IteCh example<examples_itech>`, there is a function ``make_offer()`` that will
create the offer screen and takes the details of the offer as arguments.
If such a function is called multiple times with the same
arguments, it is recommended to use
`functools.lru_cache <https://docs.python.org/3/library/functools.html#functools.lru_cache>`_
as annotator. In this way, the screen will only be computed once for every unique
parameter combination, and, after the first call, the result will be returned from
cache, which lowers computation time.

The reason this was not done in the :ref:`IteCh example<examples_itech>` was 
that ``make_offer()`` was never called twice for a unique parameter combination.


Reacting to user input
---------------------- 

For input :doc:`eventlistener` is
used, which handles the corresponding pygame events. When the user presses a
key, a pygame.Event is generated and added to the event queue. The
:py:class:`EventListener`'s :py:func:`listen` method will query all pending
events from the event-queue and process them according to handler-functions. It
has already three methods that should suffice for most needs:

* :py:func:`wait_for_n_keypresses` will return if a specified key was
    pressed n times.
* :py:func:`wait_for_keys` will return if one of the given keys
    was pressed and return the pressed key. It also supports a timeout; when the
    timeout is reached without a user pressing one of the keys, ``None`` is
    returned.
* :py:func:`wait_for_seconds` will return after n seconds. Use this method
    instead of ``time.sleep()``, so events will be processed in the meantime.

I recommend taking a look at the implementation of these 3 methods to see how
to use the :py:func:`listen`-method to implement your own handlers. The source
can be viewed from the :doc:`module documentation page <eventlistener>`. There,
you can also find in-depth explanations on how to use the EventListener class.


The Misc-Module
---------------
The Misc-Module contains everything that was handy enough to be part of
PyParadigm, but was not big enough for its own module.
It contains the following functions:

* :py:func:`init` needs to be called before any other call to a member of
    PyParadgim and creates the pygame window in which the contents will be displayed.
* :py:func:`display` can be used to conveniently display a pygame surface, 
    which has the size of the pygame window.
* :py:func:`slide_show` takes a list of pygame.Surfaces, which are supposed
    to have the same size as the display window, and a handler function. When
    the handler function returns, the next slide is shown. Handy to display
    multi-page text.
* :py:func:`empty_surface` creates a new pygame.Surface of the given size
    (or of the size of the pygame window, if no size was specified) and
    automatically fills it with a given background color.

Next Step
---------
The next step now would be to take a look the :doc:`the examples <examples>` to
see how to apply what you just learned.


