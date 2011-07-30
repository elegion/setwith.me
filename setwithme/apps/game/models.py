# -*- coding: utf-8 -*-
import random
import uuid
from django.db import models
from django.contrib.auth.models import User

from game.constants import *


get_uid = lambda : unicode(uuid.uuid4().hex)


attributes_order = ('color', 'symbol', 'number', 'shading')
attributes = {'color': ('red', 'green', 'purple'),
              'symbol': ('oval', 'squiggle', 'diamond'),
              'number': (1, 2, 3),
              'shading': ('solid', 'open', 'striped')}


class Game(models.Model):

    id = models.CharField(max_length=36, primary_key=True)
    finished = models.BooleanField(default=False)
    start = models.DateTimeField(default=datetime.datetime.now)
    end = models.DateTimeField(null=True, default=None)
    remaining_cards = models.CommaSeparatedIntegerField(max_length=250)
    desk_cards = models.CommaSeparatedIntegerField(max_length=250, default='')

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        ids = range(81)
        random.shuffle(ids)
        self.remaining_cards = ','.join(map(str, ids))

    @property
    def rem_cards_list(self):
        if not self.remaining_cards:
            return []
        return map(int, self.remaining_cards.split(','))

    @rem_cards_list.setter
    def rem_cards_list(self, lst):
        self.remaining_cards = ','.join(map(str, lst))
        self.save()

    @property
    def desk_cards_list(self):
        if not self.desk_cards:
            return []
        return map(int, self.desk_cards.split(','))

    @desk_cards_list.setter
    def desk_cards_list(self, lst):
        self.desk_cards = ','.join(map(str, lst))
        self.save()

    def drop_cards(self, first, second, third):
        cards = self.desk_cards_list
        assert len(cards) >= 3
        cards.remove(first)
        cards.remove(second)
        cards.remove(third)
        self.desk_cards_list = cards

    def pop_cards(self, quantity=3):
        cards = self.rem_cards_list
        indexes = []
        for i in xrange(min(quantity, len(cards))):
            indexes.append(random.randrange(0, len(cards) - i))
        res = []
        for index in indexes:
            res.append(cards.pop(index))
        self.rem_cards_list = cards
        dcl = self.desk_cards_list
        dcl.extend(res)
        self.desk_cards_list = dcl
        return res


class GameSessionState:
    IDLE = "IDLE"
    SET_PRESSED = "SET_PRESSED"
    SET_PENALTY = "SET_PENALTY"


GameSessionStateChoices = (
    (GameSessionState.IDLE, 'Idle'),
    (GameSessionState.SET_PRESSED, 'Set pressed'),
    (GameSessionState.SET_PENALTY, 'Set penalty'),
)


class ClientConnectionState:
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    LOST = "LOST"


ClientConnectionStateChoices = (
    (ClientConnectionState.ACTIVE, 'Active'),
    (ClientConnectionState.IDLE, 'Idle'),
    (ClientConnectionState.LOST, 'Lost'),
)


class GameSession(models.Model):
    game = models.ForeignKey(Game, null=True)
    state = models.CharField(
        max_length=50,
        default=GameSessionState.IDLE,
        choices=GameSessionStateChoices)
    client_state = models.CharField(
        max_length=50,
        default=ClientConnectionState.ACTIVE,
        choices=ClientConnectionStateChoices)
    user = models.ForeignKey(User)
    set_pressed_dt = models.DateTimeField(null=True, blank=True)
    sets_found = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)
    last_access = models.DateTimeField(default=datetime.datetime.now)

    def press_set(self):
        self.set_pressed_dt = datetime.datetime.now()
        self.state = GameSessionState.SET_PRESSED

    def set_in_time(self):
        return self.set_pressed_dt + PRESSED_SET_TIMEOUT > \
            datetime.datetime.now() if self.set_pressed_dt else \
            False

    def serialize(self, current_user_id):
        return {'game': self.game_id,
                'state': self.get_state_display(),
                'client_state': self._get_client_state(),
                'user_id': self.user.id,
                'me': self.user.id == current_user_id,
                'sets_found': self.sets_found,
                'failures': self.failures,
                'user_name': self.name}

    def update(self):
        self.last_access = datetime.datetime.now()
        self.client_state = ClientConnectionState.ACTIVE
        self.save()

    def _get_client_state(self):
        now = datetime.datetime.now()
        if self.last_access + CLIENT_LOST_TIMEOUT < now:
            return ClientConnectionState.LOST
        if self.last_access + CLIENT_IDLE_TIMEOUT < now:
            return ClientConnectionState.IDLE
        return ClientConnectionState.ACTIVE

    @property
    def name(self):
        if self.user.first_name or self.user.last_name:
            return u"%s %s" % (self.user.first_name, self.user.last_name)
        else:
            return self.user.username
