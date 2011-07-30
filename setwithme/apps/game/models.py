# -*- coding: utf-8 -*-

import datetime
from django.db import models
from django.contrib.auth.models import User


attributes_order = ('color', 'symbol', 'number', 'shading')
attributes = {'color': ('red', 'green', 'purple'),
              'symbol': ('oval', 'squiggle', 'diamond'),
              'number': (1, 2, 3),
              'shading': ('solid', 'open', 'striped')}


class Game(models.Model):

    finished = models.BooleanField(default=False)
    start = models.DateTimeField(default=datetime.datetime.now)
    end = models.DateTimeField(null=True, default=None)
    cards = models.CommaSeparatedIntegerField(max_length=250)

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        self.cards = ','.join(map(str, xrange(81)))

    def remove_cards(self, first, second, third):
        cards = map(int, self.cards.split(','))
        cards.remove(first)
        cards.remove(second)
        cards.remove(third)
        self.cards = ','.join(map(str, cards))
        self.save()

    def get_cards(self):
        return map(int, self.cards.split(','))
    

class GameSession(models.Model):

    game = models.ForeignKey(Game, null=True)
    state = models.IntegerField(default=0)
    #user = models.ForeignKey(User)
    user = models.CharField(max_length=50) # Session key
    sets_found = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)

    def serialize(self):
        return {'game': self.game_id,
                'user': self.user,
                'sets_found': self.sets_found,
                'failures': self.failures}
