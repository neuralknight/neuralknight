from functools import partial
from itertools import chain, count, groupby, starmap
from operator import itemgetter
# from statistics import harmonic_mean

from .base_agent import BaseAgent


class NewAgent(BaseAgent):
    '''Computer Agent'''

    def get_score(self, leaf, posY, posX, piece, **value_map):
        piece = {
            9: 'OWN_PAWN',
            7: 'OWN_KNIGHT',
            3: 'OWN_BISHOP',
            13: 'OWN_ROOK',
            11: 'OWN_QUEEN',
            5: 'OWN_KING',

            8: 'OPP_PAWN',
            6: 'OPP_KNIGHT',
            2: 'OPP_BISHOP',
            12: 'OPP_ROOK',
            10: 'OPP_QUEEN',
            4: 'OPP_KING',
        }.get(piece & 0xF, 'EMPTY_SPACE')
        piece_values = value_map[piece]
        return piece_values[0] + piece_values[1][posY][posX]

    def check_sequence(self, sequence, **value_map):
        leaf = sequence[-1]
        return sum(chain.from_iterable(map(
            lambda posY, row: map(
                lambda posX, piece: self.get_score(leaf, posY, posX, piece, **value_map),
                count(), row),
            count(), leaf)))

    def sequence_grouper(self, root, sequences, **value_map):
        root_value = min(map(partial(self.check_sequence, **value_map), sequences))
        return (round(root_value, -1) // 100, root)

    def evaluate_boards(self, boards):
        '''Determine value for each board state in array of board states

        Inputs:
            boards: Array of board states

        Outputs:
            best_state: The highest valued board state in the array

        '''
        own_pawn_val = 100
        own_knight_val = 320
        own_bishop_val = 330
        own_rook_val = 500
        own_queen_val = 9000
        own_king_val = 20000

        opp_pawn_val = -own_pawn_val
        opp_knight_val = -own_knight_val
        opp_bishop_val = -own_bishop_val
        opp_rook_val = -own_rook_val
        opp_queen_val = -own_queen_val
        opp_king_val = -own_king_val

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
            'OWN_PAWN': (own_pawn_val, own_pawn_squares),
            'OWN_KNIGHT': (own_knight_val, own_knight_squares),
            'OWN_BISHOP': (own_bishop_val, own_bishop_squares),
            'OWN_ROOK': (own_rook_val, own_rook_squares),
            'OWN_QUEEN': (own_queen_val, own_queen_squares),
            'OWN_KING': (own_king_val, own_king_squares),

            'OPP_PAWN': (opp_pawn_val, opp_pawn_squares),
            'OPP_KNIGHT': (opp_knight_val, opp_knight_squares),
            'OPP_BISHOP': (opp_bishop_val, opp_bishop_squares),
            'OPP_ROOK': (opp_rook_val, opp_rook_squares),
            'OPP_QUEEN': (opp_queen_val, opp_queen_squares),
            'OPP_KING': (opp_king_val, opp_king_squares),

            'EMPTY_SPACE': (0, zero_squares),
        }

        # best_boards = [(root_value, root), ...]
        best_boards = starmap(
            partial(self.sequence_grouper, **value_map), groupby(boards, itemgetter(0)))
        # best_boards = [(root_value, [(root_value, root), ...]), ...]
        best_boards = groupby(sorted(best_boards, reverse=True), itemgetter(0))
        # best_boards = (root_value, [(root_value, root), ...])
        try:
            best_boards = next(best_boards)
        except StopIteration:
            return (opp_king_val * 64, [])
        # best_average = root_value
        # best_boards = [(root_value, root), ...]
        best_average, best_boards = best_boards
        # best_boards = [root, ...]
        best_boards = tuple(map(itemgetter(1), best_boards))

        return (best_average, best_boards)
