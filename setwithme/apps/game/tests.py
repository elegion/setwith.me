# -*- coding: utf-8 -*-

import uuid
from django.template.defaultfilters import random
from django.test import TestCase
from game.utils import *
from game.models import *
from setwithme.apps.game.utils import Card


class GameModelTestCase(TestCase):

    def test_game_session_creation(self):
        user = self._create_user()
        game_session, created = GameSession.objects.get_or_create(user=user)
        self.assertTrue(created)
        self.assertIsNotNone(game_session)
        game_session, created = GameSession.objects.get_or_create(user=user)
        self.assertFalse(created)
        self.assertIsNotNone(game_session)

    def test_game_creation(self):
        user_1 = self._create_user()
        game_session_1 = GameSession.objects.get_or_create(user=user_1)[0]
        user_2 = self._create_user()
        game_session_2 = GameSession.objects.get_or_create(user=user_2)[0]
        game = Game.objects.create()
        self.assertIsNotNone(game)
        game_session_1.game = game
        game_session_2.game = game
        game_session_1.save()
        game_session_2.save()
        game.pop_cards(quantity=12)
        return game

    def test_game_drop_cards(self):
        game = Game.objects.create()
        shown_cards = game.pop_cards()
        self.assertEqual(len(game.rem_cards_list), 81 - 3 - 12)
        self.assertEqual(len(game.desk_cards_list), 3 + 12)
        game.drop_cards(*shown_cards)
        self.assertEqual(len(game.desk_cards_list), 12)

    def test_has_sets(self):
        game = self.test_game_creation()
        cards = sorted(game.desk_cards_list)
        for ncard1, card1 in enumerate(cards):
            for ncard2, card2 in enumerate(cards[ncard1 + 1:]):
                for ncard3, card3 in enumerate(cards[ncard2 + ncard1 + 1 + 1:]):
                    if is_set(Card(id=card1), Card(id=card2), Card(id=card3)):
                        self.assertEqual(True, game.has_sets())
                        return
        self.assertEqual(False, game.has_sets())

    def test_game_rem_cards(self):
        game = Game.objects.create()
        rem_lst = game.rem_cards_list
        self.assertEqual(len(rem_lst), 81 - 12)
        desk_lst = game.desk_cards_list
        self.assertEqual(len(desk_lst), 12)
        popped_lst = game.pop_cards(quantity=12)
        self.assertEqual(len(popped_lst), 12)
        desk_lst = game.desk_cards_list
        self.assertEqual(len(desk_lst), 12 + 12)
        rem_lst = game.rem_cards_list
        self.assertEqual(len(rem_lst), 81 - 12 - 12)

    def _create_user(self):
        user_uuid = unicode(uuid.uuid4().hex)[:30]
        user, created = User.objects.get_or_create(
            username=user_uuid,
            defaults={'first_name': 'Anon %s' % (user_uuid[:4],)})
        return user


class UtilsTestCase(TestCase):
    def test_ids(self):
        for n in range(80):
            self.assertEqual(Card(text=Card(id=n).as_text()).as_id(), n)

    def test_is_set(self):
        data = [(True, 0 ,3 ,6),
        (True, 0, 1, 2),
        (True, 15, 16, 17),
        (False, 8, 9, 10),
        (False, 14, 16, 17),]

        for d in data:
            self.assertEqual(d[0],
                             is_set(Card(id=d[1]),
                                    Card(id=d[2]),
                                    Card(id=d[3])),
                             '%s: %d, %d, %d' % d)
