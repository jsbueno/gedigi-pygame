#!/usr/bin/python
# coding: utf-8

import pygame
from functools import wraps

DURATIONDONTCARE = 0
DURATIONENDED = 1
DURATIONCONTINUE = 2


class Coord(list):
    """
       Auxiliar loose vector type to make operations
       with coordinates. Methods are being implemented
       as needed.
    """
    def __init__(self, *coords):
        list.__init__(self, *coords)
        if not coords:
            self.extend([0,0])
        
    x = property(lambda self: self[0],
                 lambda self, value: self.__setitem__(0, value))
    y = property(lambda self: self[1],
                 lambda self, value: self.__setitem__(1, value))
    def __iadd__(self, other):
        self[0] += other[0]
        self[1] += other[1]
        return self
    def __add__(self, other):
        return Coord ((self[0] + other[0],
                       self[1] + other[1]))
    def __sub__(self, other):
        return Coord((self[0] - other[0],
                      self[1] - other[1]))
    def __mul__(self, scalar):
        return Coord((self[0] * scalar, self[1] * scalar))
    def __div__(self, scalar):
        return Coord((self[0] / scalar, self[1] / scalar))
    def to_int(self):
        return Coord((int(self[0]), int(self[1])))

# Aspect oriented-like decorators for 
# text rendering caching:
def _clear_or_dirty(method, dirty):
    @wraps(method)
    def wrapper(self, *args, **kw):
        result = method(self, *args, **kw)
        self._dirty = dirty
        return result
    return wrapper

def dirties(method):
    return _clear_or_dirty(method, True)

def clears(method):
    return _clear_or_dirty(method, False)


def cached(method):
    @wraps(method)
    def wrapper(self, *args, **kw):
        if (not self._dirty and
            hasattr(self, "_cached" + method.__name__)):
            value, c_args, c_kw = getattr(self, "_cached" + method.__name__)
            if c_args == args and c_kw == kw:
                return value
        value = method(self, *args, **kw)
        setattr(self, "_cached" + method.__name__, 
                (value, args, kw))
        return value
    return wrapper

