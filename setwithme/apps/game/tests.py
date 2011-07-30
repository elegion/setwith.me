# -*- coding: utf-8 -*-

import uuid
from django.test import TestCase
from game.utils import *
from game.models import *
from setwithme.apps.game.utils import Card


class GameModelTestCase(TestCase):

    def test_game_session_creation(self):
        user_id = uuid.uuid4().hex
        game_session, created = GameSession.objects.get_or_create(user=user_id)
        self.assertTrue(created)
        self.assertIsNotNone(game_session)
        game_session, created = GameSession.objects.get_or_create(user=user_id)
        self.assertFalse(created)
        self.assertIsNotNone(game_session)

    def test_game_creation(self):
        user_id_1 = uuid.uuid4().hex
        game_session_1 = GameSession.objects.get_or_create(user=user_id_1)[0]
        user_id_2 = uuid.uuid4().hex
        game_session_2 = GameSession.objects.get_or_create(user=user_id_2)[0]
        game = Game.objects.create()
        self.assertIsNotNone(game)
        game_session_1.game = game
        game_session_2.game = game
        game_session_1.save()
        game_session_2.save()

    def test_game_get_cards(self):
        game = Game.objects.create()
        cards = game.rem_cards_list
        self.assertEqual(list(xrange(81)), cards)

    def test_game_drop_cards(self):
        game = Game.objects.create()
        shown_cards = game.pop_cards()
        self.assertEqual(len(game.rem_cards_list), 81 - 3)
        self.assertEqual(len(game.desk_cards_list), 3)
        game.drop_cards(*shown_cards)
        self.assertEqual(len(game.desk_cards_list), 0)


class CardIdsTestCase(TestCase):
    def test(self):
        for n in range(80):
            self.assertEqual(Card(text=Card(id=n).as_text()).as_id(), n)
