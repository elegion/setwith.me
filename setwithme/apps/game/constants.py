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

WAITING_USER_TIMEOUT = getattr(
    settings,
    "WAITING_USER_TIMEOUT",
    datetime.timedelta(seconds=60))

CARDS_ON_DESK = getattr(
    settings,
    "CARDS_ON_DESK",
    16)
