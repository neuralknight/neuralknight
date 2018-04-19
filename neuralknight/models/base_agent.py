import requests
from itertools import chain, count, groupby, starmap
from functools import lru_cache, partial
from operator import itemgetter
from random import randint
from statistics import mean
from uuid import uuid4

import neuralknight


@lru_cache(maxsize=1024)
def get_score(leaf, posY, posX, piece, **value_map):
    piece = {
            9 : 'OWN_PAWN',
            7 : 'OWN_KNIGHT',
            3 : 'OWN_BISHOP',
            13: 'OWN_ROOK',
            11: 'OWN_QUEEN',
            5 : 'OWN_KING',

            8 : 'OPP_PAWN',
            6 : 'OPP_KNIGHT',
            2 : 'OPP_BISHOP',
            12: 'OPP_ROOK',
            10: 'OPP_QUEEN',
            4 : 'OPP_KING',
    }.get(piece, 'EMPTY_SPACE')
    piece_values = value_map[piece]
    return piece_values[0] + piece_values[1][posY][posX]


def check_sequence(sequence, **value_map):
    leaf = tuple(map(tuple, sequence[-1]))
    return sum(chain.from_iterable(map(
        lambda posY, row: map(
            lambda posX, piece: get_score(leaf, posY, posX, piece, **value_map),
            count(), row),
        count(), leaf)))


def sequence_grouper(root, sequences, **value_map):
    root_value = mean(map(partial(check_sequence, **value_map), sequences))
    return (round(root_value, 2), root)


class BaseAgent:
    '''Slayer of chess'''

    AGENT_POOL = {}
    PORT = 8080
    API_URL = 'http://localhost:{}'.format(PORT)

    @classmethod
    def get_agent(cls, _id):
        """
        Provide game matching id.
        """
        return cls.AGENT_POOL[_id]

    def __init__(self, game_id, player, lookahead=1):
        self.agent_id = str(uuid4())
        self.player = player
        self.lookahead = lookahead
        self.game_id = game_id
        self.game_over = False
        self.AGENT_POOL[self.agent_id] = self
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

    def evaluate_boards(self, boards):
        '''Determine value for each board state in array of board states

        Inputs:
            boards: Array of board states

        Outputs:
            best_state: The highest valued board state in the array

        '''

        # Piece values
        pawn_val = 100
        knight_val = 320
        bishop_val = 330
        rook_val = 500
        queen_val = 9000
        king_val = 20000

        # pylama:ignore=E201,E203,E231
        # Piece squares - from http://www.chessbin.com/post/Piece-Square-Table
        # Own piece squares
        own_pawn_squares = (
            ( 0,  0,  0,  0,  0,  0,  0,  0),
            (50, 50, 50, 50, 50, 50, 50, 50),
            (10, 10, 20, 30, 30, 20, 10, 10),
            ( 5,  5, 10, 25, 25, 10,  5,  5),
            ( 0,  0,  0, 20, 20,  0,  0,  0),
            ( 5, -5,-10,  0,  0,-10, -5,  5),
            ( 5, 10, 10,-20,-20, 10, 10,  5),
            ( 0,  0,  0,  0,  0,  0,  0,  0),
        )
        own_knight_squares = (
            (-50,-40,-30,-30,-30,-30,-40,-50),
            (-40,-20,  0,  0,  0,  0,-20,-40),
            (-30,  0, 10, 15, 15, 10,  0,-30),
            (-30,  5, 15, 20, 20, 15,  5,-30),
            (-30,  0, 15, 20, 20, 15,  0,-30),
            (-30,  5, 10, 15, 15, 10,  5,-30),
            (-40,-20,  0,  5,  5,  0,-20,-40),
            (-50,-40,-20,-30,-30,-20,-40,-50),
        )
        own_bishop_squares = (
            (-20,-10,-10,-10,-10,-10,-10,-20),
            (-10,  0,  0,  0,  0,  0,  0,-10),
            (-10,  0,  5, 10, 10,  5,  0,-10),
            (-10,  5,  5, 10, 10,  5,  5,-10),
            (-10,  0, 10, 10, 10, 10,  0,-10),
            (-10, 10, 10, 10, 10, 10, 10,-10),
            (-10,  5,  0,  0,  0,  0,  5,-10),
            (-20,-10,-40,-10,-10,-40,-10,-20),
        )
        own_rook_squares = (
             (0,  0,  0,  0,  0,  0,  0,  0),
             (5, 10, 10, 10, 10, 10, 10,  5),
             (-5,  0,  0,  0,  0,  0,  0,  -5),
             (-5,  0,  0,  0,  0,  0,  0,  -5),
             (-5,  0,  0,  0,  0,  0,  0,  -5),
             (-5,  0,  0,  0,  0,  0,  0,  -5),
             (-5,  0,  0,  0,  0,  0,  0,  -5),
             (0,  0,  0,  5,  5,  0,  0,  0),
        )
        own_queen_squares = (
            (-20,-10,-10, -5, -5,-10,-10,-20),
            (-10,  0,  0,  0,  0,  0,  0,-10),
            (-10,  0,  5,  5,  5,  5,  0,-10),
            (-5,  0,  5,  5,  5,  5,  0, -5),
            (0,  0,  5,  5,  5,  5,  0, -5),
            (-10,  5,  5,  5,  5,  5,  0,-10),
            (-10,  0,  5,  0,  0,  0,  0,-10),
            (-20,-10,-10, -5, -5,-10,-10,-20),
        )
        own_king_squares = (
            (-30,-40,-40,-50,-50,-40,-40,-30),
            (-30,-40,-40,-50,-50,-40,-40,-30),
            (-30,-40,-40,-50,-50,-40,-40,-30),
            (-30,-40,-40,-50,-50,-40,-40,-30),
            (-20,-30,-30,-40,-40,-30,-30,-20),
            (-10,-20,-20,-20,-20,-20,-20,-10),
            (20, 20,  0,  0,  0,  0, 20, 20),
            (20, 30, 10,  0,  0, 10, 30, 20),
        )

        # Opp piece squares
        opp_pawn_squares = (
            ( 0,  0,  0,  0,  0,  0,  0,  0),
            (-5,-10,-10, 20, 20,-10,-10, -5),
            (-5,  5, 10,  0,  0, 10,  5, -5),
            ( 0,  0,  0,-20,-20,  0,  0,  0),
            (-5, -5,-10,-25,-25,-10, -5, -5),
            (-10,-10,-20,-30,-30,-20,-10,-10),
            (-50,-50,-50,-50,-50,-50,-50,-50),
            ( 0,  0,  0,  0,  0,  0,  0,  0),
        )
        opp_knight_squares = (
            ( 50, 40, 20, 30, 30, 20, 40, 50),
            ( 40, 20,  0, -5, -5,  0, 20, 40),
            ( 30, -5,-10,-15,-15,-10, -5, 30),
            ( 30,  0,-15,-20,-20,-15,  0, 30),
            ( 30, -5,-15,-20,-20,-15, -5, 30),
            ( 30,  0,-10,-15,-15,-10,  0, 30),
            ( 40, 20,  0,  0,  0,  0, 20, 40),
            ( 50,-40,-20,-30,-30,-20,-40, 50),
        )
        opp_bishop_squares = (
            ( 20, 10, 40, 10, 10, 40, 10, 20),
            ( 10, -5,  0,  0,  0,  0, -5, 10),
            ( 10,-10,-10,-10,-10,-10,-10, 10),
            ( 10,  0,-10,-10,-10,-10,  0, 10),
            ( 10, -5, -5,-10,-10, -5, -5, 10),
            ( 10,  0, -5,-10,-10, -5,  0, 10),
            ( 10,  0,  0,  0,  0,  0,  0, 10),
            ( 20, 10, 40, 10, 10, 40, 10, 20),
        )
        opp_rook_squares = (
             (0,  0,  0, -5, -5,  0,  0,  0),
             (5,  0,  0,  0,  0,  0,  0,  5),
             (5,  0,  0,  0,  0,  0,  0,  5),
             (5,  0,  0,  0,  0,  0,  0,  5),
             (5,  0,  0,  0,  0,  0,  0,  5),
             (5,  0,  0,  0,  0,  0,  0,  5),
             (-5,-10,-10,-10,-10,-10,-10,-5),
             (0,  0,  0,  0,  0,  0,  0,  0),
        )
        opp_queen_squares = (
            ( 20, 10, 10,  5,  5, 10, 10, 20),
            ( 10,  0,  0,  0,  0, -5,  0, 10),
            ( 10,  0, -5, -5, -5, -5, -5, 10),
            (  0,  0, -5, -5, -5, -5,  0,  5),
            (  5,  0, -5, -5, -5, -5,  0,  5),
            ( 10,  0, -5, -5, -5, -5,  0, 10),
            ( 10,  0,  0,  0,  0,  0,  0, 10),
            ( 20, 10, 10,  5,  5, 10, 10, 20),
        )
        opp_king_squares = (
            (-20,-30,-10,  0,  0,-10,-30,-20),
            (-20,-20,  0,  0,  0,  0,-20,-20),
            ( 10, 20, 20, 20, 20, 20, 20, 10),
            ( 20, 30, 30, 40, 40, 30, 30, 20),
            ( 30, 40, 40, 50, 50, 40, 40, 30),
            ( 30, 40, 40, 50, 50, 40, 40, 30),
            ( 30, 40, 40, 50, 50, 40, 40, 30),
            ( 30, 40, 40, 50, 50, 40, 40, 30),
        )
        zero_squares = (
             (0,  0,  0,  0,  0,  0,  0,  0),
             (0,  0,  0,  0,  0,  0,  0,  0),
             (0,  0,  0,  0,  0,  0,  0,  0),
             (0,  0,  0,  0,  0,  0,  0,  0),
             (0,  0,  0,  0,  0,  0,  0,  0),
             (0,  0,  0,  0,  0,  0,  0,  0),
             (0,  0,  0,  0,  0,  0,  0,  0),
             (0,  0,  0,  0,  0,  0,  0,  0),
        )

        # Pair encoded pieces to values
        value_map = {
            'OWN_PAWN' : (pawn_val, own_pawn_squares),
            'OWN_KNIGHT' : (knight_val, own_knight_squares),
            'OWN_BISHOP' : (bishop_val, own_bishop_squares),
            'OWN_ROOK': (rook_val, own_rook_squares),
            'OWN_QUEEN': (queen_val, own_queen_squares),
            'OWN_KING' : (king_val, own_king_squares),

            'OPP_PAWN' : (-pawn_val, opp_pawn_squares),
            'OPP_KNIGHT' : (-knight_val, opp_knight_squares),
            'OPP_BISHOP' : (-bishop_val, opp_bishop_squares),
            'OPP_ROOK': (-rook_val, opp_rook_squares),
            'OPP_QUEEN': (-queen_val, opp_queen_squares),
            'OPP_KING' : (-king_val, opp_king_squares),

            'EMPTY_SPACE' : (0, zero_squares),
        }

        # best_boards = [(root_value, root), ...]
        best_boards = starmap(
            partial(sequence_grouper, **value_map), groupby(boards, itemgetter(0)))
        # best_boards = [(root_value, [(root_value, root), ...]), ...]
        best_boards = groupby(sorted(best_boards, reverse=True), itemgetter(0))
        # best_boards = (root_value, [(root_value, root), ...])
        best_boards = next(best_boards)
        # best_average = root_value
        # best_boards = [(root_value, root), ...]
        best_average, best_boards = best_boards
        # best_boards = [root, ...]
        best_boards = tuple(map(itemgetter(1), best_boards))

        return (best_average, best_boards[randint(0, len(best_boards) - 1)])

    def put_board(self, board):
        '''Sends move selection to board state manager'''
        data = {'state': board}
        data = self.request('PUT', f'/v1.0/games/{ self.game_id }', json=data)
        self.game_over = data.get('end', False)
        if self.game_over:
            return self.close()
        return {}

    def join_game(self):
        self.request('POST', f'/v1.0/games/{ self.game_id }', json={'id': self.agent_id})
