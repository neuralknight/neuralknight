import os
import requests

from uuid import uuid4

from .board_model import BoardModel, CursorDelegate
import neuralknight


class NoBoard(Exception):
    pass


class BaseBoard:
    GAMES = {}
    if os.environ.get('PORT', ''):
        PORT = os.environ['PORT']
    else:
        PORT = 8080
    API_URL = 'http://localhost:{}'.format(PORT)

    @classmethod
    def get_game(cls, _id):
        """
        Provide game matching id.
        """
        if _id in cls.GAMES:
            return cls.GAMES[_id]
        raise NoBoard

    def __init__(self, board, _id=None, active_player=True):
        if _id:
            self.id = _id
        else:
            self.id = str(uuid4())
        self.GAMES[self.id] = self
        if isinstance(board, BoardModel):
            self._board = board
        else:
            self._board = BoardModel(board)
        self.board = self._board.board
        self.cursor_delegate = CursorDelegate()
        self._active_player = active_player
        self.player1 = None
        self.player2 = None

    def __bool__(self):
        """
        Ensure active player king on board.
        """
        return bool(self._board)

    def __contains__(self, piece):
        """
        Ensure piece on board.
        """
        return piece in self._board

    def __iter__(self):
        """
        Provide next boards at one lookahead.
        """
        return self._board.lookahead_boards(1)

    def request(self, method, resource, *args, json=None, **kwargs):
        if neuralknight.testapp:
            if method == 'POST':
                return neuralknight.testapp.post_json(resource, json).json
            if method == 'PUT':
                return neuralknight.testapp.put_json(resource, json).json
            if method == 'GET':
                return neuralknight.testapp.get(resource, json).json
        if method == 'POST':
            self.executor.submit(
                requests.post, f'{ self.API_URL }{ resource }', data=json, **kwargs
            ).add_done_callback(self.handle_future)
        if method == 'PUT':
            self.executor.submit(
                requests.put, f'{ self.API_URL }{ resource }', json=json, **kwargs
            ).add_done_callback(self.handle_future)
        if method == 'GET':
            self.executor.submit(
                requests.get, f'{ self.API_URL }{ resource }', data=json, **kwargs
            ).add_done_callback(self.handle_future)

    def active_player(self):
        """
        UUID of active player.
        """
        if self._active_player:
            return self.player1
        return self.player2

    def close(self):
        self.GAMES.pop(self.id, None)
        return {}

    def current_state_v1(self):
        """
        Provide REST view of game state.
        """
        return {'state': self.board}

    def handle_future(self, future):
        """
        Handle a future from and async request.
        """
        future.result().json()

    def prune_lookahead_boards(self, n=4):
        return self._board.prune_lookahead_boards(n)

    def lookahead_boards(self, n=4):
        return self._board.lookahead_boards(n)

    def poke_player(self, end, active_player=None):
        """
        Inform active player of game state.
        """
        self.request('PUT', f'/agent/{ active_player or self.active_player() }', json={'end': end})

    def update(self, state):
        """
        Validate and return new board state.
        """
        board = type(self)(
            self._board.update(tuple(map(bytes.fromhex, state))), self.id, not self._active_player)
        board.player1 = self.player1
        board.player2 = self.player2
        return board
