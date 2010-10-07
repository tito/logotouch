from pymt import *
from logotouch import LTWorld
from os.path import join, dirname
from glob import glob

world = LTWorld()
datapath = join(dirname(__file__), 'data')
for filename in glob(join(datapath, '*.csv')):
    world.create_word(filename=filename)

runTouchApp(world)
