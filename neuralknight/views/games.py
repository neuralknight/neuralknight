import requests

from concurrent.futures import ThreadPoolExecutor, wait
from cornice import Service
from itertools import islice
from json import dumps
from uuid import uuid4

from ..models import Board, TableBoard, TableGame

executor = ThreadPoolExecutor()

games = Service(
    name='games',
    path='/v1.0/games',
    description='Create game')
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
    player1 = request.matchdict.get('id', '')
    player2 = request.matchdict.get('opponent', '')
    game_uuid = str(uuid4())
    board = Board()
    board.player1 = player1

    def set_player_2(fut):
        nonlocal board, game_uuid, player2
        response = fut.result()
        board.player2 = player2 if player2 else response.json().get('id', '')
        table_game = TableGame(
            game=game_uuid,
            player_one=board.player1,
            player_two=board.player2,
            one_won=True,
            two_won=True)
        table_board = TableBoard(
            board_state=dumps(board.board),
            move_num=board.move_count,
            player=board.active_player(),
            game=game_uuid)
        table_board.game_link.append(table_game)
        request.dbsession.add(table_game)
        request.dbsession.add(table_board)

    GAMES[game_uuid] = board
    active_game = {'id': game_uuid}
    future = executor.submit(
        requests.post,
        request.route_url('issue_agent'), data=active_game)
    future.add_done_callback(set_player_2)
    if player1:
        executor.submit(
            requests.put,
            request.route_url('agent', agent_id=player1)
        ).add_done_callback(lambda fut: fut.result())
    wait({future})
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
    state = Board(request.json['state'])
    game_uuid = request.matchdict['game']
    moving_player = board.active_player()
    GAMES[game_uuid] = GAMES[game_uuid].update(state)
    board = GAMES[game_uuid]
    executor.submit(
        requests.put,
        request.route_url('agent', agent_id=board.active_player())
    ).add_done_callback(lambda fut: fut.result())
    table_game = request.dbsession.query(TableGame).filter(
        TableGame.game == game_uuid).first()
    table_board = TableBoard(
        board_state=dumps(board.board),
        move_num=board.move_count,
        player=board.active_player(),
        game=game_uuid)
    table_board.game_link.append(table_game)
    request.dbsession.add(table_board)
    if not board:
        executor.submit(
            requests.put,
            request.route_url('agent', agent_id=moving_player),
            data={'id': moving_player}
        ).add_done_callback(lambda fut: fut.result())
        if board.has_king():
            table_game.one_won = False
            table_game.two_won = False
        elif board.active_player() == table_game.player_one:
            table_game.one_won = False
        else:
            table_game.two_won = False
        return {'end': True}
    return {'end': False}
