"""
Chess state handling model.
"""

from concurrent.futures import ThreadPoolExecutor
from itertools import count
from json import dumps

from .base_board import BaseBoard, NoBoard
from .table_board import TableBoard
from .table_game import TableGame

__all__ = ['Board', 'NoBoard']


class Board(BaseBoard):
    """
    Chess board interaction model.
    """

    EMOJI = [
      '⌛', '‼',
      '♝', '♗', '♚', '♔', '♞', '♘', '♟', '♙', '♛', '♕', '♜', '♖', '▪', '▫']

    def __init__(self, board=None, _id=None, active_player=True):
        """
        Set up board.
        """
        super().__init__(board, _id, active_player)
        self.executor = ThreadPoolExecutor()

    def __repr__(self):
        """
        Output the raw view of board.
        """
        return f'Board({ self.board !r})'

    def __str__(self):
        """
        Output the emoji view of board.
        """
        if self._active_player:
            def piece_to_index(piece):
                return (piece & 0xF)
        else:
            def piece_to_index(piece):
                return (piece & 0xE) | (0 if piece & 1 else 1)

        return '\n'.join(map(
            lambda posY, row: ''.join(map(
                lambda posX, piece: self.EMOJI[
                    piece_to_index(piece)
                    if piece else
                    14 + ((posY + posX) % 2)],
                count(), row)),
            count(),
            self.board if self._active_player else reversed(
                [reversed(row) for row in self.board])))

    def add_player_v1(self, dbsession, player):
        """
        Player 2 joins game.
        """
        assert player
        if self.player1:
            self.player2 = player
            table_game = TableGame(
                game=self.id,
                player_one=self.player1,
                player_two=self.player2,
                one_won=True,
                two_won=True)
            table_board = TableBoard(
                board_state=dumps(tuple(map(tuple, self.board))),
                move_num=self._board.move_count,
                player=self.active_player(),
                game=self.id)
            table_board.game_link.append(table_game)
            dbsession.add(table_game)
            dbsession.add(table_board)
            self.poke_player(False)
            return {}
        self.player1 = player
        return {}

    def slice_cursor_v1(self, cursor=None, lookahead=1, complete=False):
        """
        Retrieve REST cursor slice.
        """
        return self.cursor_delegate.slice_cursor_v1(self._board, cursor, int(lookahead), complete)

    def update_state_v1(self, dbsession, state):
        """
        Make a move to a new state on the board.
        """
        moving_player = self.active_player()
        board = self.update(state)
        table_game = dbsession.query(TableGame).filter(
            TableGame.game == board.id).first()
        table_board = TableBoard(
            board_state=dumps(tuple(map(tuple, board.board))),
            move_num=board._board.move_count,
            player=board.active_player(),
            game=board.id)
        if table_game:  # TODO(grandquista)
            table_board.game_link.append(table_game)
        dbsession.add(table_board)
        if board:
            board.poke_player(False)
            return {'end': False}
        board.poke_player(True, moving_player)
        if board._board.has_kings():
            table_game.one_won = False
            table_game.two_won = False
        elif moving_player == table_game.player_one:
            table_game.two_won = False
        else:
            table_game.one_won = False
        board.close()
        return {'end': True}
