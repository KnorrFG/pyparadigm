""" This script contains an example implementation of the stroop task. 

The easiest way to understand this code is to start reading in the main
function, and then read every function when it's called first
"""

import random
import time
import csv
from collections import namedtuple
from enum import Enum
from functools import lru_cache
from itertools import islice, repeat

import pygame

from pyparadigm import (EventListener, Fill, Font, LinLayout, LLItem, Padding,
                        RectangleShaper, Surface, Text, compose, display,
                        empty_surface, init, slide_show)

# ================================================================================
# Just Configuration
# ================================================================================
n_train_1_trials = 30
n_train_2_trials = 10
trials_per_block = 10
intro_text = ["""
Welcome to the Stroop-demo.
In this task you will be presented with words naming colors
which are written in a colored font.
You will either have to indicate the name of the color, or the
color of the font, using the arrow keys.

Press Return to continue.
""",
"""
To indicate the color you will have to use the number keys,

1 for red
2 for green
3 for blue

press Return to continue
""",
"""
First you will learn the mappings by heart.
To do so you will be displayed with the mappings, after %d trials
the mappings won't be shown any more. Then after %d
correct trials, the main task will start.
""" % (n_train_1_trials, n_train_2_trials)]


pre_hidden_training_text = """
Now we will hide the mapping, and the task will continue until you answered
correctly %d times.

Press Return to continue""" % n_train_2_trials


post_hidden_training_text = """
The training was succesful.

Press Return to continue"""


pre_text_block_text = """
Now, we begin with the test. Please indicate the color 
that is named by the letters

Press Return to continue
"""


post_test_block_text = """
Now, please indicate the color in which 
the word is written

Press Return to continue
"""


end_text = """
The task is complete, thank you for your participation
Press Return to escape
"""

# ================================================================================
# some utility functions
# ================================================================================

@lru_cache()
def text(s: str, color=0):
    # This is our configuration of how to display text, with the arial font, and
    # a pointsize of 30.
    # Due to the way text is plotted it needs the information of an alphachannel
    # therefore it is not possible to simply pass the hex-code of the color, but it 
    # is necessary to create a pygame.Color object. For which, again, it is necessary
    # to multiply the hex code with 0x100 to respect the alphachannel
    return Text(s, Font("Arial", size=30), color=pygame.Color(color * 0x100))


def _bg():
    # short for background
    return empty_surface(0xFFFFFF)


def display_text(s:str):
    display(compose(_bg())(text(s)))


def display_text_and_wait(s: str, el: EventListener, key: int = pygame.K_RETURN):
    display_text(s)
    el.wait_for_keys(key)


# ================================================================================
# Main Program
# ================================================================================
class Color(Enum):
    red = 0xFF0000
    green = 0x00FF00
    blue = 0x0000FF


colors = list(Color)


key_color_mapping = {
    eval("pygame.K_%d" % (i + 1)): color
    for i, color in enumerate(Color)
}


def display_intro(el: EventListener):
    # the first argument for slide_show must be an iterable of pygame.Surface
    # to create it we render the text onto an empty surface with the map()
    # function. slide_show displays one slide, and then calls the function that
    # is passed to it as second argument. When this function returns, the next
    # slide is displayed and the function is called again. The function that is 
    # passed simply waits for the return key
    slides = map(lambda s: compose(_bg())(text(s)), intro_text)
    slide_show(slides, lambda: el.wait_for_keys(pygame.K_RETURN))


@lru_cache()
def make_train_stim(type: str, color: Color):
    # encapsulates the creation of a training stim. Either a square of the given
    # or the name of the color as text, they are wrapped by a RectangleShaper, 
    # by default, will create a square
    assert type in ["color", "text"]
    return RectangleShaper()(
        text(color.name) if type == "text" else Fill(color.value))


def make_color_mapping():
    # The mapping is a horizontal layout consisting of groups of
    # a text element describing the key, and a square containing the color
    # we use make_train_stim() to create the square, and add a LLItem(1) in
    # the back and the front to get visible gaps between the groups.
    # The * in from of the list is used to expand the list to the arguments
    # for the LinLayouts inner function.
    return LinLayout("h")(*[LinLayout("h")(LLItem(1), text(str(key + 1)),
                                           make_train_stim("color", color), LLItem(1))
                            for key, color in enumerate(Color)])


@lru_cache()
def render_train_screen(show_mapping, stim_type, target_color):
    # the contents are aranged in a vertical layout, topmost is the
    # title "target color", followed by the stim for training (either a
    # square containing the color, or the word naming the color)
    # in the Bottom there is the information which key is mapped to which
    # color. But its only displayed optionally

    return compose(_bg(), LinLayout("v"))(
        # Create the Text
        text("target color:"),

        # Create the stimulus, and scale it down a little.
        Padding.from_scale(0.3)(make_train_stim(stim_type, target_color)),

        # Up till here the content is static, but displaying the mapping is optionally
        # and depends on the parameter, therefore we either add the mapping, or
        # an LLItem(1) as placeholder
        make_color_mapping() if show_mapping else LLItem(1)
    )


def do_train_trial(event_listener: EventListener, show_mapping: bool, stim_type:
                   str, target_color: Color):
    # displays a training_screen
    display(render_train_screen(show_mapping, stim_type, target_color))

    # waits for a response
    response_key = event_listener.wait_for_keys(key_color_mapping)

    # returns whether the response was correct
    return key_color_mapping[response_key] == target_color


def rand_elem(seq, n=None):
    """returns a random element from seq n times. If n is None, it continues indefinitly"""
    return map(random.choice, repeat(seq, n) if n is not None else repeat(seq))


def until_n_correct(n, func):
    n_correct = 0
    while n_correct < n:
        if func():
            n_correct += 1
        else:
            n_correct = 0


def do_training(el: EventListener):
    arguments = zip(rand_elem(["text", "color"]), rand_elem(colors))
    for stim_type, color in islice(arguments, n_train_1_trials):
        do_train_trial(el, True, stim_type, color)

    display_text_and_wait(pre_hidden_training_text, el)
    until_n_correct(n_train_2_trials, lambda: do_train_trial(el, False, *next(arguments)))    
    display_text_and_wait(post_hidden_training_text, el)


@lru_cache()
def render_trial_screen(word, font_color, target):
    return compose(_bg(), LinLayout("v"))(
        # Create the Text
        text("Which color is named by the letters?" if target == "text"
             else "What's the color of the word?"),

        # Create the stimulus, and scale it down a little.
        Padding.from_scale(0.3)(text(word, font_color)),
        LLItem(1)
    )


BlockResult = namedtuple("BlockResult", "RT word font_color response was_correct")


def run_block(event_listener: EventListener, by: str, n_trials: int)-> BlockResult:
    assert by in ["text", "color"]
    RTs = []; words = []; fonts = []; responses = []; was_correct = []
    for word, font in zip(rand_elem(colors, n_trials), rand_elem(colors)):
        words.append(word)
        fonts.append(font)
        display(render_trial_screen(word.name, font.value, by))

        # We use this to record reaction times
        start = time.time()
        response_key = event_listener.wait_for_keys(key_color_mapping)

        # Now the reaction time is just now - then
        RTs.append(time.time() - start)
        response = key_color_mapping[response_key] 
        responses.append(response)
        was_correct.append(response == (word if by == "text" else font))
    
    return BlockResult(RTs, words, fonts, responses, was_correct)


def save_results(text_res: BlockResult, font_res: BlockResult):
    with open("results.tsv", "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(("by",) + BlockResult._fields)
        for line in zip(*text_res):
            writer.writerow(("text",) + line)
        for line in zip(*font_res):
            writer.writerow(("font",) + line)


def main():
    # create the pygame window. It has a resolution of 1024 x 800 pixels
    init((1024, 800))

    # create an event listener that will be used through the whole program
    event_listener = EventListener()
    display_intro(event_listener)
    do_training(event_listener)
    
    display_text_and_wait(pre_text_block_text, event_listener)
    text_block_results = run_block(event_listener, by="text",
                                   n_trials=trials_per_block)
    display_text_and_wait(post_test_block_text, event_listener)
    color_block_results = run_block(event_listener, by="color",
                                    n_trials=trials_per_block)
    display_text_and_wait(end_text, event_listener)

    save_results(text_block_results, color_block_results)


if __name__ == "__main__":
    main()
