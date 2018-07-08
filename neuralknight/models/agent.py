import os
import requests

from operator import methodcaller
from uuid import uuid4

from . import base_agent

import neuralknight


class Agent:
    """
    Slayer of chess
    """

    AGENT_POOL = {}
    if os.environ.get('PORT', ''):
        PORT = os.environ['PORT']
    else:
        PORT = 8080
    API_URL = 'http://localhost:{}'.format(PORT)

    @classmethod
    def get_agent(cls, _id):
        """
        Provide game matching id.
        """
        return cls.AGENT_POOL[_id]

    def __init__(
            self,
            game_id, player, lookahead=1,
            delegate=base_agent.Agent, *args, **kwargs):
        if isinstance(delegate, str):
            delegate = base_agent.AGENTS.get(delegate, base_agent.Agent)
        self.agent_id = str(uuid4())
        self.AGENT_POOL[self.agent_id] = self
        self.delegate = delegate(*args, **kwargs)
        self.game_id = game_id
        self.game_over = False
        self.lookahead = lookahead
        self.player = player
        self.request_count = 0
        self.request_count_data = 0
        self.join_game()

    def request(self, method, resource, *args, json=None, **kwargs):
        if neuralknight.testapp:
            if method == 'POST':
                return neuralknight.testapp.post_json(resource, json).json
            if method == 'PUT':
                return neuralknight.testapp.put_json(resource, json).json
            if method == 'GET':
                return neuralknight.testapp.get(resource, json).json
        if method == 'POST':
            return requests.post(f'{ self.API_URL }{ resource }', json=json, **kwargs).json()
        if method == 'PUT':
            return requests.put(f'{ self.API_URL }{ resource }', json=json, **kwargs).json()
        if method == 'GET':
            return requests.get(f'{ self.API_URL }{ resource }', data=json, **kwargs).json()

    def close(self):
        self.AGENT_POOL.pop(self.agent_id, None)
        return {}

    def get_boards(self, cursor):
        '''Retrieves potential board states'''
        params = {'lookahead': self.lookahead}
        if cursor:
            params['cursor'] = cursor
        return self.request('GET', '/v1.0/games/{}/states'.format(self.game_id), params=params)

    def get_boards_cursor(self):
        cursor = True
        while cursor:
            board_options = self.get_boards(cursor)
            cursor = board_options['cursor']
            self.request_count += 1
            self.request_count_data += len(cursor)
            yield tuple(map(
                lambda boards: tuple(map(
                    lambda board: tuple(map(bytes.fromhex, board)),
                    boards)),
                board_options['boards']))

    def get_state(self):
        '''Gets current board state'''
        if self.game_over:
            return {'end': True}
        data = self.request('GET', f'/v1.0/games/{ self.game_id }')
        return data['state']

    def join_game(self):
        self.request('POST', f'/v1.0/games/{ self.game_id }', json={'id': self.agent_id})

    def play_round(self):
        '''Play a game round'''
        print(self.request_count, self.request_count_data)
        return self.put_board(self.delegate.play_round(self.get_boards_cursor()))

    def put_board(self, board):
        '''Sends move selection to board state manager'''
        data = {'state': tuple(map(methodcaller('hex'), board))}
        data = self.request('PUT', f'/v1.0/games/{ self.game_id }', json=data)
        self.game_over = data.get('end', False)
        if self.game_over:
            return self.close()
        if data.get('invalid', False):
            return self.play_round()
        return data
