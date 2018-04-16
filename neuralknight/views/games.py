from cornice import Service
from itertools import islice
from uuid import uuid4

from ..models import Board

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
    # POST /issue-agent {id: active_game} -> {'id': uuid}
    active_game = str(uuid4())
    GAMES[active_game] = Board()
    return {'id': active_game}


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
        it = CURSORS[cursor]
    else:
        board = GAMES[request.matchdict['game']]
        it = CURSORS[cursor] = board.lookahead_boards(
            request.GET.get('lookahead', 1))
    states = list(islice(it, 20))
    if len(states) < 20:
        cursor = None
    return {
        'cursor': cursor,
        'boards': [[b.board for b in btup] for btup in states]}


@game_interaction.put()
def put_state(request):
    """
    Make a move to a new state on the board.
    """
    # PUT /agent/{id} -> {}
    game = request.matchdict['game']
    GAMES[game] = GAMES[game].update(request.PUT['state'])
    return {'end': not GAMES[request.matchdict['game']]}
