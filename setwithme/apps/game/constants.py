# -*- coding: utf-8 -*-
import datetime
from django.conf import settings

PRESSED_SET_TIMEOUT = getattr(
    settings,
    "PRESSED_SET_TIMEOUT",
    datetime.timedelta(seconds=10))

CLIENT_IDLE_TIMEOUT = getattr(
    settings,
    "CLIENT_IDLE_TIMEOUT",
    datetime.timedelta(seconds=30))

CLIENT_LOST_TIMEOUT = getattr(
    settings,
    "CLIENT_LOST_TIMEOUT",
    datetime.timedelta(seconds=60))

CLIENT_PENALTY_TIMEOUT = getattr(
    settings,
    'CLIENT_PENALTY_TIMEOUT',
    datetime.timedelta(seconds=120)
)

WAITING_USER_TIMEOUT = getattr(
    settings,
    "WAITING_USER_TIMEOUT",
    datetime.timedelta(seconds=60))

GAME_JOIN_WAIT_TIMEOUT = getattr(
    settings,
    "GAME_JOIN_WAIT_TIMEOUT",
    datetime.timedelta(seconds=15))

CARDS_ON_DESK = getattr(
    settings,
    "CARDS_ON_DESK",
    12)

MAX_ADDITIONAL_CARDS = getattr(
    settings,
    "MAX_ADDITIONAL_CARDS",
    3
)

CARD_ADD_INTERVAL = getattr(
    settings,
    "CARD_ADD_INTERVAL",
    60
)

CANCEL_SET_CHECK = getattr(
    settings,
    "CANCEL_SET_CHECK",
    False)
