import cProfile
from animated_drawings import render

cProfile.run('render.start("./examples/config/mvc/export_gif_example.yaml")')