# -*- coding: utf-8 -*-
import random
import datetime
import uuid

from django.db import models
from django.contrib.auth.models import User

from game import constants
from setwithme.apps.game.utils import is_set, Card
from users.models import get_user_json


get_uid = lambda : unicode(uuid.uuid4().hex)


attributes_order = ('color', 'symbol', 'number', 'shading')
attributes = {'color': ('red', 'green', 'purple'),
              'symbol': ('oval', 'squiggle', 'diamond'),
              'number': (1, 2, 3),
              'shading': ('solid', 'open', 'striped')}


ids = range(81)
random.shuffle(ids)

def get_desk():
    return ','.join(
        map(str,
            ids[:constants.CARDS_ON_DESK]))

def get_remaining():
    return ','.join(
        map(str,
            ids[constants.CARDS_ON_DESK:]))


class Game(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    finished = models.BooleanField(default=False)
    start = models.DateTimeField(default=datetime.datetime.now)
    end = models.DateTimeField(null=True, default=None)
    remaining_cards = models.CommaSeparatedIntegerField(
        max_length=250, default=get_remaining)
    desk_cards = models.CommaSeparatedIntegerField(
        max_length=250,
        default=get_desk)

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

    def replace_cards(self, *cards_to_remove):
        cards = self.desk_cards_list
        assert len(cards) >= len(cards_to_remove)
        left_cards = self.rem_cards_list
        for card in cards_to_remove:
            try:
                new_card = random.choice(left_cards)
            except IndexError:
                cards.remove(card)
            else:
                left_cards.remove(new_card)
                cards[cards.index(card)] = new_card
        self.rem_cards_list = left_cards
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

    @property
    def last_action_time(self):
        last_action = self.gamesession_set.filter(set_pressed_dt__isnull=False)\
                .order_by('-set_pressed_dt')
        if last_action.count():
            return last_action[0].set_pressed_dt
        return self.start

    @property
    def cards_to_pop(self):
        cards_to_pop = constants.CARDS_ON_DESK
        now = datetime.datetime.now()
        time_since_last_action = now - self.last_action_time
        if time_since_last_action > datetime.timedelta(seconds=constants.CARD_ADD_INTERVAL):
            cards_to_pop += min(
                constants.MAX_ADDITIONAL_CARDS,
                int(time_since_last_action.seconds / float(constants.CARD_ADD_INTERVAL))
            )
        return cards_to_pop

    def has_sets(self):
        #FIXME: cache that and update on cards removal
        cards = sorted(self.desk_cards_list)
        for ncard1, card1 in enumerate(cards):
            for ncard2, card2 in enumerate(cards[ncard1+1:]):
                for ncard3, card3 in enumerate(cards[ncard2+ncard1+1+1:]):
                    if is_set(Card(id=card1), Card(id=card2), Card(id=card3)):
                        return True
        return False

    def count_sets(self):
        cnt = 0
        cards = sorted(self.desk_cards_list)
        for ncard1, card1 in enumerate(cards):
            for ncard2, card2 in enumerate(cards[ncard1+1:]):
                for ncard3, card3 in enumerate(cards[ncard2+ncard1+1+1:]):
                    if is_set(Card(id=card1), Card(id=card2), Card(id=card3)):
                        cnt += 1
        return cnt

    def is_finished(self):
        has_cards = len(self.remaining_cards) > 0
        has_sets = self.has_sets()
        active_players = self.gamesession_set\
            .exclude(client_state=ClientConnectionState.LOST)\
            .exclude(state=GameSessionState.LEFT).count()
        is_finished = (active_players < 2) or (not has_cards and not has_sets)
        if is_finished:
            self.finished = True
            self.save()
        return is_finished

    @property
    def leader(self):
        """Determines leading user, can be user after game end for determining winner"""
        scores = self.gamesession_set.exclude(client_state=ClientConnectionState.LOST)\
            .exclude(state=GameSessionState.LEFT)\
            .values_list('sets_found', 'failures', 'user')
        return max([(score[0] - score[1], score[2]) for score in scores])[1]


class GameSessionState:
    NORMAL = "NORMAL"
    LEFT = "LEFT"
    SET_PRESSED = "SET_PRESSED"
    SET_PENALTY = "SET_PENALTY"
    SET_ANOTHER_USER = "SET_ANOTHER_USER"


GameSessionStateChoices = (
    (GameSessionState.NORMAL, 'Normal'),
    (GameSessionState.LEFT, 'Left'),
    (GameSessionState.SET_PRESSED, 'Set pressed'),
    (GameSessionState.SET_PENALTY, 'Set penalty'),
    (GameSessionState.SET_ANOTHER_USER, 'Set another user'),
)


class ClientConnectionState:
    ACTIVE = "ACTIVE"
    IDLE = "IDLE" #no status requests in 30 sec
    LOST = "LOST" #no status requests in 60 sec


ClientConnectionStateChoices = (
    (ClientConnectionState.ACTIVE, 'Active'),
    (ClientConnectionState.IDLE, 'Idle'),
    (ClientConnectionState.LOST, 'Lost'),
)


class GameSession(models.Model):
    game = models.ForeignKey(Game, null=True)
    state = models.CharField(
        max_length=50,
        default=GameSessionState.NORMAL,
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
    left = models.BooleanField(default=False)

    def press_set(self):
        self.set_pressed_dt = datetime.datetime.now()
        self.state = GameSessionState.SET_PRESSED
        self.save()

    def set_received_in_time(self):
        return self.set_pressed_dt + constants.PRESSED_SET_TIMEOUT > \
            datetime.datetime.now() if self.set_pressed_dt else \
            False

    def serialize(self, current_user_id):
        return {'game': self.game_id,
                'state': self._get_game_state(),
                'client_state': self._get_client_state(),
                'user_id': self.user.id,
                'me': self.user.id == current_user_id,
                'sets_found': self.sets_found,
                'failures': self.failures,
                'score': self.score,
                'user_name': self.name,
                'user_data': get_user_json(self.user)}

    def update(self):
        self.last_access = datetime.datetime.now()
        self.client_state = ClientConnectionState.ACTIVE
        self.save()

    def _fix_game_state(self):
        now = datetime.datetime.now()
        state_pressed = self.state == GameSessionState.SET_PRESSED
        if state_pressed:
            if not self.set_pressed_dt or (self.set_pressed_dt and\
                ((now > self.set_pressed_dt + constants.PRESSED_SET_TIMEOUT))):
                for gs in self.game.gamesession_set.filter(state=GameSessionState.SET_ANOTHER_USER):
                    gs.state = GameSessionState.NORMAL
                    gs.save()
                self.state = GameSessionState.SET_PENALTY
                self.failures += 1
                self.save()

        if not self.game.gamesession_set.exclude(state=GameSessionState.SET_PENALTY).count():
            self.game.gamesession_set.all().update(state=GameSessionState.NORMAL)

        self.game.gamesession_set\
            .filter(state=GameSessionState.SET_PENALTY,
                    set_pressed_dt__lte=now-constants.CLIENT_PENALTY_TIMEOUT)\
            .update(state=GameSessionState.NORMAL)

    def _get_game_state(self):
        self._fix_game_state()
        return self.state

    def _get_client_state(self):
        now = datetime.datetime.now()
        if self.last_access + constants.CLIENT_LOST_TIMEOUT < now:
            self.client_state = ClientConnectionState.LOST
            self.save()
            return self.client_state
        if self.last_access + constants.CLIENT_IDLE_TIMEOUT < now:
            self.client_state = ClientConnectionState.IDLE
            self.save()
            return self.client_state
        return ClientConnectionState.ACTIVE

    @property
    def name(self):
        if self.user.first_name or self.user.last_name:
            return u"%s %s" % (self.user.first_name, self.user.last_name)
        else:
            return self.user.username

    @property
    def score(self):
        return self.sets_found - self.failures

class Facts(models.Model):
    text = models.CharField(max_length=255)
