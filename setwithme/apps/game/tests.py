# -*- coding: utf-8 -*-

import uuid
from django.test import TestCase
from game.utils import *
from game.models import *

class IsSetTestCase(TestCase):

    def test_match(self):
        self.assertTrue(match(Color.red, Color.red, Color.red))
        self.assertTrue(match(Color.red, Color.green, Color.purple))
        self.assertFalse(match(Color.red, Color.green, Color.green))

    def test_set(self):
        first = Card(1, Shading.opened, Color.green, Symbol.diamond)
        second = Card(2, Shading.opened, Color.green, Symbol.diamond)
        third = Card(3, Shading.opened, Color.green, Symbol.diamond)
        self.assertTrue(is_set(first, second,third))

        first = Card(1, Shading.opened, Color.green, Symbol.diamond)
        second = Card(2, Shading.solid, Color.purple, Symbol.oval)
        third = Card(3, Shading.striped, Color.red, Symbol.squiggle)
        self.assertTrue(is_set(first, second,third))

        first = Card(1, Shading.opened, Color.green, Symbol.diamond)
        second = Card(2, Shading.opened, Color.purple, Symbol.oval)
        third = Card(3, Shading.striped, Color.red, Symbol.squiggle)
        self.assertFalse(is_set(first, second,third))


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
        cards = game.get_cards()
        self.assertEqual(list(xrange(81)), cards)

    def test_game_remove_cards(self):
        game = Game.objects.create()
        game.remove_cards(1, 4, 7)
        lst = range(81)
        lst.remove(1)
        lst.remove(4)
        lst.remove(7)
        cards = game.get_cards()
        self.assertEqual(lst, cards)
