# -*- coding: utf-8 -*-
import datetime
from django.contrib.sessions.models import Session
from django.views.decorators.http import require_POST
from game.models import Game, GameSession
from annoying.decorators import ajax_request, render_to
from django.shortcuts import redirect


@render_to('game/waiting_screen.html')
def waiting_screen(request):
    sessions = Session.objects.filter(expire_date__gt=datetime.datetime.now()).all()
    users = [s.session_key for s in sessions if s.session_key != request.session.session_key]
    return {'waiting_users': users}


@render_to('game/game_screen.html')
def game_screen(request):
    return {}


@require_POST
def start_game(request):
    opponent = request.POST['opponent']
    g_session = GameSession.objects.get_or_create(
        user=request.session.session_key)[0]
    g_session_other = GameSession.objects.get_or_create(user=opponent)[0]
    game = Game.objects.create()
    g_session.game = game
    g_session_other.game = game
    g_session.save()
    g_session_other.save()
    return redirect(game_screen)


@ajax_request
def status(request):
    game_session, created = GameSession.objects.\
        get_or_create(user=request.session.session_key)
    return {'session': game_session.serialize()}
