"""Create pygame-surfaces in a declarative way

The purpose of this module is to make it easy to compose the 
frames that are displayed in a paradigm.

When you use simple pygame to write a paradigm, you will spend a lot 
of time writing code to compute the positions of the elemnts the surface
is composed of. This module addresses this time-sink by offering a way to 
define these postions in a declarative way. E.g. the code

.. code-block:: python

    frame = compose(screen.get_size(), LinLayout("h"))(
        LLItem(2)(red_ball),
        LinLayout("v")(
            green_ball,
            Surface(scale=0.1)(green_ball), 
            green_ball),
        red_ball
    )

will create the following screen:

.. figure:: ../../doc/source/image/example_screen.png
   :scale: 50 %
   :alt: example

Of course there is code missing to create the balls and display 
the surface on screen.

The system works by returning context-objects, which all implement a
draw-method. This basically creates a scene tree, where the 
leave-objects, and handle the actual drawing. The Layouts just call draw on
their children with the correct rectangles
"""
from functools import reduce, wraps
from operator import add

import pygame
from fields import Fields, Tuple
from toolz import compose as t_compose
from toolz import  pipe, accumulate
from toolz.curried import do, map

_lmap = t_compose(list, map)
_dp = do(print)
_wrap_surface = lambda elem:\
     Surface()(elem) if type(elem) == pygame.Surface else elem

def _inner_func_anot(func):
    """must be applied to all inner functions that return contexts.
    
    Wraps all instances of pygame.Surface in the input in Surface"""
    @wraps(func)
    def new_func(*args):
        return func(*_lmap(_wrap_surface, args))
    return new_func


class _LinLayoutContext(Tuple.orientation.children):
    def draw(self, surface, target_rect):
        child_rects = self.compute_child_rects(target_rect)
        for child, rect in zip(self.children, child_rects):
            child.item.draw(surface, rect)

    def compute_child_rects(self, target_rect):
        flip_if_not_horizontal = lambda t: \
            t if self.orientation == "h" else (t[1], t[0])
        target_rect_size = target_rect.size
        divider, full = flip_if_not_horizontal(target_rect_size) 
        dyn_size_per_unit = divider / sum(child.relative_size for child in self.children)
        strides = [child.relative_size * dyn_size_per_unit for child in self.children]
        dyn_offsets = [0] + list(accumulate(add, strides))[:-1]
        left_offsets, top_offsets = flip_if_not_horizontal((dyn_offsets, 
                                                            [0] * len(self.children)))
        widths, heights = flip_if_not_horizontal((strides, [full] * len(self.children)))

        return [pygame.Rect(target_rect.left + left_offset, 
                            target_rect.top + top_offset,
                            w, h)
                for left_offset, top_offset, w, h in 
                    zip(left_offsets, top_offsets, widths, heights)]


class _SurfaceContext(Tuple.child.margin.scale.smooth):
    @staticmethod
    def scale_to_target(source, target_rect, smooth=False):
        target_size = source.get_rect().fit(target_rect).size
        return pygame.transform.scale(source, target_size) \
            if not smooth else pygame.transform.smoothscale(source, target_size) 
            
    def determine_target_size(child, target_rect, scale):
        if scale > 0:
            return tuple(dist * scale for dist in target_rect.size)
        elif all(s_dim <= t_dim 
                for s_dim, t_dim in zip(child.get_size(), target_rect.size)):
            return 0
        else:
            return target_rect.size
        
    def draw(self, surface, target_rect):
        if self.child is None:
            return
        target_size = _SurfaceContext.determine_target_size(self.child, target_rect, 
                                                        self.scale)
        content = _SurfaceContext.scale_to_target(self.child, (0, 0, *target_size), 
                                            self.smooth)\
                if target_size else self.child
        remaining_h_space = target_rect.w - content.get_rect().w
        remaining_v_space = target_rect.h - content.get_rect().h
        offset_by_margins = lambda space, one, two: space * one / (one + two)
        surface.blit(content, (
            target_rect.left + offset_by_margins(remaining_h_space,
                self.margin.left, self.margin.right),
            target_rect.top + offset_by_margins(remaining_v_space,
                self.margin.top, self.margin.bottom)))


class _PaddingContext(Tuple.child.left.right.top.bottom):
    def draw(self, surface, target_rect):
        child_rect = pygame.Rect(
            target_rect.left + target_rect.w * self.left,
            target_rect.top + target_rect.h * self.top,
            target_rect.w * (1 - self.left - self.right),
            target_rect.h * (1 - self.top - self.bottom)
        )
        self.child.draw(surface, child_rect)
            

class _LLItem(Tuple.item.relative_size[1]): 
    """Wrapper around items in layout, which stores the associated relative size"""
    pass


class Margin(Tuple.left[1].right[1].top[1].bottom[1]): 
    """Defines the relative position of an item within a box, for details see Surface."""
    pass


def compose(target, root=None):
    """Top level function to create a surface.
    
    :param target: the pygame.Surface to blit on. Or a (width, height) tuple
        in which case a new surface will be created

    :type target: -
    """
    @_inner_func_anot
    def inner_compose(*children):
        if root:
            root_context = root(*children)
        else:
            assert len(children) == 1
            root_context = children[0]

        if type(target) == pygame.Surface:
            surface = target
            size = target.get_size()
        else:
            size = target
            surface = pygame.Surface(size)

        root_context.draw(surface, pygame.Rect(0, 0, *size))
        return surface
    return inner_compose


def LinLayout(orientation):
    """A linear layout to order items horizontally or vertically.
    
    Every element in the layout is automatically wrapped within a LLItem with
    relative_size=1, i.e. all elements get assigned an equal amount of space, to
    change that elements can be wrappend in LLItems manually to get desired
    proportions 
    
    :param orientation: orientation of the layout, either 'v' for vertica, or
        'h' for horizontal.
    
    :type orientation: str
    """
    assert orientation in ["v", "h"]
    @_inner_func_anot
    def inner_layout(*children):
        return _LinLayoutContext(orientation, _lmap(
            lambda child: 
                child if type(child) == _LLItem else _LLItem(child), 
            children))
    return inner_layout


def Surface(margin=Margin(1, 1, 1, 1), scale=0, smooth=True):
    """Wraps a pygame surface.

    The Surface is the connection between the absolute world of pygame.Surfaces and the
    relative world of the composition functions. A pygame.Surfaces can be bigger than
    the space that is available to the Surface, or smaller. The Surface does the actual
    blitting, and determines the concrete position, and if necessary (or
    desired) scales the input surface.

    :param margin: used to determine the exact location of the pygame.Surfaces within 
        the available space. The margin value represents the proportion of 
        the free space, along
        an axis, i.e. Margin(1, 1, 1, 1) is centered, Margin(0, 1, 1, 2) is as far
        left as possible and one/third on the way down.

    :type margin: Margin object

    :param scale: If 0 < scale <= 1 the longer side of the surface is scaled to 
        to the given fraction of the available space, the aspect ratio is 
        will be preserved.
        If scale is 0 the will be no scaling if the image is smaller than the
        available space. It will still be scaled down if it is too big. 

    :type scale: float

    :param smooth: if True the result of the scaling will be smoothed

    :type smooth: float
   """
    assert 0 <= scale <= 1
    return lambda child=None: _SurfaceContext(child, margin, scale, smooth)


def LLItem(relative_size):
    """Defines the relative size of an element in a LinLayout

    All Elements that are passed to a linear layout are automatically wrapped
    into an LLItem with relative_size=1. Therefore by default all elements
    within a layout will be of the same size. To change the proportions a LLItem
    can be used explicitely with another relative size"""
    return _inner_func_anot(lambda child: _LLItem(child, relative_size))


def Padding(left, right, top, bottom):
    """Pads a child element

    Each argument refers to a percentage of the axis it belongs to.
    A padding of (0.25, 0.25, 0.25) would generate blocked area a quater of the
    available height in size above and below the child, and a quarter of the 
    available width left and right of the child.

    If left and right or top and bottom sum up to one that would mean no space
    for the child is remaining
    """
    assert all(0 <= side < 1 for side in [left, right, top, bottom])
    assert left + right < 1
    assert top + bottom < 1
    return _inner_func_anot(lambda child: 
        _PaddingContext(child, left, right, top, bottom))


def Circle(color, width=0):
    """Draws a Circle in the assigned space.
    
    The circle will always be centered, and the radius will be half of the
    shorter side of the assigned space.
    
    :param color: The color of the circle
    
    :type color: pygame.Color or int
    
    :param width: width of the circle (in pixels). If 0 the circle will be filled
    
    :type width: int
    """
    class _CircleBrush:
        @staticmethod
        def draw(surface, target_rect):
            pygame.draw.circle(surface, color, target_rect.center, 
                int(round(min(target_rect.w, target_rect.h) * 0.5)), width)
    return _CircleBrush     


def Fill(color):
    """Fills the assigned area. Afterwards, the children are rendered

    :param color: the color with which the area is filled

    :type color: pygame.Color or int
    """
    class _FillContext(Tuple.child.color):
        def draw(self, surface, target_rect):
            surface.fill(self.color, target_rect)
            self.child.draw(surface, target_rect)
    return _inner_func_anot(lambda child: _FillContext(child, color))


def Overlay():
    """Draws all its children on top of each other in the same rect"""
    class _OverlayContext(Tuple.dummy.children):
        def draw(self, surface, target_rect):
            for child in self.children:
                child.draw(surface, target_rect)
    return _inner_func_anot(lambda *children: _OverlayContext(None, children))

