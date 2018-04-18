import requests

from random import randint
from uuid import uuid4

import neuralknight


class BaseAgent:
    '''Slayer of chess'''

    AGENT_POOL = {}
    PORT = 8080
    API_URL = 'http://localhost:{}'.format(PORT)

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
        del self.AGENT_POOL[self.agent_id]

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
        own_pawn_squares = [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [ 5,  5, 10, 25, 25, 10,  5,  5],
            [ 0,  0,  0, 20, 20,  0,  0,  0],
            [ 5, -5,-10,  0,  0,-10, -5,  5],
            [ 5, 10, 10,-20,-20, 10, 10,  5],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
        ]
        own_knight_squares = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-20,-30,-30,-20,-40,-50],
        ]
        own_bishop_squares = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-40,-10,-10,-40,-10,-20],
        ]
        own_rook_squares = [
             [0,  0,  0,  0,  0,  0,  0,  0],
             [5, 10, 10, 10, 10, 10, 10,  5],
             [-5,  0,  0,  0,  0,  0,  0,  -5],
             [-5,  0,  0,  0,  0,  0,  0,  -5],
             [-5,  0,  0,  0,  0,  0,  0,  -5],
             [-5,  0,  0,  0,  0,  0,  0,  -5],
             [-5,  0,  0,  0,  0,  0,  0,  -5],
             [0,  0,  0,  5,  5,  0,  0,  0],
        ]
        own_queen_squares = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [-5,  0,  5,  5,  5,  5,  0, -5],
            [0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20],
        ]
        own_king_squares = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20],
        ]

        # Opp piece squares
        opp_pawn_squares = [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [-5,-10,-10, 20, 20,-10,-10, -5],
            [-5,  5, 10,  0,  0, 10,  5, -5],
            [ 0,  0,  0,-20,-20,  0,  0,  0],
            [-5, -5,-10,-25,-25,-10, -5, -5],
            [-10,-10,-20,-30,-30,-20,-10,-10],
            [-50,-50,-50,-50,-50,-50,-50,-50],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
        ]
        opp_knight_squares = [
            [ 50, 40, 20, 30, 30, 20, 40, 50],
            [ 40, 20,  0, -5, -5,  0, 20, 40],
            [ 30, -5,-10,-15,-15,-10, -5, 30],
            [ 30,  0,-15,-20,-20,-15,  0, 30],
            [ 30, -5,-15,-20,-20,-15, -5, 30],
            [ 30,  0,-10,-15,-15,-10,  0, 30],
            [ 40, 20,  0,  0,  0,  0, 20, 40],
            [ 50,-40,-20,-30,-30,-20,-40, 50],
        ]
        opp_bishop_squares = [
            [ 20, 10, 40, 10, 10, 40, 10, 20],
            [ 10, -5,  0,  0,  0,  0, -5, 10],
            [ 10,-10,-10,-10,-10,-10,-10, 10],
            [ 10,  0,-10,-10,-10,-10,  0, 10],
            [ 10, -5, -5,-10,-10, -5, -5, 10],
            [ 10,  0, -5,-10,-10, -5,  0, 10],
            [ 10,  0,  0,  0,  0,  0,  0, 10],
            [ 20, 10, 40, 10, 10, 40, 10, 20],
        ]
        opp_rook_squares = [
             [0,  0,  0, -5, -5,  0,  0,  0],
             [5,  0,  0,  0,  0,  0,  0,  5],
             [5,  0,  0,  0,  0,  0,  0,  5],
             [5,  0,  0,  0,  0,  0,  0,  5],
             [5,  0,  0,  0,  0,  0,  0,  5],
             [5,  0,  0,  0,  0,  0,  0,  5],
             [-5,-10,-10,-10,-10,-10,-10,-5],
             [0,  0,  0,  0,  0,  0,  0,  0],
        ]
        opp_queen_squares = [
            [ 20, 10, 10,  5,  5, 10, 10, 20],
            [ 10,  0,  0,  0,  0, -5,  0, 10],
            [ 10,  0, -5, -5, -5, -5, -5, 10],
            [  0,  0, -5, -5, -5, -5,  0,  5],
            [  5,  0, -5, -5, -5, -5,  0,  5],
            [ 10,  0, -5, -5, -5, -5,  0, 10],
            [ 10,  0,  0,  0,  0,  0,  0, 10],
            [ 20, 10, 10,  5,  5, 10, 10, 20],
        ]
        opp_king_squares = [
            [-20,-30,-10,  0,  0,-10,-30,-20],
            [-20,-20,  0,  0,  0,  0,-20,-20],
            [ 10, 20, 20, 20, 20, 20, 20, 10],
            [ 20, 30, 30, 40, 40, 30, 30, 20],
            [ 30, 40, 40, 50, 50, 40, 40, 30],
            [ 30, 40, 40, 50, 50, 40, 40, 30],
            [ 30, 40, 40, 50, 50, 40, 40, 30],
            [ 30, 40, 40, 50, 50, 40, 40, 30],
        ]
        zero_squares = [
             [0,  0,  0,  0,  0,  0,  0,  0],
             [0,  0,  0,  0,  0,  0,  0,  0],
             [0,  0,  0,  0,  0,  0,  0,  0],
             [0,  0,  0,  0,  0,  0,  0,  0],
             [0,  0,  0,  0,  0,  0,  0,  0],
             [0,  0,  0,  0,  0,  0,  0,  0],
             [0,  0,  0,  0,  0,  0,  0,  0],
             [0,  0,  0,  0,  0,  0,  0,  0],
        ]

        # Pair encoded pieces to values
        value_map = {
            9 : (pawn_val, own_pawn_squares),
            7 : (knight_val, own_knight_squares),
            3 : (bishop_val, own_bishop_squares),
            13: (rook_val, own_rook_squares),
            11: (queen_val, own_queen_squares),
            5 : (king_val, own_king_squares),

            8 : (-pawn_val, opp_pawn_squares),
            6 : (-knight_val, opp_knight_squares),
            2 : (-bishop_val, opp_bishop_squares),
            12: (-rook_val, opp_rook_squares),
            10: (-queen_val, opp_queen_squares),
            4 : (-king_val, opp_king_squares),

            0 : (0, zero_squares),
        }
        
        best_boards = []
        root = boards[0][0]
        leaf_sum = 0
        leaf_count = 0
        leaf_average = 0
        best_average = 0

        for board_sequence in boards:
            board_score = 0
            leaf = board_sequence[-1]

            for row in range(8):
                for col in range(8):
                    piece_values = value_map[leaf[row][col]]
                    board_score += piece_values[0]
                    board_score += piece_values[1][row][col]

            if board_sequence[0] == root:
                leaf_sum += board_score
                leaf_count += 1
            else:
                leaf_average = leaf_sum / leaf_count
                leaf_sum = board_score
                leaf_count = 1
                if leaf_average > best_average:
                    best_average = leaf_average
                    best_boards = [root]
                elif leaf_average == best_average:
                    if root not in best_boards:
                        best_boards.append(root)

                root = board_sequence[0]
        if not best_boards:
            return {
                'best_board': root,
                'board_score': best_average
            }

        return {
            'best_board': best_boards[randint(0, len(best_boards) - 1)],
            'board_score': best_average
        }

    def put_board(self, board):
        '''Sends move selection to board state manager'''
        # import pdb; pdb.set_trace()
        data = {'state': board}
        data = self.request('PUT', f'/v1.0/games/{ self.game_id }', json=data)
        if 'end' in data:
            self.game_over = data['end']

    def join_game(self):
        self.request('POST', f'/v1.0/games/{ self.game_id }', json={'id': self.agent_id})
