from raylibpy import *

class View(object):
    def __init__(self):
        self.camera = Camera2D()
        self.camera.offset = Vector2(0, 0)
        self.camera.target = Vector2(mario.position[0] + 20, mario.position[1] + 20)
        self.camera.rotation = 0.0
        self.camera.zoom = 1.0