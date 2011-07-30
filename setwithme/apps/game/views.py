# -*- coding: utf-8 -*-
import datetime
import uuid
from django.contrib.sessions.models import Session
from django.views.decorators.http import require_POST
from game.models import Game, GameSession, State
from users.models import WaitingUser
from annoying.decorators import ajax_request, render_to
from django.shortcuts import redirect
from setwithme.apps.game.utils import Card

WAITING_USER_TIMEOUT = 60


@render_to('game/waiting_screen.html')
def waiting_screen(request):
    sessions = Session.objects.filter(expire_date__gt=datetime.datetime.now()).all()
    users = [s.session_key for s in sessions if s.session_key != request.session.session_key]
    return {'waiting_users': users}


@render_to('game/game_screen.html')
def game_screen(request, game_id):
    return {'game_id': game_id}


@ajax_request
def start_game(request):
    user_id = request.session.session_key
    wu = WaitingUser.objects.get_or_create(user=user_id)[0].update()
    last_poll_guard = datetime.datetime.now() - \
                      datetime.timedelta(seconds=WAITING_USER_TIMEOUT)
    opponents = WaitingUser.objects.\
        filter(last_poll__gt=last_poll_guard).\
        exclude(user=user_id).all()
    if opponents:
        opponent = opponents[0]
        game_id = unicode(uuid.uuid4())
        game = Game.objects.create(uid=game_id)
        GameSession.objects.create(game=game, user=user_id)
        GameSession.objects.create(game=game, user=opponent.user)
        wu.delete()
        opponent.delete()
        return redirect(game_screen, game_id=game_id)
    return {'status': 'polling'}


@ajax_request
def status(request, game_id):
    game = Game.objects.get(uid=game_id)
    self_id = request.session.session_key
    GameSession.objects.get(game=game_id, user=self_id).update()
    users = [gs.serialize(self_id) for gs in \
        game.gamesession_set.all()]
    return {'users': users,
            'cards': [Card(id=card).as_text() for card in game.cards_list]}


@ajax_request
def put_set(request, game_id):
    game = Game.objects.get(uid=game_id)
    self_id = request.session.session_key
    if not game.gamesession_set.filter(state=State.SET_PRESSED).count():
        gs = game.gamesession_set.get(user=self_id)
        gs.press_set()
    return {'success': True}


@ajax_request
def show_set(request, game_id):
    game = Game.objects.get(uid=game_id)
    self_id = request.session.session_key
    gs = game.gamesession_set.get(user=self_id)
    if gs.set_in_time():
        # TODO: check if set was correct
        # Process set, remove cards, return new
        pass
    return {'success': True}
