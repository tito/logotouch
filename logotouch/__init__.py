__all__ = ('LTWorld', )

from ltworld import LTWorld
from os.path import dirname, join
from pymt import css_reload, css_add_file, css_register_prefix, \
                 css_register_state

current_path = dirname(__file__)

css_register_state('selected')
css_register_prefix('antonym')
css_add_file(join(current_path, 'styles', 'logotouch.css'))
css_reload()

