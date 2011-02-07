import sys
from pymt import *
from logotouch import LTWorld
from os.path import join, dirname
from glob import glob

world = LTWorld()

if len(sys.argv) > 1:
    files = sys.argv[1:]
else:
    datapath = join(dirname(__file__), 'data')
    files = glob(join(datapath, '*.csv'))

for filename in files:
    world.create_word(filename=filename)
    break

runTouchApp(world)
