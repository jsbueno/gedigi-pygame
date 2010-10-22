#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import math
import random

from editor_utils import DURATIONDONTCARE, DURATIONENDED, DURATIONCONTINUE, Coord


class EffectedChar(object):
    """
        Stores data needed to special effect
        applied to a single char on the text editor

        char effects should store the state data for each
        effect in name-spaced attributes here.
    """
    def __init__(self, text_pos, phase=0, effects=None):
        self.text_pos = text_pos
        self.line = None
        #pixel position within the rendered line
        self.pix_pos = None
        self.pix_offset = Coord((0, 0))
        self.phase = phase
        if not effects:
            self.effects = [CharEffect(BaseCharEffect)]
        else:
            self.effects = list(effects)
            self.effects.insert(0, CharEffect(BaseCharEffect))
        self.started = False
        self.loaded = False
        
    def start(self):
        self.effect_appliers = []
        for effect in self.effects:
            self.effect_appliers.append(effect.start(self))
        self.started = True
    
    def load(self, text_pos, line, pix_pos, surface):
        self.loaded = True
        self.text_pos = text_pos
        self.line = line
        self.pix_pos = Coord(pix_pos)
        self.original_surface = self.surface = surface
    
    def update(self):
        if not self.loaded:
            return DURATIONCONTINUE
        if not self.started:
            self.start()
        results = [effect() for effect in self.effect_appliers]
        try:
            while True:
                to_die = results.index(DURATIONENDED)
                del self.effects[to_die]
                del self.effect_appliers[to_die]
                del results[to_die]
        except ValueError:
            pass
        return max(results)
     
    def __repr__(self):
        return u"Effect char" + unicode(self.effects)
     

# Created to uniformize access to text effects,
# though line effects are much simpler than char 
# effects and can be instantiated directly
def LineEffect (effect_class, **parameters):
    if isinstance(effect_class, str):
        effect_class = globals()[effect_class]
    return effect_class(**parameters)

class CharEffect(object):
    def __init__(self, effect_class, **parameters):
        if isinstance(effect_class, str):
            effect_class = globals()[effect_class]
        self.effect_class = effect_class
        self.parameters = parameters
    
    def start(self, char):
        effect = self.effect_class(char)
        effect.__dict__.update(self.parameters)
        #these could lie in __init__ but some 
        #variables in the state may need the parameters
        #to be set first
        effect.start()
        return effect

class BaseCharEffect(object):
    def __init__(self, char):
        self.char = char

    def start(self):
        pass
    
    def __call__(self):
        self.char.surface = self.char.original_surface
        self.char.pix_offset = Coord((0, 0))
        self.char.phase += 1
        return DURATIONDONTCARE

class CharWalk(BaseCharEffect):
    duration = 15
    speed = None
    angle = None
    def start(self):
        if self.speed is None:
            speed = random.uniform(3, 6)
        else:
            speed = self.speed
        duration = self.duration
        radius = speed * duration
        if self.angle is None:
            angle = random.uniform(0, 2 * math.pi)
        else:
            angle = self.angle
        self.offset = Coord(self.char.surface.get_rect().center)
        self.offset.x += radius * math.cos(angle)
        self.offset.y += -radius * math.sin(angle)
        self.step = Coord((-self.offset.x / duration,
                             -self.offset.y / duration))

    def __call__(self):
        self.offset += self.step
        self.char.pix_offset += self.offset
        if self.duration > self.char.phase:
            return DURATIONCONTINUE
        return DURATIONENDED

class CharRot(BaseCharEffect):
    duration = 15
    angle = 180
    scale = 1.0
    def start(self):
        self.angular = - float(self.angle) / self.duration
        self.scalar = -(self.scale - 1.0) / self.duration

    def __call__(self):
        or_size = Coord(self.char.surface.get_size())
        self.char.surface = pygame.transform.rotozoom(self.char.surface, self.angle, self.scale)
        new_size = Coord(self.char.surface.get_size())
        offset = (or_size - new_size) / 2
        self.char.pix_offset += offset
        self.angle += self.angular
        self.scale += self.scalar
        if self.duration > self.char.phase:
            return DURATIONCONTINUE
        return DURATIONENDED

class CharTranslucence(BaseCharEffect):
    duration = 15
    opacity = 0  # Initial opacity
    def start(self):
        self.step = 255 // self.duration
        
    def __call__(self):
        # FIXME: there must be a way to optimize this :-(
        # (like, in not iterating over all pixels in python)
        surface = self.char.surface.copy()
        alpha = pygame.surfarray.pixels_alpha(surface)
        #alpha_surf = pygame.surfarray.make_surface(alpha)
        op = self.opacity
        for col in alpha:
            for i, value in enumerate(col):
                if value > op:
                    col[i] =  op
        del alpha
        self.char.surface = surface
        self.opacity += self.step
        if self.opacity < 255:
            return DURATIONCONTINUE
        return DURATIONENDED

class CharImplode(BaseCharEffect):
    duration = 15
    scale = 6
    ordered = False
    def start(self):
        self.scalar = -(self.scale - 1.0) / self.duration
        self.random_state = random.getstate()
    
    def __call__(self):
        original_random_state = random.getstate()
        random.setstate(self.random_state)
        or_size = Coord(self.char.surface.get_size())
        dst_surface = pygame.Surface((or_size * self.scale).to_int(), SRCALPHA, 32)
        dst_size = Coord(dst_surface.get_size())
        
        src_pixels = pygame.surfarray.pixels2d(self.char.surface)
        dst_pixels = pygame.surfarray.pixels2d(dst_surface)
        cx, cy = or_size / 2.0
        dcx, dcy = (dst_size / 2.0).to_int()
        s = self.scale
        ordered = self.ordered
        ellapsed = self.char.phase / float(self.duration)
        remaining = 1.0 - ellapsed
        for x, col in enumerate(src_pixels):
            if x > cx:
                x_quad = dcx
            else:
                x_quad = 0
            for y, pixel in enumerate(col):
                if not ordered:
                    if y > cy:
                        y_quad = dcy
                    else:
                        y_quad = 0
                    # starting positions fixed
                    #  due to fixed state of  random:
                    st_x = random.randrange(dcx) + x_quad
                    st_y = random.randrange(dcy) + y_quad
                if pixel:
                    nx = int((x - cx) * self.scale + dcx)
                    ny = int((y - cy) * self.scale + dcy)
                    if not ordered:
                        nx = int(ellapsed * nx + remaining * st_x)
                        ny = int(ellapsed * ny + remaining  * st_y)
                    dst_pixels[nx][ny] = pixel
        del dst_pixels
        self.char.surface = dst_surface
        new_size = Coord(self.char.surface.get_size())
        offset = (or_size - new_size) / 2
        self.char.pix_offset += offset
        self.scale += self.scalar
        random.setstate(original_random_state)
        if self.duration > self.char.phase:
            return DURATIONCONTINUE
        return DURATIONENDED

class BaseLineEffect(object):
    """
        Base class for special raster effects
        applied on each line of text as it is 
        rendered to the screen.
        
        Each derived class should define the calc_hor_step
        and effect methods - the later on actually renders
        the effect.
    """
    
    def calc_hor_step(self, w, h):
        return w
    
    def __call__(self, surface, line=0, phase=0):
        w, h = surface.get_size()
        hor_step = self.calc_hor_step(w, h)
        # The SRCALPHA flag fills the surface with 
        # transparency, otherwise it is opaque black
        new_surface = pygame.Surface((w, h),SRCALPHA, 32)
        x = 0
        while x < w:
            w1 = min(hor_step, w - x)
            slice = surface.subsurface((x, 0, w1, h))
            slice, v_pos = self.effect(slice, w, h, x, w1, line, phase)
            new_surface.blit(slice, (x, v_pos))
            x += hor_step
        return new_surface
    
    def effect(self, slice, width, height, x_pos, slice_width, phase):
        return slice, 0

class Waves(BaseLineEffect):
    """
       Valid alignments are "base", "center" and "top"
    """
    def __init__(self, lenght=50, amplitude=.5, align="base"):
        self.lenght = lenght
        self.amplitude = amplitude
        self.f = math.pi / self.lenght
        if align == "base":
            self.align_func = lambda h, new_h: h - new_h
        elif align == "center":
            self.align_func = lambda h, new_h: (h - new_h) // 2
        else:
            self.align_func = lambda h, new_h: 0
        
    def calc_hor_step(self, w, h):
        return max(1, int (self.lenght/(h * self.amplitude)))
    
    def effect(self, slice, w, h, x, w1, line, phase):
        phase /= 5.0
        phase += line
        new_h = int(h * (self.amplitude * .5 * (1 + math.sin(phase + x * self.f)) + (1.0 - self.amplitude)))
        slice = pygame.transform.scale(slice, (w1, new_h))
        return slice, self.align_func(h, new_h)

class Colors(BaseLineEffect):
    def __init__(self, lenght=30, colors=None):
        if colors is None:
            self.colors=[(255, i, 0) for i in xrange(255, 0, -10)]
        else:
            self.colors = colors
        self.lenght = lenght
    calc_hor_step = lambda self, w, h: self.lenght
    
    def effect(self, slice, w, h, x, w1, line, phase):
        phase = int(phase / 3.0) + line * 3
        color = self.colors[int(phase + x / w1)  % len(self.colors)]

        # pixels3d will let alpha unaltered
        pixels = pygame.surfarray.pixels3d(slice)
        for col in xrange(len(pixels)):
            pixels[col] = color
            
        # pygame.surfarray.blit_array(slice, pixels)
        del pixels
        return slice, 0
        
__all__ = [name for name, class_ in globals().items() if isinstance(class_, type) and ( (issubclass(class_, BaseCharEffect) and not class_ is BaseCharEffect) 
                                         or (issubclass(class_, BaseLineEffect) and not class_ is BaseLineEffect))]  