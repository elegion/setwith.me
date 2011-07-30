# -*- coding: utf-8 -*-
from django.utils.datastructures import SortedDict

def match(first, second, third):
    return (first == second and second == third) or \
    (first != second and first != third and second != third)


class Card:
    attributes = SortedDict([
        ('count', ('one', 'two', 'three'),),
        ('symbol', ('oval', 'diamond', 'squiggle'),),
        ('shading', ('solid', 'open', 'striped')),
        ('color', ('red', 'green', 'blue'))
    ])

    def __init__(self, *args, **kwargs):
        text = kwargs.get('text')
        if text:
            kwargs = dict([(Card.attributes.keys()[n], value)
                           for n, value in enumerate(text.split(' '))])

        id = kwargs.get('id')
        if id is not None:
            self.id = id
            [setattr(self, key, value) for key, value in self.id_to_params(id).items()]
        else:
            [setattr(self, key, value) for key, value in kwargs.items()]
            self.id = self.params_to_id()

    def id_to_params(self, id):
        result = {}
        for n, key in enumerate(Card.attributes.keys()):
            power = 3**(len(Card.attributes)-n-1)
            pn = id/power
            id -= pn * power
            result[key] = Card.attributes[key][pn]
        return result

    def params_to_id(self, *kwargs):
        result = 0
        for n, key in enumerate(Card.attributes.keys()):
            result += 3**(len(Card.attributes)-n-1) * Card.attributes[key].index(getattr(self, key))
        return result
    
    def as_text(self):
        return ' '.join([getattr(self, key) for key in Card.attributes.keys()])

    def as_id(self):
        return self.id


def is_set(first, second, third):
    return all(match(
        getattr(first, a_name),
        getattr(second, a_name),
        getattr(third, a_name)) for a_name in Card.attributes)


