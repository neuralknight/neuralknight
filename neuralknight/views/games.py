import requests

from concurrent.futures import ThreadPoolExecutor
from cornice import Service
from itertools import islice
from uuid import uuid4

from ..models import Board

executor = ThreadPoolExecutor()

games = Service(
    name='games', path='/v1.0/games', description='Create game')
game_states = Service(
    name='game_states',
    path='/v1.0/games/{game}/states',
    description='Game states')
game_interaction = Service(
    name='game_interaction',
    path='/v1.0/games/{game}',
    description='Game interaction')

CURSORS = {}
GAMES = {}


@games.post()
def post_game(request):
    """
    Create a new game and provide an id for interacting.
    """
    player1 = request.matchdict.get('id', None)
    active_game = str(uuid4())
    board = Board()
    GAMES[active_game] = board
    active_game = {'id': active_game}
    future = executor.submit(
        requests.POST,
        request.route_url('issue_agent'), post=active_game)
    board.player1 = player1
    future.add_done_callback(
        lambda fut: setattr(board, 'player2', fut.result().json()['id']))
    if player1:
        future = executor.submit(
            requests.PUT,
            request.route_url('agent', agent_id=player1))
        future.add_done_callback(lambda fut: fut)
    return active_game


@game_states.get()
def get_states(request):
    """
    Start or continue a cursor of next board states.
    """
    if 'cursor' in request.GET:
        cursor = request.GET['cursor']
    else:
        cursor = str(uuid4())
    if cursor in CURSORS:
        it = CURSORS.pop(cursor)
    else:
        board = GAMES[request.matchdict['game']]
        it = CURSORS[cursor] = board.lookahead_boards(
            request.GET.get('lookahead', 1))
    states = list(islice(it, 20))
    if len(states) < 20:
        cursor = None
    else:
        cursor = str(uuid4())
        CURSORS[cursor] = it
    return {
        'cursor': cursor,
        'boards': [[b.board for b in btup] for btup in states]}


@game_interaction.get()
def get_state(request):
    """
    Provide current state on the board.
    """
    game = request.matchdict['game']
    return {'board': GAMES[game].board}


@game_interaction.put()
def put_state(request):
    """
    Make a move to a new state on the board.
    """
    game = request.matchdict['game']
    game = GAMES[game] = GAMES[game].update(request.json['state'])
    future = executor.submit(
        requests.PUT,
        request.route_url('agent'), agent_id=game.active_player())
    future.add_done_callback(lambda fut: fut)
    if not game:
        return {'end': True}
    return {'end': False}
