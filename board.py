"""
Chess state handling model.
"""

from itertools import chain, count, starmap
from functools import partial

EMOJI = [
  '⌛', '‼',
  '♗', '♝', '♕', '♛', '♘', '♞', '♙', '♟', '♔', '♚', '♖', '♜', '▫', '▪']

BISHOP = 0B10
KING = 0B100
KNIGHT = 0B110
PAWN = 0B1000
QUEEN = 0B1010
ROOK = 0B1100

_FIRST_ROW = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
_PAWN_ROW = [PAWN for _ in range(8)]

INITIAL_BOARD = [
    _FIRST_ROW,
    _PAWN_ROW,
    *[[0 for _ in range(8)] for _ in range(4)],
    [piece | 1 for piece in _PAWN_ROW],
    [piece | 1 for piece in _FIRST_ROW]]
# low bit indicates active player piece


def _unit(i):
    return -1 if i < 0 else (0 if i == 0 else 1)


class Board:
    """
    Chess board state model.
    """

    def __init__(self, board=None) -> None:
        """
        Set up board.
        """
        self.board = [row[:] for row in (board or INITIAL_BOARD)]

    def __bool__(self):
        """
        Ensure active player king on board.
        """
        return self.has_king()

    def __repr__(self):
        """
        Output the raw view of board.
        """
        return f'Board({ self.board !r})'

    def __str__(self):
        """
        Output the emoji view of board.
        """
        return '\n'.join(''.join(EMOJI[p] for p in row) for row in self.board)

    def is_on_board(self, posX, posY, move):
        """
        Validate a move against board bounds.
        """
        if move:
            return 0 <= (posX + move[0]) < 8 and 0 <= (posY + move[1]) < 8

    def validate_ending(self, posX, posY, move):
        """
        Validate a move against ending location.
        """
        return not (self.board[posX + move[0]][posY + move[1]] & 1)

    def validate_move(self, posX, posY, move):
        """
        Validate clear path along move.
        """
        return (
            self.validate_ending(posX, posY, move) and
            all(
                map(
                    lambda _range:
                        not self.board
                        [posX + _unit(move[0]) * _range]
                        [posY + _unit(move[1]) * _range],
                    range(1, max(abs(move[0]), abs(move[1]))))))

    def validation_for_piece(self, piece, posX, posY):
        """
        Get final validation function for piece.
        """
        return (
            None,
            partial(self.validate_move, posX, posY),
            partial(self.validate_ending, posX, posY),
            partial(self.validate_ending, posX, posY),
            None,
            partial(self.validate_move, posX, posY),
            partial(self.validate_move, posX, posY))[piece // 2]

    def moves_for_piece(self, piece, posX, posY):
        """
        Get all possible moves for piece type.
        """
        return filter(partial(self.is_on_board, posX, posY), (
            [None],  # No piece
            (  # Bishop
                (-8, -8), (-7, -7), (-6, -6), (-5, -5),
                (-4, -4), (-3, -3), (-2, -2), (-1, -1),
                (1, 1), (2, 2), (3, 3), (4, 4),
                (5, 5), (6, 6), (7, 7), (8, 8),
                (-8, 8), (-7, 7), (-6, 6), (-5, 5),
                (-4, 4), (-3, 3), (-2, 2), (-1, 1),
                (1, -1), (2, -2), (3, -3), (4, -4),
                (5, -5), (6, -6), (7, -7), (8, -8)),
            (  # King
              (-1, -1), (-1, 0), (-1, 1), (0, -1),
              (0, 1), (1, -1), (1, 0), (1, 1)),
            (  # Knight
              (-2, -1), (-2, 1), (-1, -2), (-1, 2),
              (1, -2), (1, 2), (2, -1), (2, 1)),
            filter(  # Pawn
              None,
              (
                (
                  None if (
                    self.board[posX][posY - 1]) else (0, -1),
                  None if (
                    posY != 6 or
                    self.board[posX][posY - 1] or
                    self.board[posX][posY - 2]) else (0, -2),
                  (1, -1)
                ) if (
                  (posX < 7) and
                  (posY > 0) and
                  ((self.board[posX + 1][posY - 1] & 0xE)) and
                  self.validate_ending(posX, posY, (1, -1))
                ) else None,
                (-1, -1) if (
                  (posX > 0) and
                  ((posY > 0)) and
                  ((self.board[posX - 1][posY - 1] & 0xE)) and
                  (self.validate_ending(posX, posY, (-1, -1)))
                ) else None
              )
            ),
            (  # Queen
              (-8, -8), (-7, -7), (-6, -6), (-5, -5),
              (-4, -4), (-3, -3), (-2, -2), (-1, -1),
              (1, 1), (2, 2), (3, 3), (4, 4),
              (5, 5), (6, 6), (7, 7), (8, 8),
              (-8, 8), (-7, 7), (-6, 6), (-5, 5),
              (-4, 4), (-3, 3), (-2, 2), (-1, 1),
              (1, -1), (2, -2), (3, -3), (4, -4),
              (5, -5), (6, -6), (7, -7), (8, -8),
              (0, -8), (0, -7), (0, -6), (0, -5),
              (0, -4), (0, -3), (0, -2), (0, -1),
              (0, 1), (0, 2), (0, 3), (0, 4),
              (0, 5), (0, 6), (0, 7), (0, 8),
              (-8, 0), (-7, 0), (-6, 0), (-5, 0),
              (-4, 0), (-3, 0), (-2, 0), (-1, 0),
              (1, 0), (2, 0), (3, 0), (4, 0),
              (5, 0), (6, 0), (7, 0), (8, 0)
            ),
            (  # Rook
              (0, -8), (0, -7), (0, -6), (0, -5),
              (0, -4), (0, -3), (0, -2), (0, -1),
              (0, 1), (0, 2), (0, 3), (0, 4),
              (0, 5), (0, 6), (0, 7), (0, 8),
              (-8, 0), (-7, 0), (-6, 0), (-5, 0),
              (-4, 0), (-3, 0), (-2, 0), (-1, 0),
              (1, 0), (2, 0), (3, 0), (4, 0),
              (5, 0), (6, 0), (7, 0), (8, 0)
            )
          )[piece // 2])

    def valid_moves_for_piece(self, piece, posX, posY):
        """
        Get all valid moves for piece type.
        """
        return filter(
            self.validation_for_piece(piece, posX, posY),
            self.moves_for_piece(piece, posX, posY))

    def lookahead_boards_for_piece(self, piece, posX, posY):
        """
        Get all future board states.
        """
        def mutate_board(move):
            import pdb; pdb.set_trace()
            return map(
                count(),
                self.board,
                lambda pieceY, row: map(
                    count(),
                    row,
                    lambda pieceX, pp:
                        0
                        if (posX == pieceX) and (posY == pieceY) else
                        (
                            (
                                (piece ^ 1)
                                if piece & 1 else
                                ((piece | 1) if piece else 0))
                            if (
                                ((posX + move[0]) == pieceX) and
                                (posY + move[1]) == pieceY) else
                            pp + ((1 if piece % 2 == 0 else -1)))))

        return map(Board, map(
            mutate_board,
            self.valid_moves_for_piece(piece, posX, posY)))

    @staticmethod
    def active_piece(piece):
        """
        Validate piece as active.
        """
        return piece[2] & 1 and piece[2] > 1

    def active_pieces(self):
        """
        Get all pieces for current player.
        """
        return filter(
            self.active_piece,
            chain.from_iterable(
                map(
                    lambda posY, row: map(
                        lambda posX, piece: (piece, posX, posY), count(), row),
                    count(), self.board)))

    def lookahead_boards(self, n=4) -> None:
        """
        Provide an iterable of valid moves for current board state.
        """
        if n == 0:
            return [(self,)]
        return chain.from_iterable(
            map(
                lambda board: board.lookahead_boards(n - 1),
                chain.from_iterable(
                    starmap(
                        self.lookahead_boards_for_piece,
                        self.active_pieces()))))

    def has_king(self):
        """
        Ensure active player king on board.
        """
        return any(map(lambda row: (KING & 1) in row, self.board))


if __name__ == '__main__':
    seen = set()
    queue = set([Board()])
    while queue:
        board = queue.pop()
        seen.add(board)
        if not all(board.lookahead_boards(1)):
            continue
        for future in board.lookahead_boards(1):
            queue.add(future)
