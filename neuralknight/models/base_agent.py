from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache, partial
from itertools import chain, count, groupby, repeat, starmap
from operator import itemgetter, methodcaller
from random import sample
from statistics import harmonic_mean


__all__ = ('AGENTS',)


class BaseAgent:
    """
    Slayer of chess

    Override the following method to provide choice options.
    This method is called by multiprocessing.

    def evaluate_boards(self, best_boards):
        '''
        // best_boards <- [<board_matrix>, ...]
        // return <- (selection_weight, [<board_matrix>, ...])

        select a sub slice of input and provide a collection weight.
        '''
        ...
        return (0, sample(best_boards, 3))
    """

    @staticmethod
    def evaluate_boards(best_boards):
        return sample(best_boards, 3)

    def play_round(self, boards_cursor):
        '''Play a game round'''
        with ProcessPoolExecutor(4) as executor:
            # best_boards = [(root_value, root), ...]
            best_boards = executor.map(
                self.call,
                map(partial(methodcaller, 'evaluate_boards'), boards_cursor),
                repeat(self),
                chunksize=50)
            # best_boards = [(root_value, [(root_value, root), ...]), ...]
            best_boards = groupby(sorted(best_boards, reverse=True), itemgetter(0))
            # _, best_boards = (root_value, [(root_value, root), ...])
            try:
                _, best_boards = next(best_boards)
            except StopIteration:
                return self.close()
            # best_boards = [root, ...]
            best_boards = list(map(
                next,
                map(
                    itemgetter(1),
                    groupby(chain.from_iterable(map(itemgetter(1), best_boards))))))
            if not best_boards:
                return self.close()
            return self.put_board(sample(best_boards, 1)[0])


@lru_cache(maxsize=1024)
def get_score(leaf, posY, posX, piece, **value_map):
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


class WeightAgent(BaseAgent):
    """
    Uses a piece and square weighting to implement .

    override the following values to implement.

    OWN_<PIECE>_VAL = int
    ...

    OPP_<PIECE>_VAL = int
    ...

    OWN_<PIECE>_SQUARES = <board_matrix>
    ...

    OPP_<PIECE>_SQUARES = <board_matrix>
    ...

    ZERO_SQUARES = <board_matrix>
    """

    @staticmethod
    def get_score(leaf, posY, posX, piece, **value_map):
        return get_score(leaf, posY, posX, piece, **value_map)

    @staticmethod
    def call(_call, *args, **kwargs):
        return _call(*args, **kwargs)

    def check_sequence(self, sequence, **value_map):
        leaf = sequence[-1]
        return sum(chain.from_iterable(map(
            lambda posY, row: map(
                lambda posX, piece: self.get_score(leaf, posY, posX, piece, **value_map),
                count(), row),
            count(), leaf)))

    def sequence_grouper(self, root, sequences, **value_map):
        root_value = sample(list(map(partial(self.check_sequence, **value_map), sequences)), 1)
        return (round(root_value, -1) // 100, root)

    def evaluate_boards(self, boards):
        '''Determine value for each board state in array of board states

        Inputs:
            boards: Array of board states

        Outputs:
            best_state: The highest valued board state in the array
        '''

        # Pair encoded pieces to values
        value_map = {
            'OWN_PAWN': (self.OWN_PAWN_VAL, self.OWN_PAWN_SQUARES),
            'OWN_KNIGHT': (self.OWN_KNIGHT_VAL, self.OWN_KNIGHT_SQUARES),
            'OWN_BISHOP': (self.OWN_BISHOP_VAL, self.OWN_BISHOP_SQUARES),
            'OWN_ROOK': (self.OWN_ROOK_VAL, self.OWN_ROOK_SQUARES),
            'OWN_QUEEN': (self.OWN_QUEEN_VAL, self.OWN_QUEEN_SQUARES),
            'OWN_KING': (self.OWN_KING_VAL, self.OWN_KING_SQUARES),

            'OPP_PAWN': (self.OPP_PAWN_VAL, self.OPP_PAWN_SQUARES),
            'OPP_KNIGHT': (self.OPP_KNIGHT_VAL, self.OPP_KNIGHT_SQUARES),
            'OPP_BISHOP': (self.OPP_BISHOP_VAL, self.OPP_BISHOP_SQUARES),
            'OPP_ROOK': (self.OPP_ROOK_VAL, self.OPP_ROOK_SQUARES),
            'OPP_QUEEN': (self.OPP_QUEEN_VAL, self.OPP_QUEEN_SQUARES),
            'OPP_KING': (self.OPP_KING_VAL, self.OPP_KING_SQUARES),

            'EMPTY_SPACE': (20000, self.ZERO_SQUARES),
        }

        # best_boards = [(root_value, root), ...]
        best_boards = starmap(
            partial(self.sequence_grouper, **value_map), groupby(boards, itemgetter(0)))
        # best_boards = [(root_value, [(root_value, root), ...]), ...]
        best_boards = groupby(sorted(best_boards), itemgetter(0))
        # best_boards = (root_value, [(root_value, root), ...])
        try:
            best_boards = next(best_boards)
        except StopIteration:
            return (self.OPP_KING_VAL * 64, [])
        # best_boards = [(root_value, root), ...]
        best_average, best_boards = best_boards
        # best_boards = [root, ...]
        best_boards = tuple(map(itemgetter(1), best_boards))

        return (best_average, best_boards)


class PositiveWeightAgent(WeightAgent):
    # Piece values
    OWN_PAWN_VAL = 20100
    OWN_KNIGHT_VAL = 20320
    OWN_BISHOP_VAL = 20330
    OWN_ROOK_VAL = 20500
    OWN_QUEEN_VAL = 29000
    OWN_KING_VAL = 40000

    OPP_PAWN_VAL = 19900
    OPP_KNIGHT_VAL = 19680
    OPP_BISHOP_VAL = 19670
    OPP_ROOK_VAL = 19500
    OPP_QUEEN_VAL = 11000
    OPP_KING_VAL = 0

    # pylama:ignore=E201,E203,E231
    # Piece squares - from http://www.chessbin.com/post/Piece-Square-Table
    # Own piece squares
    OWN_PAWN_SQUARES = (
        (50, 50, 50, 50, 50, 50, 50, 50),
        (100, 100, 100, 100, 100, 100, 100, 100),
        (60, 60, 70, 80, 80, 70, 60, 60),
        (55, 55, 60, 75, 75, 60, 55, 55),
        (50, 50, 50, 70, 70, 50, 50, 50),
        (55, 45, 40, 50, 50, 40, 45, 55),
        (55, 60, 60, 30, 30, 60, 60, 55),
        (50, 50, 50, 50, 50, 50, 50, 50),
    )
    OWN_KNIGHT_SQUARES = (
        (0, 10, 20, 20, 20, 20, 10, 0),
        (10, 30, 50, 50, 50, 50, 30, 10),
        (20, 50, 60, 65, 65, 60, 50, 20),
        (20, 55, 65, 70, 70, 65, 55, 20),
        (20, 50, 65, 70, 70, 65, 50, 20),
        (20, 55, 60, 65, 65, 60, 55, 20),
        (10, 30, 50, 55, 55, 50, 30, 10),
        (0, 10, 30, 20, 20, 30, 10, 0),
    )
    OWN_BISHOP_SQUARES = (
        (30, 40, 40, 40, 40, 40, 40, 30),
        (40, 50, 50, 50, 50, 50, 50, 40),
        (40, 50, 55, 60, 60, 55, 50, 40),
        (40, 55, 55, 60, 60, 55, 55, 40),
        (40, 50, 60, 60, 60, 60, 50, 40),
        (40, 60, 60, 60, 60, 60, 60, 40),
        (40, 55, 50, 50, 50, 50, 55, 40),
        (30, 40, 10, 40, 40, 10, 40, 30),
    )
    OWN_ROOK_SQUARES = (
        (50, 50, 50, 50, 50, 50, 50, 50),
        (55, 60, 60, 60, 60, 60, 60, 55),
        (45, 50, 50, 50, 50, 50, 50, 45),
        (45, 50, 50, 50, 50, 50, 50, 45),
        (45, 50, 50, 50, 50, 50, 50, 45),
        (45, 50, 50, 50, 50, 50, 50, 45),
        (45, 50, 50, 50, 50, 50, 50, 45),
        (50, 50, 50, 55, 55, 50, 50, 50),
    )
    OWN_QUEEN_SQUARES = (
        (30, 40, 40, 45, 45, 40, 40, 30),
        (40, 50, 50, 50, 50, 50, 50, 40),
        (40, 50, 55, 55, 55, 55, 50, 40),
        (45, 50, 55, 55, 55, 55, 50, 45),
        (50, 50, 55, 55, 55, 55, 50, 45),
        (40, 55, 55, 55, 55, 55, 50, 40),
        (40, 50, 55, 50, 50, 50, 50, 40),
        (30, 40, 40, 45, 45, 40, 40, 30),
    )
    OWN_KING_SQUARES = (
        (20, 10, 10, 0, 0, 10, 10, 20),
        (20, 10, 10, 0, 0, 10, 10, 20),
        (20, 10, 10, 0, 0, 10, 10, 20),
        (20, 10, 10, 0, 0, 10, 10, 20),
        (30, 20, 20, 10, 10, 20, 20, 30),
        (40, 30, 30, 30, 30, 30, 30, 40),
        (70, 70, 50, 50, 50, 50, 70, 70),
        (70, 80, 60, 50, 50, 60, 80, 70),
    )

    # Opp piece squares
    OPP_PAWN_SQUARES = (
        (50, 50, 50, 50, 50, 50, 50, 50),
        (45, 40, 40, 70, 70, 40, 40, 45),
        (45, 55, 60, 50, 50, 60, 55, 45),
        (50, 50, 50, 30, 30, 50, 50, 50),
        (45, 45, 40, 25, 25, 40, 45, 45),
        (40, 40, 30, 20, 20, 30, 40, 40),
        (0, 0, 0, 0, 0, 0, 0, 0),
        (50, 50, 50, 50, 50, 50, 50, 50),
    )
    OPP_KNIGHT_SQUARES = (
        (100, 90, 70, 80, 80, 70, 90, 100),
        (90, 70, 50, 45, 45, 50, 70, 90),
        (80, 45, 40, 35, 35, 40, 45, 80),
        (80, 50, 35, 30, 30, 35, 50, 80),
        (80, 45, 35, 30, 30, 35, 45, 80),
        (80, 50, 40, 35, 35, 40, 50, 80),
        (90, 70, 50, 50, 50, 50, 70, 90),
        (100, 10, 30, 20, 20, 30, 10, 100),
    )
    OPP_BISHOP_SQUARES = (
        (70, 60, 90, 60, 60, 90, 60, 70),
        (60, 45, 50, 50, 50, 50, 45, 60),
        (60, 40, 40, 40, 40, 40, 40, 60),
        (60, 50, 40, 40, 40, 40, 50, 60),
        (60, 45, 45, 40, 40, 45, 45, 60),
        (60, 50, 45, 40, 40, 45, 50, 60),
        (60, 50, 50, 50, 50, 50, 50, 60),
        (70, 60, 90, 60, 60, 90, 60, 70),
    )
    OPP_ROOK_SQUARES = (
        (50, 50, 50, 45, 45, 50, 50, 50),
        (55, 50, 50, 50, 50, 50, 50, 55),
        (55, 50, 50, 50, 50, 50, 50, 55),
        (55, 50, 50, 50, 50, 50, 50, 55),
        (55, 50, 50, 50, 50, 50, 50, 55),
        (55, 50, 50, 50, 50, 50, 50, 55),
        (45, 40, 40, 40, 40, 40, 40, 45),
        (50, 50, 50, 50, 50, 50, 50, 50),
    )
    OPP_QUEEN_SQUARES = (
        (70, 60, 60, 55, 55, 60, 60, 70),
        (60, 50, 50, 50, 50, 45, 50, 60),
        (60, 50, 45, 45, 45, 45, 45, 60),
        (50, 50, 45, 45, 45, 45, 50, 55),
        (55, 50, 45, 45, 45, 45, 50, 55),
        (60, 50, 45, 45, 45, 45, 50, 60),
        (60, 50, 50, 50, 50, 50, 50, 60),
        (70, 60, 60, 55, 55, 60, 60, 70),
    )
    OPP_KING_SQUARES = (
        (30, 20, 40, 50, 50, 40, 20, 30),
        (30, 30, 50, 50, 50, 50, 30, 30),
        (60, 70, 70, 70, 70, 70, 70, 60),
        (70, 80, 80, 90, 90, 80, 80, 70),
        (80, 90, 90, 100, 100, 90, 90, 80),
        (80, 90, 90, 100, 100, 90, 90, 80),
        (80, 90, 90, 100, 100, 90, 90, 80),
        (80, 90, 90, 100, 100, 90, 90, 80),
    )
    ZERO_SQUARES = (
        (50, 50, 50, 50, 50, 50, 50, 50),
        (50, 50, 50, 50, 50, 50, 50, 50),
        (50, 50, 50, 50, 50, 50, 50, 50),
        (50, 50, 50, 50, 50, 50, 50, 50),
        (50, 50, 50, 50, 50, 50, 50, 50),
        (50, 50, 50, 50, 50, 50, 50, 50),
        (50, 50, 50, 50, 50, 50, 50, 50),
        (50, 50, 50, 50, 50, 50, 50, 50),
    )


class BalanceWeightAgent(WeightAgent):
    # Piece values
    OWN_PAWN_VAL = 100
    OWN_KNIGHT_VAL = 320
    OWN_BISHOP_VAL = 330
    OWN_ROOK_VAL = 500
    OWN_QUEEN_VAL = 9000
    OWN_KING_VAL = 20000

    OPP_PAWN_VAL = -OWN_PAWN_VAL
    OPP_KNIGHT_VAL = -OWN_KNIGHT_VAL
    OPP_BISHOP_VAL = -OWN_BISHOP_VAL
    OPP_ROOK_VAL = -OWN_ROOK_VAL
    OPP_QUEEN_VAL = -OWN_QUEEN_VAL
    OPP_KING_VAL = -OWN_KING_VAL

    # pylama:ignore=E201,E203,E231
    # Piece squares - from http://www.chessbin.com/post/Piece-Square-Table
    # Own piece squares
    OWN_PAWN_SQUARES = (
        (0,  0,  0,  0,  0,  0,  0,  0),
        (50, 50, 50, 50, 50, 50, 50, 50),
        (10, 10, 20, 30, 30, 20, 10, 10),
        (5,  5, 10, 25, 25, 10,  5,  5),
        (0,  0,  0, 20, 20,  0,  0,  0),
        (5, -5, -10,  0,  0, -10, -5,  5),
        (5, 10, 10, -20, -20, 10, 10,  5),
        (0,  0,  0,  0,  0,  0,  0,  0),
    )
    OWN_KNIGHT_SQUARES = (
        (-50, -40, -30, -30, -30, -30, -40, -50),
        (-40, -20,  0,  0,  0,  0, -20, -40),
        (-30,  0, 10, 15, 15, 10,  0, -30),
        (-30,  5, 15, 20, 20, 15,  5, -30),
        (-30,  0, 15, 20, 20, 15,  0, -30),
        (-30,  5, 10, 15, 15, 10,  5, -30),
        (-40, -20,  0,  5,  5,  0, -20, -40),
        (-50, -40, -20, -30, -30, -20, -40, -50),
    )
    OWN_BISHOP_SQUARES = (
        (-20, -10, -10, -10, -10, -10, -10, -20),
        (-10,  0,  0,  0,  0,  0,  0, -10),
        (-10,  0,  5, 10, 10,  5,  0, -10),
        (-10,  5,  5, 10, 10,  5,  5, -10),
        (-10,  0, 10, 10, 10, 10,  0, -10),
        (-10, 10, 10, 10, 10, 10, 10, -10),
        (-10,  5,  0,  0,  0,  0,  5, -10),
        (-20, -10, -40, -10, -10, -40, -10, -20),
    )
    OWN_ROOK_SQUARES = (
         (0,  0,  0,  0,  0,  0,  0,  0),
         (5, 10, 10, 10, 10, 10, 10,  5),
         (-5,  0,  0,  0,  0,  0,  0,  -5),
         (-5,  0,  0,  0,  0,  0,  0,  -5),
         (-5,  0,  0,  0,  0,  0,  0,  -5),
         (-5,  0,  0,  0,  0,  0,  0,  -5),
         (-5,  0,  0,  0,  0,  0,  0,  -5),
         (0,  0,  0,  5,  5,  0,  0,  0),
    )
    OWN_QUEEN_SQUARES = (
        (-20, -10, -10, -5, -5, -10, -10, -20),
        (-10,  0,  0,  0,  0,  0,  0, -10),
        (-10,  0,  5,  5,  5,  5,  0, -10),
        (-5,  0,  5,  5,  5,  5,  0, -5),
        (0,  0,  5,  5,  5,  5,  0, -5),
        (-10,  5,  5,  5,  5,  5,  0, -10),
        (-10,  0,  5,  0,  0,  0,  0, -10),
        (-20, -10, -10, -5, -5, -10, -10, -20),
    )
    OWN_KING_SQUARES = (
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-20, -30, -30, -40, -40, -30, -30, -20),
        (-10, -20, -20, -20, -20, -20, -20, -10),
        (20, 20,  0,  0,  0,  0, 20, 20),
        (20, 30, 10,  0,  0, 10, 30, 20),
    )

    # Opp piece squares
    OPP_PAWN_SQUARES = (
        (0,  0,  0,  0,  0,  0,  0,  0),
        (-5, -10, -10, 20, 20, -10, -10, -5),
        (-5,  5, 10,  0,  0, 10,  5, -5),
        (0,  0,  0, -20, -20,  0,  0,  0),
        (-5, -5, -10, -25, -25, -10, -5, -5),
        (-10, -10, -20, -30, -30, -20, -10, -10),
        (-50, -50, -50, -50, -50, -50, -50, -50),
        (0,  0,  0,  0,  0,  0,  0,  0),
    )
    OPP_KNIGHT_SQUARES = (
        (50, 40, 20, 30, 30, 20, 40, 50),
        (40, 20,  0, -5, -5,  0, 20, 40),
        (30, -5, -10, -15, -15, -10, -5, 30),
        (30,  0, -15, -20, -20, -15,  0, 30),
        (30, -5, -15, -20, -20, -15, -5, 30),
        (30,  0, -10, -15, -15, -10,  0, 30),
        (40, 20,  0,  0,  0,  0, 20, 40),
        (50, -40, -20, -30, -30, -20, -40, 50),
    )
    OPP_BISHOP_SQUARES = (
        (20, 10, 40, 10, 10, 40, 10, 20),
        (10, -5,  0,  0,  0,  0, -5, 10),
        (10, -10, -10, -10, -10, -10, -10, 10),
        (10,  0, -10, -10, -10, -10,  0, 10),
        (10, -5, -5, -10, -10, -5, -5, 10),
        (10,  0, -5, -10, -10, -5,  0, 10),
        (10,  0,  0,  0,  0,  0,  0, 10),
        (20, 10, 40, 10, 10, 40, 10, 20),
    )
    OPP_ROOK_SQUARES = (
         (0,  0,  0, -5, -5,  0,  0,  0),
         (5,  0,  0,  0,  0,  0,  0,  5),
         (5,  0,  0,  0,  0,  0,  0,  5),
         (5,  0,  0,  0,  0,  0,  0,  5),
         (5,  0,  0,  0,  0,  0,  0,  5),
         (5,  0,  0,  0,  0,  0,  0,  5),
         (-5, -10, -10, -10, -10, -10, -10, -5),
         (0,  0,  0,  0,  0,  0,  0,  0),
    )
    OPP_QUEEN_SQUARES = (
        (20, 10, 10,  5,  5, 10, 10, 20),
        (10,  0,  0,  0,  0, -5,  0, 10),
        (10,  0, -5, -5, -5, -5, -5, 10),
        (0,  0, -5, -5, -5, -5,  0,  5),
        (5,  0, -5, -5, -5, -5,  0,  5),
        (10,  0, -5, -5, -5, -5,  0, 10),
        (10,  0,  0,  0,  0,  0,  0, 10),
        (20, 10, 10,  5,  5, 10, 10, 20),
    )
    OPP_KING_SQUARES = (
        (-20, -30, -10,  0,  0, -10, -30, -20),
        (-20, -20,  0,  0,  0,  0, -20, -20),
        (10, 20, 20, 20, 20, 20, 20, 10),
        (20, 30, 30, 40, 40, 30, 30, 20),
        (30, 40, 40, 50, 50, 40, 40, 30),
        (30, 40, 40, 50, 50, 40, 40, 30),
        (30, 40, 40, 50, 50, 40, 40, 30),
        (30, 40, 40, 50, 50, 40, 40, 30),
    )
    ZERO_SQUARES = (
         (0,  0,  0,  0,  0,  0,  0,  0),
         (0,  0,  0,  0,  0,  0,  0,  0),
         (0,  0,  0,  0,  0,  0,  0,  0),
         (0,  0,  0,  0,  0,  0,  0,  0),
         (0,  0,  0,  0,  0,  0,  0,  0),
         (0,  0,  0,  0,  0,  0,  0,  0),
         (0,  0,  0,  0,  0,  0,  0,  0),
         (0,  0,  0,  0,  0,  0,  0,  0),
    )


class StrategyAgent(BaseAgent):
    """
    Use strategy to evaluate a sequence of root values.

    STRATEGY = lambda <int_sequence>: int
    """
    STRATEGY = harmonic_mean

    def sequence_grouper(self, root, sequences, **value_map):
        root_value = self.STRATEGY(map(partial(self.check_sequence, **value_map), sequences))
        return (round(root_value, -1) // 100, root)


class Agent(StrategyAgent, PositiveWeightAgent):
    '''Computer Agent'''
    STRATEGY = harmonic_mean


class BalanceAgent(StrategyAgent, BalanceWeightAgent):
    '''Computer Agent'''
    def STRATEGY(values):
        return harmonic_mean(map(lambda value: value if value > 0 else 0, values))


class NewAgent(StrategyAgent, BalanceWeightAgent):
    '''Computer Agent'''
    STRATEGY = min


class MaxBalanceAgent(StrategyAgent, BalanceWeightAgent):
    '''Computer Agent'''
    STRATEGY = max


class MaxPositiveAgent(StrategyAgent, PositiveWeightAgent):
    '''Computer Agent'''
    STRATEGY = max


class MinPositiveAgent(StrategyAgent, PositiveWeightAgent):
    '''Computer Agent'''
    STRATEGY = min


AGENTS = {
    'base-agent': Agent,
    'balance-agent': BalanceAgent,
    'new-agent': NewAgent,
    'max-balance-agent': MaxPositiveAgent,
    'max-positive-agent': MaxPositiveAgent,
    'min-positive-agent': MinPositiveAgent,
}
