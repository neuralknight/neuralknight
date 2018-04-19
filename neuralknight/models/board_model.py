"""
Chess state handling model.
"""

from itertools import chain, count, islice, starmap
from functools import partial, lru_cache
from uuid import uuid4

from .board_constants import (
    INITIAL_BOARD, KING, unit,
    BISHOP_MOVES, KING_MOVES, KNIGHT_MOVES, QUEEN_MOVES, ROOK_MOVES)

__all__ = ['BoardModel', 'CursorDelegate']


class CursorDelegate:
    def __init__(self):
        self.cursors = {}

    def get_cursor(self, board, cursor, lookahead):
        """
        Retrieve iterable for cursor.
        """
        cursor = cursor or str(uuid4())
        return self.cursors.pop(cursor, board.lookahead_boards(lookahead))

    def slice_cursor_v1(self, board, cursor, lookahead):
        """
        Retrieve REST cursor slice.
        """
        it = self.get_cursor(board, cursor, lookahead)
        slen = 300 // lookahead
        boards = tuple(islice(it, slen))
        if len(boards) < slen:
            return {'cursor': None, 'boards': boards}
        cursor = str(uuid4())
        self.cursors[cursor] = it
        return {'cursor': cursor, 'boards': boards}


@lru_cache()
def is_on_board(posX, posY, move):
    """
    Validate a move against board bounds.
    """
    return 0 <= (posX + move[0]) < 8 and 0 <= (posY + move[1]) < 8


@lru_cache()
def validate_ending(board, posX, posY, move):
    """
    Validate a move against ending location.
    """
    return not active_piece(
        board[posY + move[1]][posX + move[0]])


@lru_cache()
def validate_move(board, posX, posY, move):
    """
    Validate clear path along move.
    """
    return (
        validate_ending(board, posX, posY, move)
        and all(
            map(
                lambda _range:
                    not board
                    [posY + unit(move[1]) * _range]
                    [posX + unit(move[0]) * _range],
                range(1, max(abs(move[0]), abs(move[1]))))))


@lru_cache()
def validation_for_piece(board, piece, posX, posY):
    """
    Get final validation function for piece.
    """
    def validate_true(*args):
        return True

    return partial((
        validate_true,  # No piece
        partial(validate_move, board),  # Bishop
        partial(validate_ending, board),  # King
        partial(validate_ending, board),  # Knight
        validate_true,  # Pawn
        partial(validate_move, board),  # Queen
        partial(validate_move, board)  # Rook
        )[piece // 2], posX, posY)


@lru_cache()
def moves_for_pawn(board, piece, posX, posY):
    return tuple(_moves_for_pawn(board, piece, posX, posY))


def _moves_for_pawn(board, piece, posX, posY):
    """
    Get all possible moves for pawn.
    """
    if (
            is_on_board(posX, posY, (0, -1))
            and (not board[posY - 1][posX])):
        yield (0, -1)
    if (
            posY == 6
            and (not board[posY - 1][posX])
            and (not board[posY - 2][posX])):
        yield (0, -2)
    if (
            is_on_board(posX, posY, (1, -1))
            and inactive_piece(board[posY - 1][posX + 1])):
        yield (1, -1)
    if (
            is_on_board(posX, posY, (1, 1))
            and inactive_piece(board[posY + 1][posX + 1])):
        yield (1, 1)
    if piece & 0x10:
        yield ()  # en passant


@lru_cache()
def moves_for_piece(board, piece, posX, posY):
    """
    Get all possible moves for piece type.
    """
    return tuple(filter(partial(is_on_board, posX, posY), (
        (),  # No piece
        BISHOP_MOVES,
        KING_MOVES,
        KNIGHT_MOVES,
        moves_for_pawn(board, piece, posX, posY),
        QUEEN_MOVES,
        ROOK_MOVES
      )[piece // 2]))


@lru_cache()
def valid_moves_for_piece(board, piece, posX, posY):
    """
    Get all valid moves for piece type.
    """
    return tuple(filter(
        validation_for_piece(board, piece, posX, posY),
        moves_for_piece(board, piece, posX, posY)))


@lru_cache()
def lookahead_boards_for_piece(board, check, piece, posX, posY):
    """
    Get all future board states.
    """
    def mutate_board(move):
        new_state = list(map(list, board))
        new_state[posY][posX] = 0
        new_state[posY + move[1]][posX + move[0]] = piece
        return swap(tuple(map(tuple, new_state)))

    _valid_moves_for_piece = valid_moves_for_piece(board, piece, posX, posY)
    if check:
        _valid_moves_for_piece = filter(
            lambda move: board[posY + move[1]][posX + move[0]] == KING,
            _valid_moves_for_piece)
    return tuple(map(mutate_board, _valid_moves_for_piece))


def lookahead_check_for_piece(board, piece, posX, posY):
    """
    Get possiblity of check in all future board states.
    """
    return map(
        lambda move: board[posY + move[1]][posX + move[0]] == KING,
        valid_moves_for_piece(board, piece, posX, posY))


@lru_cache()
def lookahead_check(board):
    return any(chain.from_iterable(
        starmap(partial(lookahead_check_for_piece, board), active_pieces(board))))


@lru_cache()
def active_piece(piece):
    """
    Validate piece as active.
    """
    return piece & 1 and piece & 0xE


@lru_cache()
def inactive_piece(piece):
    """
    Validate piece as inactive.
    """
    return (not piece & 1) and piece & 0xE


@lru_cache()
def active_pieces(board):
    """
    Get all pieces for current player.
    """
    return tuple(chain.from_iterable(
        map(
            lambda posY, row: filter(None, map(
                lambda posX, piece:
                    (piece, posX, posY)
                    if active_piece(piece) else
                    None,
                count(), row)),
            count(), board)))


@lru_cache()
def swap(board):
    """
    Rotate active player.
    """
    return tuple(list(map(
        lambda row: tuple(list(map(
            lambda pp:
                pp & 0xE | (1 if inactive_piece(pp) else 0),
            row))[::-1]),
        board))[::-1])


class BoardModel:
    """
    Chess board model.
    """

    def __init__(self, board=None):
        """
        Set up board.
        """
        self.board = tuple(map(tuple, board or INITIAL_BOARD))
        self.move_count = 1
        self.moves_since_pawn = 0

    def __bool__(self):
        """
        Ensure active player king on board.
        """
        return self.moves_since_pawn >= 50 or self.has_kings()

    def __contains__(self, piece):
        """
        Ensure piece on board.
        """
        return any(map(lambda row: piece in row, self.board))

    def swap(self):
        """
        Rotate active player.
        """
        return BoardModel(swap(self.board))

    def update(self, state):
        """
        Validate and return new board state.
        """
        mutation = tuple(filter(None, chain.from_iterable(map(
            lambda posY, old_row, new_row: map(
                lambda posX, old_piece, new_piece:
                    None
                    if old_piece == new_piece else
                    (posX, posY, old_piece, new_piece),
                count(),
                old_row, new_row),
            count(),
            self.board, state))))
        if len(mutation) != 2:
            raise RuntimeError
        if mutation[0][3] == 0:
            old, new = mutation
        elif mutation[1][3] == 0:
            new, old = mutation
        else:
            raise RuntimeError
        if active_piece(new[2]):
            raise RuntimeError
        posX, posY, piece, _ = old
        if not active_piece(piece):
            raise RuntimeError
        if old[2] != new[3]:
            raise RuntimeError
        move = (new[0] - posX, new[1] - posY)
        if move not in valid_moves_for_piece(self.board, piece, posX, posY):
            raise RuntimeError
        board = BoardModel(swap(state))
        board.move_count = self.move_count + 1
        board.moves_since_pawn = 0 if piece == 9 else (self.moves_since_pawn + 1)
        return board

    def lookahead_boards(self, n, active=False):
        """
        Provide an iterable of valid moves for current board state.
        """
        check = lookahead_check(self.board)
        if not self:
            return iter((((self.board if active else swap(self.board)) for _ in range(n)),))
        if n == 0:
            return iter(((),))
        return chain.from_iterable(
            map(
                lambda board: map(
                    lambda n: (board if active else swap(board),) + tuple(n),
                    BoardModel(board).lookahead_boards(n - 1, not active)),
                chain.from_iterable(
                    starmap(
                        partial(lookahead_boards_for_piece, self.board, check),
                        active_pieces(self.board)))))

    def has_kings(self):
        """
        Ensure active kings on board.
        """
        return (KING | 1) in self and KING in self
