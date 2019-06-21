"""Using functionality from this file requires extra dependencies."""
import warnings

try:
    import numpy as np
    from matplotlib import cm
    import matplotlib as mpl
except ImportError:
    warnings.warn("This module requires numpy and matplotlib, which seem to be missing.")

import contextlib
with contextlib.redirect_stdout(None):
    import pygame


def _normalize(mat: np.ndarray):
    """rescales a numpy array, so that min is 0 and max is 255"""
    abs_max = np.nanmax(np.abs(mat))
    norm = mpl.colors.Normalize(vmin=-float(abs_max),vmax=abs_max)
    return norm(mat).data


def to_24bit_gray(mat: np.ndarray):
    """returns a matrix that contains RGB channels, and colors scaled
    from 0 to 255"""
    return np.repeat(np.expand_dims(_normalize(mat) * 255, axis=2), 3,
            axis=2).astype(np.uint8)


def apply_color_map(name: str, mat: np.ndarray = None, normalize = True):
    """returns an RGB matrix scaled by a matplotlib color map,
    if normalize is False the matrix must only have values in the range [0, 1]"""
    def apply_map(mat):
        if normalize:
            mat = _normalize(mat)
        return (cm.get_cmap(name)(mat) * 255).astype(np.uint8) 
        
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

    transformed_mat = transformer(mat.T) if transformer is not None else mat.T
    if transformed_mat.shape[2] == 4:
        img = pygame.pixelcopy.make_surface(transformed_mat[:, :, :3])\
                .convert_alpha()
        pix_arr = pygame.surfarray.pixels_alpha(img)
        pix_arr = transformed_mat[:, :, 3]
        return img


    return pygame.pixelcopy.make_surface(transformed_mat)
