# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand

from game.models import Game, ClientConnectionState


LAST_SESSION_UPDATE_TIMEOUT = datetime.timedelta(minutes=2)


class Command(BaseCommand):
    help = """ Obtains twitter_id by screen_name for users from old DB
     and updates twitter_id field """
    args = 'old_db_name'

    def handle(self, *args, **options):
        cleaned_cnt = 0
        for game in Game.objects.filter(finished=False):
            now = datetime.datetime.now()
            last_access_guard = now - LAST_SESSION_UPDATE_TIMEOUT
            gs_total_cnt = game.gamesession_set.count()
            gs_old_cnt = game.gamesession_set.filter(
                last_access__lt=last_access_guard).\
                count()
            if gs_old_cnt == gs_total_cnt:
                for gs in game.gamesession_set.all():
                    gs.client_state = ClientConnectionState.LOST
                    gs.save()
                game.finished = True
                game.save()
                cleaned_cnt += 1
        if cleaned_cnt:
            print "Cleaned %s zombie games" % cleaned_cnt
