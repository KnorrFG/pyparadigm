import pyparadigm as pp
import numpy as np

def test_extras():
    pp.init((800, 600))
    el = pp.EventListener()
    arr = np.arange(1, 101).reshape(10, 10)
    pp.display(pp.compose(pp.empty_surface(0))(
        pp.Surface(scale=1)(pp.mat_to_surface(arr))))
    el.wait_for_seconds(1)
    pp.display(pp.compose(pp.empty_surface(0))(
        pp.Surface(scale=1)(pp.mat_to_surface(arr,
            pp.apply_color_map("autumn")))))
    el.wait_for_seconds(1)
    _test_transparency_mask()
    el.wait_for_seconds(1)
    _test_transparency_colorkey()
    el.wait_for_seconds(1)


def _test_transparency_colorkey():
    tra_img = pp.compose(pp.empty_surface(0))(
            pp.empty_surface(20, (200, 200)))
    tra_img = pp.make_transparent_by_colorkey(tra_img, 20)
    pp.display(pp.compose(pp.empty_surface(0xFF0000))(
        tra_img))

def _test_transparency_mask():
    mask = np.ones((100, 100), dtype=bool)
    mask[:, :50] = 0
    img = pp.mat_to_surface(np.random.randint(0, 255, (100, 100)))
    pp.display(pp.compose(pp.empty_surface(0))(
        pp.make_transparent_by_mask(img, mask)))



if __name__ == "__main__":
    test_extras()
