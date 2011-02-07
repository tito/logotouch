from time import time
from pymt import *
from wordprovider import *
from OpenGL.GL import *
import pymunk as pm

class LTWord(MTWidget):
    def __init__(self, **kwargs):
        self.provider = CSVWordProvider(kwargs.get('filename'))
        kwargs.setdefault('cls', self.provider.wtype)

        super(LTWord, self).__init__(**kwargs)
        self._word = ''
        self._vertex = []
        self.padding_x = kwargs.get('padding_x', 50)
        self.padding_y = kwargs.get('padding_y', 30)
        self.textopt = {
            'font_size': self.style.get('font-size'),
            'font_name': self.style.get('font-name'),
            'color':     self.style.get('color'),
        }
        self.touches = []
        self.touch = None
        self.action_exclusive = None
        self.padding = 10
        self.lpos = self.pos
        self.lsize = self.size
        self.ldirection = self.direction = 0
        self.angle = None
        self.shake_counter = 0
        self.shake_direction = 0

        # configure trigger
        self.action_scale_trigger = kwargs.get('scale_trigger', 30)
        self.action_scale_padding = kwargs.get('scale_padding', 10)
        self.action_scale_fontsize = kwargs.get('scale_fontsize', 1)
        self.action_rotation_trigger = kwargs.get('rotation_trigger', 45)
        self.action_time_trigger = kwargs.get('time_trigger', 25)
        self.action_person_trigger = kwargs.get('person_trigger', 25)
        self.action_shake_trigger = kwargs.get('shake_trigger', 15)

        # init pymunk
        self.pm_space = kwargs.get('space')
        self.pm_body = None
        self.pm_shape = None

        # launch initial vertex calculation + pymunk shape
        self.update_vertex()

    #
    # pymunk part
    #

    def update_pymunk_shape(self):
        if self.pm_body is not None:
            self.pm_space.remove(self.pm_body, self.pm_shape)
        mass = 10.
        v = self.vertex
        x, y = self.pos
        points = [(v[0] - x, v[1] - y), (v[2] - x, v[3] - y),
                  (v[4] - x, v[5] - y), (v[6] - x, v[7] - y)]
        moment = pm.moment_for_poly(mass, points, (0,0))
        self.pm_body = pm.Body(mass, moment)
        self.pm_body.position = self.pos
        self.pm_shape = pm.Poly(self.pm_body, points, (0,0))
        self.pm_shape.friction = 1
        self.pm_space.add(self.pm_body, self.pm_shape)

    def update_pymunk_position(self):
        if not self.pm_body:
            return
        self.pm_body.position = tuple(self.lpos)

    #
    # shape
    #

    def update_vertex(self):
        w = self.width
        h = self.height
        x = self.x - w / 2.
        y = self.y - h / 2.
        d = -self.direction
        self.vertex = [x, y+d, x+w, y-d, x+w, y+h+d, x, y+h-d]

    def _get_vertex(self):
        return self._vertex
    def _set_vertex(self, x):
        if self._vertex == x:
            return
        self._vertex = x
    vertex = property(_get_vertex, _set_vertex)


    #
    # word part
    #

    def _get_word(self):
        return self._word
    def _set_word(self, x):
        if self._word == x:
            return
        self._word = x
        self.label = getLabel(x, **self.textopt)
        s = self.label.content_size
        p = self.padding
        self.lsize = s[0] + self.padding_x + p, s[1] + self.padding_y + p
    word = property(_get_word, _set_word)

    def update_word(self):
        self.word = self.provider.get()

    #
    # detect action
    #

    def is_controled(self):
        return bool(len(self.touches))

    def is_action_allowed(self, action):
        return not self.action_exclusive or self.action_exclusive == action

    def detect_action(self, touch):
        num = len(self.touches)
        action = None
        if num == 1:
            action = self.detect_action_1(touch)
        elif num == 2:
            action = self.detect_action_2(touch)
        elif num == 3:
            action = self.detect_action_3(touch)
        if action:
            self.apply_action(action, touch)

    def detect_action_1(self, touch):
        # double tap ?
        if self.is_action_allowed('toggleperson'):
            if touch.is_double_tap:
                return 'toggleperson'

        # only one action possible.. move :=)
        if self.is_action_allowed('shake'):
            distance = Vector(touch.userdata['origin']).distance(touch.pos)
            direction = (touch.x - touch.userdata['origin'][0] > 0)
            if distance > self.action_shake_trigger:
                # no shake yet, initialize.
                if self.shake_counter == 0:
                    self.shake_counter = 1
                    self.shake_direction = not direction
                elif self.shake_direction == direction:
                    self.shake_direction = not direction
                    self.shake_counter += 1
                if self.shake_counter >= 3:
                    return 'shake'

        # no shake... allow move :)
        if self.is_action_allowed('move'):
            return 'move'

    def detect_action_2(self, touch):
        touch1, touch2 = self.touches
        # 2 fingers, detect scale
        if self.is_action_allowed('scale'):
            distance = Vector(touch1.pos).distance(touch2.pos) - \
                       Vector(touch1.userdata['origin']).distance(touch2.userdata['origin'])
            if abs(distance) >= self.action_scale_trigger:
                touch.userdata['scale'] = distance
                return 'scale'

        # no scale, detect a rotation
        if self.is_action_allowed('rotate'):
            angle = Vector(0, 1).angle(Vector(touch1.pos) - Vector(touch2.pos))
            if self.angle is None:
                self.angle = angle
            else:
                angle = abs(angle - self.angle) % 360
                if angle > 180:
                    angle = 360 - angle
                # trigger
                if angle > self.action_rotation_trigger:
                    return 'rotate'

    def detect_action_3(self, touch):
        touch1, touch2, touch3 = self.touches
        if touch is not touch3:
            return

        # do the movement detection only on the third finger
        dx = touch.x - touch.userdata['origin'][0]
        dy = touch.y - touch.userdata['origin'][1]
        if self.is_action_allowed('time'):
            if abs(dx) > self.action_time_trigger:
                touch.userdata['time'] = dx
                return 'time'
        if self.is_action_allowed('person'):
            if abs(dy) > self.action_person_trigger:
                touch.userdata['person'] = dy
                return 'person'



    #
    # apply action
    #

    def apply_action(self, action, touch):
        pymt_logger.debug('apply action %s' % action)
        # just move the word
        if action == 'move':
            self.lpos = map(int, Vector(touch.pos) - touch.userdata['delta'])
            return

        # do synonym
        elif action == 'shake':
            pymt_logger.debug('do shake')
            self.cancel_action_scale()
            self.cancel_action_antonym()
            self.provider.do_synonym()
            self.shake_counter = 0
            self.shake_direction = 0

        else:
            self.cancel_action_shake()

        if action == 'toggleperson':
            pymt_logger.debug('toggle person')
            self.provider.toggle_person()

        # bigger / smaller word
        if action == 'scale':
            self.action_exclusive = 'scale'
            if touch.userdata['scale'] > 0:
                if self.provider.do_zoomout():
                    self.padding += self.action_scale_padding
                    self.textopt['font_size'] += self.action_scale_fontsize
                    pymt_logger.debug('do scale + %d' % self.padding)
            else:
                if self.provider.do_zoomin():
                    self.padding -= self.action_scale_padding
                    self.textopt['font_size'] -= self.action_scale_fontsize
                    pymt_logger.debug('do scale - %d' % self.padding)

        # rotation do the antonym
        elif action == 'rotate':
            if self.action_exclusive != 'rotate':
                self.action_exclusive = 'rotate'
                self.provider.do_antonym()
                s = self.style.get
                color = s('color')
                if self.provider.antonym:
                    color = s('antonym-color')
                self.textopt['color'] = color

        # prev/next time
        elif action == 'time':
            pymt_logger.debug('do time %d' % touch.userdata['time'])
            self.action_exclusive = 'time'
            if touch.userdata['time'] > 0:
                self.provider.do_time_next()
            else:
                self.provider.do_time_previous()
            self.ldirection = (self.provider.tense - 1) * 10

        # prev/next pronoun
        elif action == 'person':
            pymt_logger.debug('do person')
            self.action_exclusive = 'person'
            if touch.userdata['person'] < 0:
                self.provider.do_person_next()
            else:
                self.provider.do_person_previous()

        self.reset_action()

    def cancel_action_scale(self):
        self.padding = 10
        self.textopt['font_size'] = self.style.get('font-size')
        self.provider.zoom = 0

    def cancel_action_antonym(self):
        self.textopt['color'] = self.style.get('color')
        if self.provider.antonym:
            self.provider.do_antonym()

    def cancel_action_shake(self):
        self.shake_counter = 0
        self.shake_direction = 0

    def reset_action(self):
        pymt_logger.debug('reset')
        # reset origin of all touches.
        for touch in self.touches:
            touch.userdata['origin'] = touch.pos
        self.angle = None

    def reset_detection(self):
        # reset exclusive action
        self.reset_action()
        self.action_exclusive = None
        self.cancel_action_shake()


    #
    # pymt interaction
    #

    def collide_point(self, x, y):
        ox, oy = self.pos
        w = self.width / 2.
        h = self.height / 2.
        return ox - w <= x <= ox + w and oy - h <= y <= oy + h

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        self.touches.append(touch)
        touch.userdata['origin'] = touch.opos
        touch.userdata['delta'] = Vector(touch.pos) - Vector(self.pos)
        touch.userdata['time'] = time()
        if self.touch is None:
            self.touch = touch
            self.detect_action(touch)
        return True

    def on_touch_move(self, touch):
        if not touch in self.touches:
            return False
        self.detect_action(touch)
        return True

    def on_touch_up(self, touch):
        if touch not in self.touches:
            return
        self.touches.remove(touch)
        if touch is self.touch:
            self.touch = None
        self.reset_detection()
        return True

    #
    # pymt update / drawing
    #

    def on_resize(self, w, h):
        super(LTWord, self).on_resize(w, h)
        self.update_vertex()
        self.update_pymunk_shape()

    def on_move(self, x, y):
        w, h = getWindow().size
        if x - self.width / 2. < 0:
            self.pos = (self.width / 2., self._pos[1])
            return
        if y - self.height / 2. < 0:
            self.pos = (self._pos[0], self.height / 2.)
            return
        if x + self.width / 2. > w:
            self.pos = (w - self.width / 2., self._pos[1])
            return
        if y + self.height / 2. > h:
            self.pos = (self._pos[0], h - self.height / 2.)
            return
        super(LTWord, self).on_move(x, y)
        self.update_vertex()
        if self.is_controled():
            self.update_pymunk_position()

    def on_update(self):
        super(LTWord, self).on_update()
        self.update_word()
        if Vector(self.size).distance(self.lsize) <= 1.:
            self.size = self.lsize
        else:
            self.size = interpolate(self.size, self.lsize, 5)
        if abs(self.ldirection - self.direction) <= 1.:
            self.direction = self.ldirection
        else:
            self.direction = interpolate(self.direction, self.ldirection, 5)
        if self.pm_body and not self.is_controled():
            self.lpos = self.pos = interpolate(self.pos, tuple(self.pm_body.position), 5)
        else:
            if Vector(self.pos).distance(self.lpos) <= 1.:
                self.pos = self.lpos
            else:
                self.pos = interpolate(self.pos, self.lpos, 5)

    def draw_background(self):
        state = 'selected' if len(self.touches) else ''
        prefix = 'antonym' if self.provider.antonym else ''
        def s(base, prefix, state):
            nbase = base
            if prefix:
                nbase = '%s-%s' % (prefix, nbase)
            if state:
                nbase = '%s-%s' % (nbase, state)
            return self.style.get(nbase, self.style.get(base))

        color       = s('color', prefix, state)
        bgcolor     = s('bg-color', prefix, state)
        bordercolor = s('border-color', prefix, state)
        vertex      = self.vertex

        # border
        set_color(*bordercolor)
        glLineWidth(2)
        drawPolygon(vertex, style=GL_LINE_LOOP)

        # background
        set_color(*bgcolor)
        drawPolygon(vertex)

    def draw(self):
        # drawing is done from the center
        self.draw_background()
        self.label.pos = self.pos
        self.label.draw()
