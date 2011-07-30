# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from annoying.decorators import ajax_request, render_to

from game.models import Game, GameSession, State, ClientState, get_uid
from game.utils import Card
from users.models import WaitingUser
from game.constants import *

@render_to('game/game_screen.html')
def game_screen(request, game_id):
    return {'game_id': game_id}


@ajax_request
def start_game(request):
    user_id = request.session.session_key
    qs = GameSession.objects.\
        filter(user=user_id, client_state=ClientState.ACTIVE)
    if qs.count():
        gs = qs.all()[0]
        return {'status': 302,
                'url': reverse(game_screen, kwargs={'game_id': gs.game.id})}
    wu = WaitingUser.objects.get_or_create(user=user_id)[0].update()
    last_poll_guard = datetime.datetime.now() - WAITING_USER_TIMEOUT
    opponents = WaitingUser.objects.\
        filter(last_poll__gt=last_poll_guard).\
        exclude(user=user_id).all()
    if opponents:
        opponent = opponents[0]
        game_id = get_uid()
        game = Game.objects.create(id=game_id)
        GameSession.objects.create(game=game, user=user_id)
        GameSession.objects.create(game=game, user=opponent.user)
        wu.delete()
        opponent.delete()
        return {'status': '302',
                'url': reverse(game_screen, kwargs={'game_id': game_id})}
    return {'status': 'polling'}


@ajax_request
def get_status(request, game_id):
    game = Game.objects.get(id=game_id)
    self_id = request.session.session_key
    GameSession.objects.get(game=game, user=self_id).update()
    users = [gs.serialize(self_id) for gs in \
        game.gamesession_set.all()]
    desc_cards = game.desk_cards_list
    rem_cards_cnt = len(game.rem_cards_list)
    desc_cards.extend(game.pop_cards(quantity=12 - len(desc_cards)))
    return {'users': users,
            'cards': [Card(id=card_id).as_text() for card_id in desc_cards],
            'cards_left': rem_cards_cnt}


@ajax_request
def put_set_mark(request, game_id):
    game = Game.objects.get(id=game_id)
    self_id = request.session.session_key
    if not game.gamesession_set.filter(state=State.SET_PRESSED).count():
        gs = game.gamesession_set.get(user=self_id)
        gs.press_set()
    return {'success': True}


@ajax_request
def check_set(request, game_id):
    game = Game.objects.get(id=game_id)
    self_id = request.session.session_key
    gs = game.gamesession_set.get(user=self_id)
    if gs.set_in_time():
        # TODO: check if set was correct
        # Process set, remove cards, return new
        pass
    return {'success': True}
