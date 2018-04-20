"""
Chess state handling model.
"""

from itertools import chain, count, groupby, islice, starmap
from functools import partial, lru_cache
from operator import itemgetter
from uuid import uuid4

from .board_constants import (
    INITIAL_BOARD, BISHOP, KING, KNIGHT, QUEEN, ROOK, unit,
    BISHOP_MOVES, KING_MOVES, KNIGHT_MOVES, QUEEN_MOVES, ROOK_MOVES)

__all__ = ['BoardModel', 'CursorDelegate', 'InvalidMove']


class InvalidMove(RuntimeError):
    pass


class CursorDelegate:
    def __init__(self):
        self.cursors = {}

    def get_cursor(self, board, cursor, lookahead, complete):
        """
        Retrieve iterable for cursor.
        """
        if cursor in self.cursors:
            return self.cursors.pop(cursor)
        if complete:
            it = board.lookahead_boards(lookahead)
        else:
            it = board.prune_lookahead_boards(lookahead)
        it = groupby(it, itemgetter(0))
        return next(it)[1], it

    def slice_cursor_v1(self, board, cursor, lookahead, complete):
        """
        Retrieve REST cursor slice.
        """
        it, cur = self.get_cursor(board, cursor, lookahead, complete)
        slen = (900 // lookahead) if complete else 450
        boards = tuple(islice(it, slen))
        if len(boards) < slen:
            if complete:
                return {'cursor': None, 'boards': boards}
            try:
                it = next(cur)[1]
            except StopIteration:
                return {'cursor': None, 'boards': boards}
        cursor = str(uuid4())
        self.cursors[cursor] = (it, cur)
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
        )[(piece & 0xE) // 2], posX, posY)


def moves_for_pawn(board, piece, posX, posY):
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
            is_on_board(posX, posY, (-1, -1))
            and inactive_piece(board[posY - 1][posX - 1])):
        yield (-1, -1)
    if (
            is_on_board(posX, posY, (1, -1))
            and inactive_piece(board[posY - 1][posX + 1])):
        yield (1, -1)
    if piece & 0x10:
        yield ()  # en passant


def moves_for_king(board, piece, posX, posY):
    """
    Get castling.
    """
    return
    if piece & 0x10:
        if (board[posY][0] & 0x10) and (board[posY][0] & 1) and (board[posY][0] & 0xE) == ROOK:
            yield (-2, 0)
            yield (-3, 0)
        if (board[posY][7] & 0x10) and (board[posY][7] & 1) and (board[posY][7] & 0xE) == ROOK:
            yield (2, 0)


@lru_cache()
def moves_for_piece(board, piece, posX, posY):
    """
    Get all possible moves for piece type.
    """
    return tuple(filter(partial(is_on_board, posX, posY), (
        (),  # No piece
        BISHOP_MOVES,
        chain(KING_MOVES, moves_for_king(board, piece, posX, posY)),
        KNIGHT_MOVES,
        moves_for_pawn(board, piece, posX, posY),
        QUEEN_MOVES,
        ROOK_MOVES
      )[(piece & 0xE) // 2]))


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
        if piece == 9 and posY == 1:
            for promote in (BISHOP, KNIGHT, QUEEN, ROOK):
                new_state[posY + move[1]][posX + move[0]] = promote | 1
                yield swap(tuple(map(bytes, new_state)))
        else:
            new_state[posY + move[1]][posX + move[0]] = piece & 0xF
            yield swap(tuple(map(bytes, new_state)))

    _valid_moves_for_piece = valid_moves_for_piece(board, piece, posX, posY)
    if check:
        _valid_moves_for_piece = filter(
            lambda move: board[posY + move[1]][posX + move[0]] & 0xE == KING,
            _valid_moves_for_piece)
    return tuple(chain.from_iterable(map(mutate_board, _valid_moves_for_piece)))


def lookahead_check_for_piece(board, piece, posX, posY):
    """
    Get possiblity of check in all future board states.
    """
    return map(
        lambda move: (board[posY + move[1]][posX + move[0]] & 0xF) == KING,
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
        lambda row: bytes(map(
            lambda pp:
                (pp ^ 1) if pp else 0,
            row))[::-1],
        board))[::-1])


def make_tuple(*args):
    return args


class BoardModel:
    """
    Chess board model.
    """

    def __init__(self, board=None):
        """
        Set up board.
        """
        self.board = board or INITIAL_BOARD
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
        return any(map(lambda row: piece in row or (piece | 0x10) in row, self.board))

    def swap(self):
        """
        Rotate active player.
        """
        return swap(self.board)

    def validate_mutation(self, mutation):
        if len(mutation) != 2:
            raise InvalidMove
        if mutation[0][3] == 0:
            old, new = mutation
        elif mutation[1][3] == 0:
            new, old = mutation
        else:
            raise InvalidMove
        if active_piece(new[2]):
            raise InvalidMove
        posX, posY, piece, _ = old
        if not active_piece(piece):
            raise InvalidMove
        if (piece & 0xF) != (new[3] & 0xF):
            if not ((piece & 0xF) == 9 and new[0] == 0):
                raise InvalidMove
        move = (new[0] - posX, new[1] - posY)
        if move not in valid_moves_for_piece(self.board, piece, posX, posY):
            raise InvalidMove
        if (piece & 0xF) == 9:
            self.moves_since_pawn = 0
        return True

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
        if self.validate_mutation(mutation):
            board = BoardModel(swap(state))
            board.move_count = self.move_count + 1
            board.moves_since_pawn = self.moves_since_pawn + 1
            return board
        raise InvalidMove

    def lookahead_boards_for_board(self, check):
        return chain.from_iterable(
            starmap(
                partial(lookahead_boards_for_piece, self.board, check),
                active_pieces(self.board)))

    def _valid_root_lookahead_boards_end(self):
        """
        Provide an iterable of valid moves for current board state.
        """
        check = lookahead_check(self.board)
        return all(map(
            lambda board: (KING | 1) in BoardModel(board),
            self.lookahead_boards_for_board(check)))

    def _valid_root_lookahead_boards(self, check):
        """
        Provide an iterable of valid moves for current board state.
        """
        return filter(
            lambda board: BoardModel(board)._valid_root_lookahead_boards_end(),
            self.lookahead_boards_for_board(check))

    def _prune_lookahead_boards(self, n, active=True):
        """
        Provide an iterable of valid moves for current board state.
        """
        check = lookahead_check(self.board)
        if n == 1:
            return iter((self.board if active else swap(self.board),))
        return chain.from_iterable(map(
            lambda board: BoardModel(board)._prune_lookahead_boards(n - 1, not active),
            self.lookahead_boards_for_board(check)))

    def prune_lookahead_boards(self, n):
        """
        Provide an iterable of valid moves for current board state.
        """
        check = lookahead_check(self.board)
        return chain.from_iterable(
            map(
                lambda board: map(
                    partial(make_tuple, swap(board)),
                    BoardModel(board)._prune_lookahead_boards(n - 1)),
                self._valid_root_lookahead_boards(check)))

    def _lookahead_boards(self, n, active=False):
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
                    lambda t: (board if active else swap(board),) + tuple(t),
                    BoardModel(board)._lookahead_boards(n - 1, not active)),
                self.lookahead_boards_for_board(check)))

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
                    lambda t: (board if active else swap(board),) + tuple(t),
                    BoardModel(board)._lookahead_boards(n - 1, not active)),
                self._valid_root_lookahead_boards(check)))

    def has_kings(self):
        """
        Ensure active kings on board.
        """
        return (KING | 1) in self and KING in self
