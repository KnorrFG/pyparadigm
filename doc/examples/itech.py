import pygame
from pyparadigm.surface_composition import *
from pyparadigm.misc import empty_surface, display, init
from pyparadigm.eventlistener import EventListener

import json
import time

# Scroll to the bottom, and start reading in the main() ;)

def offer_box(title, amount):
    # Creates a border around a vertical layout containing 2 cells, where the
    # lower one has twice the size of the upper one (layout children are
    # automatically wrapped in LLItems with relative_size=1). Both Boxes are
    # filled with text, wich is centered in its parent area.
    return Border()(
            LinLayout("v")(
                Text(title, Font(size=50)),
                LLItem(2)(Text(f"{amount}€", Font(size=50, bold=True)))
            )
        )


def make_offer(now, later, delay):
    # Create pygame.Surface with a white background.
    # The LinLayout splits the available space into (in this case)
    # equally sized horizontally aligned parts. 80% of the available
    # space of each part is used to display a offer box.
    return compose(empty_surface(0xFFFFFF), LinLayout("h"))(
        Padding.from_scale(0.8)(offer_box("Now", now)),
        Padding.from_scale(0.8)(offer_box(f"In {delay} days", later)),
    )


def make_feedback(amount, delay):
    # creates a pygame.Surface which only contains the text message
    msg = f"{amount}€ " + ("now" if delay == 0 else f"in {delay} days")
    return compose(empty_surface(0xFFFFFF))(Text(msg, Font(size=50)))


def main():
    # initiate a window with a resolution of 800 x 600 pixels
    init((800, 600))
    # alternatively, to create a full screen, hardware accelrated window, you
    # could use:
    # init((1920, 1080), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

    # Create an Eventlistener object
    event_listener = EventListener()

    # Initiate the data for the paradigm, and create 2 lists to store
    # the results
    immediate_offers = ([10] * 3) + ([20] * 3) + ([30] * 3)
    delays = [10, 20, 30] * 3
    delayed_offers = [delay + im_offer
        for delay, im_offer in zip(delays, immediate_offers)]
    chosen_amounts = []
    chosen_delays = []
    reaction_times = []

    # Execute the paradigm
    for im_offer, del_offer, delay in zip(immediate_offers, delayed_offers, delays):
        # display the offer
        display(make_offer(im_offer, del_offer, delay))
        offer_onset = time.time()

        # wait for a decision in form of the left or right arrow-key
        key = event_listener.wait_for_keys([pygame.K_LEFT, pygame.K_RIGHT])
        # calculate reaction time and save it
        reaction_times.append(time.time() - offer_onset)

        # store results according to decision
        if key == pygame.K_LEFT:
            chosen_amounts.append(im_offer)
            chosen_delays.append(0)
        else:
            chosen_amounts.append(del_offer)
            chosen_delays.append(delay)

        # display a feedback for 2 seconds
        display(make_feedback(chosen_amounts[-1], chosen_delays[-1]))
        event_listener.wait_for_seconds(2)

    # save results to a json File
    with open("results.json", "w") as file:
        json.dump({"amount": chosen_amounts, "delay": chosen_delays,
                   "reaction_times": reaction_times}, file)


if __name__ == '__main__':
    main()
