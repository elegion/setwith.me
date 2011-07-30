# -*- coding: utf-8 -*-

def match(first, second, third):
    return (first == second and second == third) or \
    (first != second and first != third and second != third)


class Color:
    red = 1
    green = 2
    purple = 3

class Symbol:
    oval = 1
    squiggle = 2
    diamond = 3

class Shading:
    solid = 1
    opened = 2
    striped = 3


class Card:
    def __init__(self, number, shading, color, symbol):
        self.number = number
        self.shading = shading
        self.color = color
        self.symbol = symbol


attributes = ('number', 'shading', 'color', 'symbol')
def is_set(first, second, third):
    return all(match(
        getattr(first, a_name),
        getattr(second, a_name),
        getattr(third, a_name)) for a_name in attributes)


