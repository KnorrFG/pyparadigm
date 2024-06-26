"""Easy Image Composition

The purpose of this module is to make it easy to compose the 
frames that are displayed in a paradigm. For an introduction, please refer to
the :ref:`tutorial<creating_surfaces>`
"""
from functools import wraps, lru_cache
from itertools import accumulate, chain

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    import pygame.ftfont

from ._primitives import PPError

_lmap = wraps(map)(lambda *args, **kwargs:list(map(*args, **kwargs)))

def _wrap_surface(elem):
    return Surface()(elem) if type(elem) == pygame.Surface else elem
    
def _round_to_int(val): 
    return int(round(val))

def _call_function(elem):
    return elem() if callable(elem) else elem


def _inner_func_anot(func):
    """must be applied to all inner functions that return contexts.
    
    Wraps all instances of pygame.Surface in the input in Surface"""
    @wraps(func)
    def new_func(*args):
        return func(*_lmap(_wrap_surface, args))
    return new_func


def _wrap_children(children):
    try:
        return [_wrap_surface(c) for c in children]
    except TypeError:
        return _wrap_surface(children)


def _check_call_op(child): 
    if child is not None:
        raise RuntimeError("Call operator was called twice")


class LLItem: 
    """Defines the relative size of an element in a LinLayout

    All Elements that are passed to a linear layout are automatically wrapped
    into an LLItem with relative_size=1. Therefore by default all elements
    within a layout will be of the same size. To change the proportions a LLItem
    can be used explicitely with another relative size.
    
    It is also possible to use an LLItem as placeholde in a layout, to generate
    an empty space like this:
    
    :Example:

    LinLayout("h")(
        LLItem(1),
        LLItem(1)(Circle(0xFFFF00)))
    """
    def __init__(self, relative_size):
        self.child = Surface()
        self.relative_size = relative_size

    def __call__(self, child):
        if child:
            self.child = _wrap_surface(child)
        return self

    def __repr__(self):
        return "LLItem({})({})".format(self.relative_size, repr(self.child))

class LinLayout:
    """A linear layout to order items horizontally or vertically.
    
    Every element in the layout is automatically wrapped within a LLItem with
    relative_size=1, i.e. all elements get assigned an equal amount of space, to
    change that elements can be wrappend in LLItems manually to get desired
    proportions 
    
    :param orientation: orientation of the layout, either 'v' for vertica, or
        'h' for horizontal.
    
    :type orientation: str
    """
    def __init__(self, orientation):
        assert orientation in ["v", "h"]
        self.orientation = orientation
        self.children = None


    def __call__(self, *children):
        if len(children) == 0:
            raise PPError("You tried to add no children to layout")

        _check_call_op(self.children)
        self.children = _lmap(lambda child: 
                                child if type(child) == LLItem else LLItem(1)(child), 
                              _wrap_children(children))
        return self

    def _draw(self, surface, target_rect):
        child_rects = self._compute_child_rects(target_rect)
        for child, rect in zip(self.children, child_rects):
            child.child._draw(surface, rect)

    def _compute_child_rects(self, target_rect):
        def flip_if_not_horizontal(t): 
            return t if self.orientation == "h" else (t[1], t[0])

        target_rect_size = target_rect.size
        sum_child_weights = sum(child.relative_size for child in self.children)
        if sum_child_weights == 0:
            raise PPError("LinLayout Children all have weight 0: " + repr(self.children))
        divider, full = flip_if_not_horizontal(target_rect_size) 
        dyn_size_per_unit = divider / sum_child_weights
        strides = [child.relative_size * dyn_size_per_unit for child in self.children]
        dyn_offsets = [0] + list(accumulate(strides))[:-1]
        left_offsets, top_offsets = flip_if_not_horizontal((dyn_offsets, 
                                                            [0] * len(self.children)))
        widths, heights = flip_if_not_horizontal((strides, [full] * len(self.children)))

        return [pygame.Rect(target_rect.left + left_offset, 
                            target_rect.top + top_offset,
                            w, h)
                for left_offset, top_offset, w, h in 
                    zip(left_offsets, top_offsets, widths, heights)]

class FRect:
    """A wrapper Item for children of the FreeFloatLayout, see description of FreeFloatLayout"""
    def __init__(self, x, y, w, h):
        for coord in (x, y, w, h):
            assert FRect.coord_valid(coord)

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.child = None

    @staticmethod
    def coord_valid(x):
        return type(x) is int or (type(x) == float and 0 <= x <= 1) 

    @staticmethod
    def adjust_coord(x, abs_partner):
        if type(x) == int:
            if x >= 0:
                return x
            else:
                return abs_partner + x
        elif type(x) == float:
            return x * abs_partner

        # this code should never be reached
        assert False

    def to_abs_rect(self, target_rect):
        tmp = pygame.Rect(
            FRect.adjust_coord(self.x, target_rect.w),
            FRect.adjust_coord(self.y, target_rect.h),
            FRect.adjust_coord(self.w, target_rect.w),
            FRect.adjust_coord(self.h, target_rect.h))
        return tmp.move(target_rect.topleft)

    def __call__(self, child):
        if child:
            self.child = _wrap_surface(child)
        return self


class FreeFloatLayout:
    """A "Layout" that allows for free positioning of its elements. All children
    must be Wrapped in an FRect, which takes a rects arguments (x, y, w, h), and
    determines the childs rect. All values can either be floats, and must then
    be between 0 and 1 and are relative to the rect-size of the layout, positive
    integers, in which case the values are interpreded as pixel offsets from the
    layout rect origin, or negative integers, in which case the absolute value
    is the available width or height minus the value"""
    def __init__(self) -> None:
        self.children = None

    def __call__(self, *children):
        if len(children) == 0:
            raise PPError("You tried to add no children to layout")

        _check_call_op(self.children)
        for child in children:
            if type(child) != FRect:
                raise PPError("All children of a FreeFloatLayout must be wrapped in an FRect")
        self.children = children
        return self

    def _draw(self, surface, target_rect):
        for child in self.children:
            rect = child.to_abs_rect(target_rect)
            if child.child is None:
                raise ValueError("There is an FRect without child")
            child.child._draw(surface, rect)


class Margin: 
    """Defines the relative position of an item within a Surface. 
    For details see Surface.
    """
    __slots__ = ["left", "right", "top", "bottom"]
    def __init__(self, left=1, right=1, top=1, bottom=1):
        self.left=left
        self.right=right
        self.top=top
        self.bottom=bottom


def _offset_by_margins(space, one, two): 
    return space * one / (one + two)


class Surface:
    """Wraps a pygame surface.

    The Surface is the connection between the absolute world of pygame.Surfaces and the
    relative world of the composition functions. A pygame.Surfaces can be bigger than
    the space that is available to the Surface, or smaller. The Surface does the actual
    blitting, and determines the concrete position, and if necessary (or
    desired) scales the input surface.

    Warning: When images are scaled with smoothing, colors will change decently, which
    makes it inappropriate to use in combination with colorkeys.

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
    def __init__(self, margin=Margin(1, 1, 1, 1), scale=0, smooth=True,
                 keep_aspect_ratio=True):
        assert 0 <= scale <= 1
        self.child = None 
        self.margin = margin
        self.scale = scale
        self.smooth = smooth
        self.keep_aspect_ratio = keep_aspect_ratio
    
    def __call__(self, child):
        _check_call_op(self.child)
        self.child = child
        return self

    @staticmethod
    def _scale_to_target(source, target_size, smooth=False):
        return pygame.transform.scale(source, target_size) if not smooth\
             else pygame.transform.smoothscale(source, target_size) 
            
    @staticmethod
    def _determine_target_size(child, target_rect, scale, keep_aspect_ratio):
        if scale > 0:
            scaled_target_rect = tuple(dist * scale for dist in target_rect)
            if keep_aspect_ratio:
                return child.get_rect().fit(scaled_target_rect).size
            else:
                return scaled_target_rect[2:4]
        elif all(s_dim <= t_dim 
                for s_dim, t_dim in zip(child.get_size(), target_rect.size)):
            return child.get_size()
        else:
            return target_rect.size

    def compute_render_rect(self, target_rect):
        target_size = Surface._determine_target_size(
            self.child, target_rect, self.scale, self.keep_aspect_ratio)
        remaining_h_space = target_rect.w - target_size[0]
        remaining_v_space = target_rect.h - target_size[1]
        return pygame.Rect(
            (target_rect.left + _offset_by_margins(remaining_h_space,
                self.margin.left, self.margin.right),
            target_rect.top + _offset_by_margins(remaining_v_space,
                self.margin.top, self.margin.bottom)), target_size)
        
    def _draw(self, surface, target_rect):
        if self.child is None:
            return
        render_rect = self.compute_render_rect(target_rect)
        if render_rect.size == self.child.get_size():
            content = self.child
        else:
            content = Surface._scale_to_target(
                self.child, render_rect.size, self.smooth)

        surface.blit(content, render_rect)


class Padding:
    """Pads a child element

    Each argument refers to a percentage of the axis it belongs to.
    A padding of (0.25, 0.25, 0.25, 0.25) would generate blocked area a quater of the
    available height in size above and below the child, and a quarter of the 
    available width left and right of the child.

    If left and right or top and bottom sum up to one that would mean no space
    for the child is remaining
    """
    def _draw(self, surface, target_rect):
        assert self.child is not None

        child_rect = pygame.Rect(
            target_rect.left + target_rect.w * self.left,
            target_rect.top + target_rect.h * self.top,
            target_rect.w * (1 - self.left - self.right),
            target_rect.h * (1 - self.top - self.bottom)
        )
        self.child._draw(surface, child_rect)

    def __init__(self, left, right, top, bottom):
        assert all(0 <= side < 1 for side in [left, right, top, bottom])
        assert left + right < 1
        assert top + bottom < 1
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.child = None

    def __call__(self, child):
        _check_call_op(self.child)
        self.child = _wrap_surface(child)
        return self

    @staticmethod
    def from_scale(scale_w, scale_h=None):
        """Creates a padding by the remaining space after scaling the content.

        E.g. Padding.from_scale(0.5) would produce Padding(0.25, 0.25, 0.25, 0.25) and
        Padding.from_scale(0.5, 1) would produce Padding(0.25, 0.25, 0, 0)
        because the content would not be scaled (since scale_h=1) and therefore
        there would be no vertical padding.
        
        If scale_h is not specified scale_h=scale_w is used as default

        :param scale_w: horizontal scaling factors
        :type scale_w: float
        :param scale_h: vertical scaling factor
        :type scale_h: float
        """
        if not scale_h: scale_h = scale_w
        w_padding = [(1 - scale_w) * 0.5] * 2
        h_padding = [(1 - scale_h) * 0.5] * 2
        return Padding(*w_padding, *h_padding)


class RectangleShaper:
    """Creates a padding, defined by a target Shape.

    Width and height are the relative proportions of the target rectangle.
    E.g RectangleShaper(1, 1) would create a square. and RectangleShaper(2, 1)
    would create a rectangle which is twice as wide as it is high.
    The rectangle always has the maximal possible size within the parent area.
    """
    def __init__(self, width=1, height=1):
        self.child = None
        self.width = width
        self.height = height

    def __call__(self, child):
        _check_call_op(self.child)
        self.child = _wrap_surface(child)
        return self
        
    def _draw(self, surface, target_rect):
        parent_w_factor = target_rect.w / target_rect.h
        my_w_factor = self.width / self.height
        if parent_w_factor > my_w_factor:
            my_h = target_rect.h
            my_w = my_h * my_w_factor
            my_h_offset = 0
            my_w_offset = _round_to_int((target_rect.w - my_w) * 0.5)
        else:
            my_w = target_rect.w
            my_h = my_w / self.width * self.height
            my_w_offset = 0
            my_h_offset = _round_to_int((target_rect.h - my_h) * 0.5)
        self.child._draw(surface, pygame.Rect(
            target_rect.left + my_w_offset,
            target_rect.top + my_h_offset,
            my_w,
            my_h
        ))
        



class Circle:
    """Draws a Circle in the assigned space.
    
    The circle will always be centered, and the radius will be half of the
    shorter side of the assigned space.
    
    :param color: The color of the circle
    
    :type color: pygame.Color or int
    
    :param width: width of the circle (in pixels). If 0 the circle will be filled
    
    :type width: int
    """
    def __init__(self, color, width=0):
        self.color = color
        self.width = width

    def _draw(self, surface, target_rect):
        pygame.draw.circle(surface, self.color, target_rect.center, 
            int(round(min(target_rect.w, target_rect.h) * 0.5)), self.width)


class Fill:
    """Fills the assigned area. Afterwards, the children are rendered

    :param color: the color with which the area is filled

    :type color: pygame.Color or int
    """
    def __init__(self, color):
        self.color = color
        self.child = None

    def __call__(self, child):
        _check_call_op(self.child)
        self.child = _wrap_surface(child)
        return self
    
    def _draw(self, surface, target_rect):
        surface.fill(self.color, target_rect)
        if self.child:
            self.child._draw(surface, target_rect)


class Overlay:
    """Draws all its children on top of each other in the same rect"""
    def __init__(self, *children):
        self.children = _wrap_children(children)

    def _draw(self, surface, target_rect):
        for child in self.children:
            child._draw(surface, target_rect)


def Cross(width=3, color=0):
    """Draws a cross centered in the target area

    :param width: width of the lines of the cross in pixels
    :type width: int
    :param color: color of the lines of the cross
    :type color: pygame.Color
    """
    return Overlay(Line("h", width, color), Line("v", width, color))


class Border:
    """Draws a border around the contained area. Can have a single child.

    :param width: width of the border in pixels
    :type width: int
    :param color: color of the border
    :type color: pygame.Color
    """
    def __init__(self, width=3, color=0):
        v_line = Line("v", width, color)
        h_line = Line("h", width, color)
        self.child_was_added = False
        self.overlay = Overlay(
            LinLayout("h")(
                LLItem(0)(v_line),
                LLItem(1),
                LLItem(0)(v_line)
            ),
            LinLayout("v")(
                LLItem(0)(h_line),
                LLItem(1),
                LLItem(0)(h_line)
            )
        )

    def __call__(self, child):
        _check_call_op(None if not self.child_was_added else 1)
        self.overlay.children.append(_wrap_surface(child))
        return self

    def _draw(self, surface, target_rect):
        self.overlay._draw(surface, target_rect)


class Line:
    """Draws a line.

    :param width: width of the line in pixels
    :type widht: int
    :param orientation: "v" or "h". Indicates whether the line should be
        horizontal or vertical.
    :type orientation: str
    """
    def __init__(self, orientation, width=3, color=0):
        assert orientation in ["h", "v"]
        assert width > 0
        self.orientation = orientation
        self.width = width
        self.color = color

    def _draw(self, surface, target_rect):
        if self.orientation == "h":
            pygame.draw.line(surface, self.color, (
                target_rect.left, 
                _round_to_int(target_rect.top + target_rect.h * 0.5)), (
                target_rect.left + target_rect.w - 1, 
                _round_to_int(target_rect.top + target_rect.h * 0.5)),
            self.width)
        else:
            pygame.draw.line(surface, self.color, (
                _round_to_int(target_rect.left + target_rect.width * 0.5), 
                target_rect.top), (
                _round_to_int(target_rect.left + target_rect.width * 0.5), 
                target_rect.top + target_rect.h - 1), 
            self.width)

def _fill_col(target_len): 
    return lambda col: col + [None] * (target_len - len(col))

def _interleave_with_lines(line, contents):
    ll = [LLItem(0)(line)]
    return chain(*zip(ll * len(contents), contents), ll)


def _to_h_layout(cols, line_width, color): 
    def inner_wrap(children): 
        contents = [it(child) for it, child in zip( 
                         map(LLItem, cols), 
                         map(_wrap_surface, children))]
        return LinLayout("h")(*(contents if line_width == 0 else
                                _interleave_with_lines(Line("v", line_width, color), 
                                                       contents)))
    return inner_wrap


def GridLayout(row_proportions=None, col_proportions=None, line_width=0, color=0):
    """Layout that arranges its children on a grid.
    
    Proportions are given as lists of integers, where the nth element
    represents the proportion of the nth row or column.

    Children are added in lists, every list represents one row,
    if row or column proportions are provided, the number of rows or columns in
    the children must match the provided proportions.
    To define an empty cell use None as child.
    
    If no column proportions are provided, rows can have different lengths. In
    this case the width of the layout will be the length of the longest row,
    and the other rows will be filled with Nones"""
    def inner_grid_layout(*children):
        nonlocal row_proportions, col_proportions
        assert all(type(child) == list for child in children)
        if row_proportions is None: row_proportions = [1] * len(children)
        else: assert len(row_proportions) == len(children)

        col_width = max(map(len, children))
        if col_proportions: assert len(col_proportions) == col_width
        else: col_proportions = [1] * col_width
        filled_cols = _lmap(_fill_col(col_width), children)

        llitems = map(LLItem, row_proportions)
        mapped_rows = map(_to_h_layout(col_proportions, line_width, color),
                filled_cols)
        contents = [it(child) for it, child in zip(llitems, mapped_rows)]
        
        return LinLayout("v")(*_interleave_with_lines(
            Line("h", line_width, color), contents)
            if line_width else contents)

    return inner_grid_layout
    

def compose(target, root=None):
    """Top level function to create a surface.
    
    :param target: the pygame.Surface to blit on. Or a (width, height) tuple
        in which case a new surface will be created

    :type target: -
    """
    if type(root) == Surface:
        raise ValueError("A Surface may not be used as root, please add "
                        +"it as a single child i.e. compose(...)(Surface(...))")
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

        root_context._draw(surface, pygame.Rect(0, 0, *size))
        return surface
    return inner_compose 


@lru_cache(128)
def Font(name=None, source="sys", italic=False, bold=False, size=20):
    """Unifies loading of fonts.

    :param name: name of system-font or filepath, if None is passed the default
        system-font is loaded

    :type name: str
    :param source: "sys" for system font, or "file" to load a file
    :type source: str
    """
    assert source in ["sys", "file"]
    if not name:
        return pygame.font.SysFont(pygame.font.get_default_font(), 
        size, bold=bold, italic=italic)
    if source == "sys":
        return pygame.font.SysFont(name, 
        size, bold=bold, italic=italic)
    else:
        f = pygame.font.Font(name, size)
        f.set_italic(italic)
        f.set_bold(bold)
        return f
        

def _text(text, font, color=pygame.Color(0, 0, 0), antialias=False):
    text = font.render(text, antialias, color)
    return text.convert_alpha()


def Text(text, font, color=pygame.Color(0, 0, 0), antialias=False, align="center"):
    """Renders a text. Supports multiline text, the background will be transparent.
    
    :param align: text-alignment must be "center", "left", or "righ"
    :type align: str
    :return: the input text
    :rtype: pygame.Surface
    """
    assert align in ["center", "left", "right"]
    margin_l, margin_r = 1, 1
    if align == "left": margin_l = 0
    elif align == "right": margin_r = 0
    margin = Margin(margin_l, margin_r)
    color_key = pygame.Color(0, 0, 1) if pygame.Color(0, 0, 1) != color else 0x000002
    
    text_surfaces = [_text(line.strip(), font=font, 
                           color=color, antialias=antialias)
                     for line in text.split("\n")]
    w = max(surf.get_rect().w for surf in text_surfaces)
    h = sum(surf.get_rect().h for surf in text_surfaces)
    surf = compose((w, h), Fill(color_key))(LinLayout("v")(
        *_lmap(lambda s: Surface(margin)(s), text_surfaces)))
    surf.set_colorkey(color_key)
    return surf.convert_alpha()
