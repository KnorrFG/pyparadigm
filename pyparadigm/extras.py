"""Using functionality from this file requires extra dependencies."""
import numpy as np
from matplotlib import cm

import contextlib
with contextlib.redirect_stdout(None):
    import pygame


def _normalize(mat: np.ndarray):
    """rescales a numpy array, so that min is 0 and max is 255"""
    return ((mat - mat.min()) * (255 / mat.max())).astype(np.uint8)


def to_24bit_gray(mat: np.ndarray):
    """returns a matrix that contains RGB channels, and colors scaled
    from 0 to 255"""
    return np.repeat(np.expand_dims(_normalize(mat), axis=2), 3, axis=2)


def apply_color_map(name: str, mat: np.ndarray = None):
    """returns an RGB matrix scaled by a matplotlib color map"""
    def apply_map(mat):
        return (cm.get_cmap(name)(_normalize(mat))[:, :, :3] * 255).astype(np.uint8)
        
    return apply_map if mat is None else apply_map(mat)


def mat_to_surface(mat: np.ndarray, transformer=to_24bit_gray):
    """Can be used to create a pygame.Surface from a 2d numpy array.

    By default a grey image with scaled colors is returned, but using the
    transformer argument any transformation can be used.

    :param mat: the matrix to create the surface of.
    :type mat: np.ndarray

    :param transformer: function that transforms the matrix to a valid color
        matrix, i.e. it must have 3dimension, were the 3rd dimension are the color
        channels. For each channel a value between 0 and 255 is allowed
    :type transformer: Callable[np.ndarray[np.ndarray]]"""

    return pygame.pixelcopy.make_surface(transformer(mat.transpose()) 
        if transformer is not None else mat.transpose())