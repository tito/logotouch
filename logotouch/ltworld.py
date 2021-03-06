import pymunk as pm
from random import random
from ltword import LTWord
from pymt import *

class LTWorld(MTWidget):
    def __init__(self, **kwargs):
        super(LTWorld, self).__init__(**kwargs)
        self.size = getWindow().size

        try:
            pm.init_pymunk()
        except:
            pass
        self.space = pm.Space()
        self.space.gravity = (0., 0.)
        #self.space.resize_static_hash()
        #self.space.resize_active_hash()

        getClock().schedule_interval(self.update_world, 1. / 60)

    def create_word(self, **kwargs):
        x = (self.width / 2.) * (random() - .5)
        kwargs['pos'] = self.center[0] + x, self.center[1]
        kwargs['space'] = self.space
        word = LTWord(**kwargs)
        self.add_widget(word)

    def update_world(self, dt):
        if len(getCurrentTouches()) == 0:
            for child in self.children:
                if not isinstance(child, LTWord):
                    continue
                child.touch = None
                child.touches = []
                child.reset_detection()
        self.space.step(1. / 60)
