# -*- coding: utf-8 -*-

import datetime
import random
import uuid
from django.db import models
from django.contrib.auth.models import User
random_id = lambda : unicode(uuid.uuid4())


attributes_order = ('color', 'symbol', 'number', 'shading')
attributes = {'color': ('red', 'green', 'purple'),
              'symbol': ('oval', 'squiggle', 'diamond'),
              'number': (1, 2, 3),
              'shading': ('solid', 'open', 'striped')}


PRESSED_SET_TIMEOUT = datetime.timedelta(seconds=5)


class Game(models.Model):

    uid = models.CharField(max_length=36, unique=True)
    finished = models.BooleanField(default=False)
    start = models.DateTimeField(default=datetime.datetime.now)
    end = models.DateTimeField(null=True, default=None)
    cards = models.CommaSeparatedIntegerField(max_length=250)

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        self.cards = ','.join(map(str, xrange(81)))

    @property
    def cards_list(self):
        if not self.cards:
            return []
        return map(int, self.cards.split(','))

    @cards_list.setter
    def cards_list(self, lst):
        self.cards = ','.join(map(str, lst))
        self.save()

    def remove_cards(self, first, second, third):
        cards = self.cards_list
        assert len(cards) >= 3
        cards.remove(first)
        cards.remove(second)
        cards.remove(third)
        self.cards_list = cards

    def pop_cards(self, quantity=3):
        cards = self.cards_list
        indexes = []
        for i in xrange(min(quantity, len(cards))):
            indexes.append(random.randrange(0, len(cards) - i))
        res = []
        for index in indexes:
            res.append(cards.pop(index))
        self.cards_list = cards
        return res

class State:
    IDLE = 0
    SET_PRESSED = 1
    BLOCKED = 2
    

class GameSession(models.Model):
    game = models.ForeignKey(Game, null=True)
    state = models.IntegerField(default=0)
    #user = models.ForeignKey(User)
    user = models.CharField(max_length=50) # Session key
    set_pressed_dt = models.DateTimeField(null=True)
    sets_found = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)

    def press_set(self):
        self.set_pressed_dt = datetime.datetime.now()
        self.state = State.SET_PRESSED

    def set_in_time(self):
        return self.set_pressed_dt + PRESSED_SET_TIMEOUT > \
            datetime.datetime.now() if self.set_pressed_dt else \
            False

    def serialize(self, current_user_id):
        return {'game': self.game_id,
                'state': self.state,
                'user_id': self.user,
                'me': self.user == current_user_id,
                'sets_found': self.sets_found,
                'failures': self.failures}

