# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from annoying.decorators import ajax_request, render_to

from game.models import Game, GameSession, GameSessionState, ClientConnectionState, get_uid
from game.utils import Card, is_set
from users.models import WaitingUser
from game.constants import *

@render_to('game/game_screen.html')
def game_screen(request, game_id):
    return {'game_id': game_id}


@ajax_request
def start_game(request):
    user = request.user
    qs = GameSession.objects.\
        filter(user=user, game__finished=False).exclude(client_state=ClientConnectionState.LOST)
    if qs.count():
        gs = qs.all()[0]
        return {'status': 302,
                'url': reverse(game_screen, kwargs={'game_id': gs.game.id})}
    wu = WaitingUser.objects.get_or_create(user=user)[0].update()
    last_poll_guard = datetime.datetime.now() - WAITING_USER_TIMEOUT
    opponents = WaitingUser.objects.\
        filter(last_poll__gt=last_poll_guard).\
        exclude(user=user).all()
    if opponents:
        opponent = opponents[0]
        game_id = get_uid()
        game = Game.objects.create(id=game_id)
        GameSession.objects.create(game=game, user=user)
        GameSession.objects.create(game=game, user=opponent.user)
        wu.delete()
        opponent.delete()
        return {'status': '302',
                'url': reverse(game_screen, kwargs={'game_id': game_id})}
    return {'status': 'polling'}


@ajax_request
def get_status(request, game_id):
    game = Game.objects.get(id=game_id)
    GameSession.objects.get(game=game, user=request.user).update()
    users = [gs.serialize(request.user.id) for gs in \
        game.gamesession_set.all()]
    desc_cards = game.desk_cards_list
    desc_cards.extend(game.pop_cards(quantity=12 - len(desc_cards)))
    rem_cards_cnt = len(game.rem_cards_list)
    return {'users': users,
            'cards': [{'id': card_id,
                       'class': Card(id=card_id).as_text()} \
                        for card_id in desc_cards],
            'cards_left': rem_cards_cnt,
            'game': {
                'is_finished': game.is_finished(),
                'leader': game.leader}}


@ajax_request
def put_set_mark(request, game_id):
    game = Game.objects.get(id=game_id)
    if not game.gamesession_set.\
            filter(state=GameSessionState.SET_PRESSED).\
            count():
        gs = game.gamesession_set.get(user=request.user)
        gs.press_set()
    return {'success': True}


@ajax_request
def check_set(request, game_id):
    game = Game.objects.get(id=game_id)
    gs = game.gamesession_set.get(user=request.user)
    if gs.set_received_in_time():
        ids = request.REQUEST.get('ids')
        if not ids:
            return {'success': False, 'msg': 'Empty ids'}
        ids_lst = map(int, ids.split(','))
        if len(ids_lst) != 3:
            return {'success': False, 'msg': 'Ids len != 3'}
        desk_cards_lst = game.desk_cards_list
        if not all(card_id in desk_cards_lst for card_id in ids_lst):
            return {'success': False, 'msg': 'Not all card were on desk'}
        cards = [Card(id=card_id) for card_id in ids_lst]
        if not is_set(*cards):
            gs.state = GameSessionState.SET_PENALTY
            gs.sets_found -= 1
            gs.save()
        else:
            gs.state = GameSessionState.IDLE
            gs.sets_found += 1
            gs.save()
            # Remove cards from desc list
            game.drop_cards(*ids_lst)
        # Update status to IDLE for other game sessions:
        for gs_other in game.gamesession_set.exclude(user=request.user).all():
            gs_other.state = GameSessionState.IDLE
            gs_other.save()
    return {'success': True}
