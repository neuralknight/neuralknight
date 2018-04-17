import requests

from uuid import uuid4
from copy import deepcopy

from .board_constants import INITIAL_BOARD
import neuralknight


class BaseBoard:
    GAMES = {}

    @classmethod
    def get_game(cls, _id):
        """
        Provide game matching id.
        """
        return cls.GAMES[_id]

    def __init__(self, _id, board=None):
        if _id:
            self.id = _id
        else:
            self.id = str(uuid4())
        self.GAMES[self.id] = self
        if board:
            self.board = board
        else:
            self.board = deepcopy(INITIAL_BOARD)

    def request(self, method, resource, *args, data=None, json=None, **kwargs):
        if neuralknight.testapp:
            if method == 'POST':
                return neuralknight.testapp.post_json(resource, data).json
            if method == 'PUT':
                return neuralknight.testapp.put(resource, json).json
            if method == 'GET':
                return neuralknight.testapp.get(resource, data).json
        if method == 'POST':
            self.executor.submit(
                requests.post, f'{ self.API_URL }{ resource }', **kwargs
            ).add_done_callback(self.handle_future)
        if method == 'PUT':
            self.executor.submit(
                requests.put, f'{ self.API_URL }{ resource }', **kwargs
            ).add_done_callback(self.handle_future)
        if method == 'GET':
            self.executor.submit(
                requests.get, f'{ self.API_URL }{ resource }', **kwargs
            ).add_done_callback(self.handle_future)

    def close(self):
        del self.GAMES[self.id]

    def current_state_v1(self):
        """
        Provide REST view of game state.
        """
        return {'board': self.board}

    def poke_player(self, end, active_player=None):
        """
        Inform active player of game state.
        """
        self.request('PUT', f'/agent/{ active_player or self.active_player }', data={'end': end})
