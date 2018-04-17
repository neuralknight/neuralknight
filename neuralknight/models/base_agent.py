from random import randint
from uuid import uuid4

from .board import Board


class BaseAgent:
    '''Slayer of chess'''

    AGENT_POOL = {}

    def __init__(self, game_id=None):
        self.agent_id = str(uuid4())
        if game_id:
            self.player = 2
            self.game_id = game_id
            self.AGENT_POOL[self.agent_id] = self
            self.join_game()

        self.state = None

    def request(self, *args, **kwargs):
        assert False

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
            [-20,-10,-10, -5, -5,-10,-10,-20]
            [-10,  0,  0,  0,  0,  0,  0,-10]
            [-10,  0,  5,  5,  5,  5,  0,-10]
            [-5,  0,  5,  5,  5,  5,  0, -5]
            [0,  0,  5,  5,  5,  5,  0, -5]
            [-10,  5,  5,  5,  5,  5,  0,-10]
            [-10,  0,  5,  0,  0,  0,  0,-10]
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        own_king_squares = [
            [-30,-40,-40,-50,-50,-40,-40,-30]
            [-30,-40,-40,-50,-50,-40,-40,-30]
            [-30,-40,-40,-50,-50,-40,-40,-30]
            [-30,-40,-40,-50,-50,-40,-40,-30]
            [-20,-30,-30,-40,-40,-30,-30,-20]
            [-10,-20,-20,-20,-20,-20,-20,-10]
            [20, 20,  0,  0,  0,  0, 20, 20]
            [20, 30, 10,  0,  0, 10, 30, 20]
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

        best_boards = [boards[0][0]]
        best_board_score = -999999
        for board_sequence in boards:
            for board in board_sequence:
                board_score = 0
                for row in range(8):
                    for col in range(8):
                        piece_values = value_map[board[row][col]]
                        board_score += piece_values[0]
                        board_score += piece_values[1][row][col]
                if board_score > best_board_score:
                    best_board_score = board_score
                    best_boards = [board_sequence[0]]
                    break
                elif board_score == best_board_score:
                    best_boards.append(board_sequence[0])
                    break

        best_board = best_boards[randint(0, len(best_boards))]

        if self.player == 1:
            print(Board(best_board))
            self.player = 2
        else:
            print(Board(best_board).swap())
            self.player = 1

        return best_board

    def get_state(self):
        '''Gets current board state'''
        response = self.request('GET', f'/v1.0/games/{ self.game_id }')
        data = response.json()
        return data['board']

    def put_board(self, board):
        '''Sends move selection to board state manager'''
        data = {'state': board}
        response = self.request('PUT', f'/v1.0/games/{ self.game_id }', json=data)
        data = response.json()
        return data['end']

    def init_game(self):
        '''Initialize a new game'''
        data = {'id': self.agent_id}
        response = self.request('POST', '/v1.0/games', data=data)
        data = response.json()
        self.game_id = data['id']

        self.player = 1
        self.state = self.get_state()
        self.AGENT_POOL[self.agent_id] = self

    def join_game(self):
        data = {'id': self.agent_id}
        response = self.request('POST', f'/v1.0/games/{ self.game_id }', data=data)
        response.json()
