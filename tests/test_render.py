from animated_drawings import render
from pkg_resources import resource_filename
import os


def test_render_gif():
    render_gif_cfg_fn = resource_filename(__name__, 'test_render_files/mvc_render_gif.yaml')

    render.start(render_gif_cfg_fn)

    assert os.path.exists('.tests/test_render_files/video.gif')
    assert os.path.getsize('.tests/test_render_files/video.gif') > 100

    os.remove('.tests/test_render_files/video.gif')


def test_render_mp4():
    render_mp4_cfg_fn = resource_filename(__name__, 'test_render_files/mvc_render_mp4.yaml')

    render.start(render_mp4_cfg_fn)

    assert os.path.exists('.tests/test_render_files/video.mp4')
    assert os.path.getsize('.tests/test_render_files/video.mp4') > 100

    os.remove('.tests/test_render_files/video.mp4')

