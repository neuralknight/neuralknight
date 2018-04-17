"""
Chess state handling model.
"""

import requests

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from itertools import chain, count, islice, starmap
from json import dumps
from functools import partial
from uuid import uuid4

from .base_board import BaseBoard
from .board_constants import (
    EMOJI, unit,
    BISHOP, KING, KNIGHT, PAWN, QUEEN, ROOK,
    BISHOP_MOVES, KING_MOVES, KNIGHT_MOVES, QUEEN_MOVES, ROOK_MOVES)
from .table_board import TableBoard
from .table_game import TableGame

__all__ = ['Board', 'BISHOP', 'KING', 'KNIGHT', 'PAWN', 'QUEEN', 'ROOK']

PORT = 8080
API_URL = 'http://localhost:{}'.format(PORT)


class Board(BaseBoard):
    """
    Chess board state model.
    """

    def __init__(
            self,
            board=None, active_player=True, _id=None, *,
            player1=None, player2=None):
        """
        Set up board.
        """
        super().__init__(_id, board)
        self._active_player = active_player
        self.active_uuid = True
        self.cursors = {}
        self.executor = ThreadPoolExecutor()
        self.move_count = 1
        self.moves_since_pawn = 0
        self.player1 = player1
        self.player2 = player2

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

    def __iter__(self):
        """
        Provide next boards at one lookahead.
        """
        return self.lookahead_boards(1)

    def __repr__(self):
        """
        Output the raw view of board.
        """
        return f'Board({ self.board !r})'

    def __str__(self):
        """
        Output the emoji view of board.
        """
        if self.active_uuid:
            def piece_to_index(piece):
                return piece
        else:
            def piece_to_index(piece):
                return (piece & 0xE) | (0 if piece & 1 else 1)

        return '\n'.join(map(
            lambda posY, row: ''.join(map(
                lambda posX, piece: EMOJI[
                    piece_to_index(piece)
                    if piece else
                    14 + ((posY + posX) % 2)],
                count(), row)),
            count(),
            self.board if self.active_uuid else reversed(
                [reversed(row) for row in self.board])))

    def active_player(self):
        """
        UUID of active player.
        """
        if self.active_uuid:
            return self.player1
        return self.player2

    def add_player_v1(self, dbsession, player2):
        """
        Player 2 joins game.
        """
        self.player2 = player2
        table_game = TableGame(
            game=self.id,
            player_one=self.player1,
            player_two=self.player2,
            one_won=True,
            two_won=True)
        table_board = TableBoard(
            board_state=dumps(self.board),
            move_num=self.move_count,
            player=self.active_player(),
            game=self.id)
        table_board.game_link.append(table_game)
        dbsession.add(table_game)
        dbsession.add(table_board)
        import pdb; pdb.set_trace()
        self.poke_player(False)
        return {}

    def get_cursor(self, cursor, lookahead):
        """
        Retrieve iterable for cursor.
        """
        cursor = cursor or str(uuid4())
        return self.cursors.pop(cursor, self.lookahead_boards(lookahead))

    def handle_future(self, future):
        """
        Handle a future from and async request.
        """
        future.result()

    def request(self, method, resource, *args, **kwargs):
        if method == 'POST':
            self.executor.submit(
                requests.post, f'{ API_URL }{ resource }', **kwargs
            ).add_done_callback(self.handle_future)
        if method == 'PUT':
            self.executor.submit(
                requests.put, f'{ API_URL }{ resource }', **kwargs
            ).add_done_callback(self.handle_future)
        if method == 'GET':
            self.executor.submit(
                requests.get, f'{ API_URL }{ resource }', **kwargs
            ).add_done_callback(self.handle_future)

    def slice_cursor_v1(self, cursor=None, lookahead=1):
        """
        Retrieve REST cursor slice.
        """
        it = self.get_cursor(cursor, lookahead)
        slen = 300 // lookahead
        boards = tuple([b.board for b in btup] for btup in islice(it, slen))
        if len(boards) < slen:
            return {'cursor': None, 'boards': boards}
        cursor = str(uuid4())
        self.cursors[cursor] = it
        return {'cursor': cursor, 'boards': boards}

    @staticmethod
    def is_on_board(posX, posY, move):
        """
        Validate a move against board bounds.
        """
        return 0 <= (posX + move[0]) < 8 and 0 <= (posY + move[1]) < 8

    def validate_ending(self, posX, posY, move):
        """
        Validate a move against ending location.
        """
        return not self.active_piece(
            self.board[posY + move[1]][posX + move[0]])

    def validate_move(self, posX, posY, move):
        """
        Validate clear path along move.
        """
        return (
            self.validate_ending(posX, posY, move)
            and all(
                map(
                    lambda _range:
                        not self.board
                        [posY + unit(move[1]) * _range]
                        [posX + unit(move[0]) * _range],
                    range(1, max(abs(move[0]), abs(move[1]))))))

    def validation_for_piece(self, piece, posX, posY):
        """
        Get final validation function for piece.
        """
        def validate_true(*args):
            return True

        return partial((
            validate_true,  # No piece
            self.validate_move,  # Bishop
            self.validate_ending,  # King
            self.validate_ending,  # Knight
            validate_true,  # Pawn
            self.validate_move,  # Queen
            self.validate_move  # Rook
            )[piece // 2], posX, posY)

    def moves_for_pawn(self, piece, posX, posY):
        """
        Get all possible moves for pawn.
        """
        if (
                self.is_on_board(posX, posY, (0, -1))
                and (not self.board[posY - 1][posX])):
            yield (0, -1)
        if (
                posY == 6
                and (not self.board[posY - 1][posX])
                and (not self.board[posY - 2][posX])):
            yield (0, -2)
        if (
                self.is_on_board(posX, posY, (1, -1))
                and self.inactive_piece(self.board[posY - 1][posX + 1])):
            yield (1, -1)
        if (
                self.is_on_board(posX, posY, (1, 1))
                and self.inactive_piece(self.board[posY + 1][posX + 1])):
            yield (1, 1)
        if piece & 0x10:
            yield ()  # en passant

    def moves_for_piece(self, piece, posX, posY):
        """
        Get all possible moves for piece type.
        """
        return filter(partial(self.is_on_board, posX, posY), (
            (),  # No piece
            BISHOP_MOVES,
            KING_MOVES,
            KNIGHT_MOVES,
            self.moves_for_pawn(piece, posX, posY),
            QUEEN_MOVES,
            ROOK_MOVES
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
            new_state = deepcopy(self.board)
            new_state[posY][posX] = 0
            new_state[posY + move[1]][posX + move[0]] = piece
            return Board(new_state, not self._active_player)

        return map(
            mutate_board,
            self.valid_moves_for_piece(piece, posX, posY))

    def active_piece(self, piece):
        """
        Validate piece as active.
        """
        if self._active_player:
            return piece & 1 and piece & 0xE
        return (not piece & 1) and piece & 0xE

    def inactive_piece(self, piece):
        """
        Validate piece as inactive.
        """
        if self._active_player:
            return (not piece & 1) and piece & 0xE
        return piece & 1 and piece & 0xE

    def active_pieces(self):
        """
        Get all pieces for current player.
        """
        return chain.from_iterable(
            map(
                lambda posY, row: filter(None, map(
                    lambda posX, piece:
                        (piece, posX, posY)
                        if self.active_piece(piece) else
                        None,
                    count(), row)),
                count(), self.board))

    def swap(self):
        """
        Rotate active player.
        """
        board = Board(list(map(
            lambda row: list(map(
                lambda pp:
                    pp & 0xE | (1 if self.inactive_piece(pp) else 0),
                row))[::-1],
            self.board))[::-1])
        board.active_uuid = not self.active_uuid
        board.player1 = self.player1
        board.player2 = self.player2
        return board

    def update(self, board):
        """
        Validate and return new board state.
        """
        if isinstance(board, Board):
            board = board.board
        mutation = tuple(filter(None, chain.from_iterable(map(
            lambda posY, old_row, new_row: map(
                lambda posX, old_piece, new_piece:
                    None
                    if old_piece == new_piece else
                    (posX, posY, old_piece, new_piece),
                count(),
                old_row, new_row),
            count(),
            self.board, board))))
        if len(mutation) != 2:
            raise RuntimeError
        if mutation[0][3] == 0:
            old, new = mutation
        elif mutation[1][3] == 0:
            new, old = mutation
        else:
            raise RuntimeError
        if self.active_piece(new[2]):
            raise RuntimeError
        posX, posY, piece, _ = old
        if not self.active_piece(piece):
            raise RuntimeError
        if old[2] != new[3]:
            raise RuntimeError
        move = (new[0] - posX, new[1] - posY)
        if move not in self.valid_moves_for_piece(piece, posX, posY):
            raise RuntimeError
        board = Board(board, _id=self.id).swap()
        board.move_count = self.move_count + 1
        if piece != 9:
            board.moves_since_pawn = self.moves_since_pawn + 1
        return board

    def update_state_v1(self, dbsession, state):
        """
        Make a move to a new state on the board.
        """
        moving_player = self.active_player()
        board = self.update(state)
        table_game = dbsession.query(TableGame).filter(
            TableGame.game == board.id).first()
        table_board = TableBoard(
            board_state=dumps(board.board),
            move_num=board.move_count,
            player=board.active_player(),
            game=board.id)
        table_board.game_link.append(table_game)
        dbsession.add(table_board)
        if board:
            self.poke_player(False)
            return {'end': False}
        self.poke_player(True, moving_player)
        if board.has_kings():
            table_game.one_won = False
            table_game.two_won = False
        elif moving_player == table_game.player_one:
            table_game.two_won = False
        else:
            table_game.one_won = False
        self.close()
        return {'end': True}

    def lookahead_boards(self, n=4) -> None:
        """
        Provide an iterable of valid moves for current board state.
        """
        if not self:
            return iter(((self for _ in range(n + 1)),))
        if n == 0:
            return iter(((self,),))
        if n == 1:
            return chain.from_iterable(
                map(
                    lambda board: board.lookahead_boards(n - 1),
                    chain.from_iterable(
                        starmap(
                            self.lookahead_boards_for_piece,
                            self.active_pieces()))))
        return chain.from_iterable(
            map(
                lambda board: map(
                    lambda n: (board,) + n,
                    board.lookahead_boards(n - 1)),
                chain.from_iterable(
                    starmap(
                        self.lookahead_boards_for_piece,
                        self.active_pieces()))))

    def has_kings(self):
        """
        Ensure active kings on board.
        """
        return (KING | 1) in self and KING in self
