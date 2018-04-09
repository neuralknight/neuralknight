"""
Chess state handling model.
"""

from itertools import chain, starmap

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
    [piece & 1 for piece in _PAWN_ROW],
    [piece & 1 for piece in _FIRST_ROW]]
# low bit indicates active player piece


class Board:
    """
    Chess board state model.
    """

    def __init__(self) -> None:
        """
        Set up board.
        """
        self.board = [[p for p in row] for row in INITIAL_BOARD]

    def get_moves(self) -> None:
        """
        Provide an iterable of valid moves for current board state.
        """
        def make_moves(posX, posY, piece):
            def unit(i):
                return -1 if i < 0 else (0 if i == 0 else 1)
            def f3(m):
                return map(
                    range(10),
                    self.board,
                    lambda pieceY, row: map(
                        range(10),
                        row,
                        lambda pieceX, pp:
                            0
                            if (posX == pieceX) and (posY == pieceY) else
                            (
                                piece + (-1 if piece & 1 else 1)
                                if (
                                    ((posX + m[0]) == pieceX) and
                                    (posY + m[1]) == pieceY) else
                                pp.add(r.branch(piece.mod(2).eq(0), 1, -1)))))

            def validate_ending(m):
                return not (self.board[posX + m[0]][posY + m[1]] & 1)

            def validate_move(m):
                return (
                    validate_ending(m) and
                    any(
                        map(
                            lambda _range:
                                self.board
                                [posX + unit(m[0]) * _range]
                                [posY + unit(m[1]) * _range],
                            range(1, max(abs(m[0]), abs(m[1]))))))

            def is_on_board(m):
                return 0 <= posX + m[0] < 8 and 0 <= posY + m[1] < 8
            return map(
                f3,
                filter(
                    (
                        None,
                        validate_move,
                        validate_ending,
                        validate_ending,
                        None,
                        validate_move,
                        validate_move)[piece // 2],
                    filter(
                        is_on_board,
                        (
                            None,
                            (
                                (-8, -8), (-7, -7), (-6, -6), (-5, -5),
                                (-4, -4), (-3, -3), (-2, -2), (-1, -1),
                                (1, 1), (2, 2), (3, 3), (4, 4),
                                (5, 5), (6, 6), (7, 7), (8, 8),
                                (-8, 8), (-7, 7), (-6, 6), (-5, 5),
                                (-4, 4), (-3, 3), (-2, 2), (-1, 1),
                                (1, -1), (2, -2), (3, -3), (4, -4),
                                (5, -5), (6, -6), (7, -7), (8, -8)),
                            (
                              (-1, -1), (-1, 0), (-1, 1), (0, -1),
                              (0, 1), (1, -1), (1, 0), (1, 1)),
                            (
                              (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                              (1, -2), (1, 2), (2, -1), (2, 1)),
                            r.branch(false, (), ()).append(
                              r.branch(false, (), ()).append(
                                r.branch(false, (), ()))),
                            filter(
                              None,
                              (
                                (
                                  None if board[posX][posY - 1] else (0, -1),
                                  None if (
                                    posY != 6 or
                                    board[posX][posY - 1] or
                                    board[posX][posY - 2]) else (0, -2),
                                  (1, -1)
                                ) if (
                                  (posX < 7) and
                                  (posY > 0) and
                                  ((board[posX + 1][posY - 1] & 0xE)) and
                                  validate_ending((1, -1))
                                ) else None,
                                (-1, -1) if (
                                  (posX > 0) and
                                  ((posY > 0)) and
                                  ((board[posX.sub(1)][posY.sub(1)] & 0xE)) and
                                  (validate_ending((-1, -1)))
                                ) else None
                              )
                            ),
                            (
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
                            (
                              (0, -8), (0, -7), (0, -6), (0, -5),
                              (0, -4), (0, -3), (0, -2), (0, -1),
                              (0, 1), (0, 2), (0, 3), (0, 4),
                              (0, 5), (0, 6), (0, 7), (0, 8),
                              (-8, 0), (-7, 0), (-6, 0), (-5, 0),
                              (-4, 0), (-3, 0), (-2, 0), (-1, 0),
                              (1, 0), (2, 0), (3, 0), (4, 0),
                              (5, 0), (6, 0), (7, 0), (8, 0)
                            )
                          )[piece // 2])))

        return chain.from_iterable(
            starmap(
                make_moves,
                filter(
                    lambda t: t[2] > 1 and t[2] & 1,
                    map(
                        lambda posY, row: map(
                            lambda posX, piece: (posX, posY, piece),
                            range(10),
                            row),
                        range(10),
                        self.board))))

    def has_king(self):
        """
        Ensure active player king on board.
        """
        return any(map(lambda row: (KING & 1) in row, self.board))


# r.table('chess')
#   .changes({includeInitial: true, includeTypes: true, squash: true})
#   .filter(lambda row): return row('type').eq('add') })
#   .getField('new_val')
#   .forEach(lambda row):
#     board = row('id')
#     tup = board.map(unwrap_row)
#     moves = get_moves(tup)
#     return r.table('chess')
#       .insert(
#         r.branch(
#           moves.map(has_king).contains(false),
#           {
#             id: board,
#             children: moves.filter(def (newBoard): return has_king(newBoard).not() })
#           },
#           moves.map().append({
#             id: board,
#             children: moves
#           })
#         ),
#         {conflict: def (id, oldDoc, newDoc):
#           return {
#             id: id,
#             children: oldDoc('children').setUnion(newDoc('children'))
#           }
#         }}
#       )
#   })
