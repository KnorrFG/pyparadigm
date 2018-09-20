.. PyParadigm documentation master file, created by
   sphinx-quickstart on Fri Sep  7 11:49:50 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyParadigm
=====================

PyParadigm is a small set of classes and functions designed to make it easy to
write psychological paradigms in Python.

"Why another presentation software?" You may ask. There is already a lot of
software, like E-Prime, Presentation, or Matlab. But since you are reading
the documentation of a Python library, I assume you already decided to use freely
available, non-commercial options. Of course there is still PsychoPy, but it
was never ported to Python3. 

PyParadigm takes another approach. It does not force you to use a mouse to drag
and drop a paradigm together and struggle with some details that might not have
been forseen by the developers. Paradigms usually are just a sequence of screens
combined with some user-interaction, which will generate some data that
needs to be stored afterwards. Python allows you to manipulate the screen in any
thinkable way and process keyboard and mouse input arbitrarily through the great
`PyGame library <https://www.pygame.org/news>`_. But while PyGame is great, it
requires a lot of code to write a paradigm, mostly because it is designed to
write programs that are much more complex than paradigms (i.e. video games).
And this is where PyParadigm comes in. It reduces the amount of required code to
a minimum. 
To wet your appetite, I will present a short script that implements a simple
inter temporal choice task, where the subject chooses between 2 offers with the
left or the right arrow-key, and gets a short feedback. The decisions, including
delay and amount, will be stored in a json-file.

The screens looks like this:

.. figure:: image/itech_offer.png
   :scale: 50 %
   :alt: Offer Presentation

Now the subject has to choose an option through a button press, in this case she/he
chooses the right option.

.. figure:: image/itech_feedback.png
   :scale: 50 %
   :alt: Feedback

And this is the script:

.. literalinclude:: ../examples/itech.py
   :language: python
   :linenos:

The next step now would be to read the :doc:`tutorial</tutorial>`

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    tutorial
    examples
    surfacecomposition
    eventlistener
    misc
