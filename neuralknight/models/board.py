"""
Chess state handling model.
"""

from concurrent.futures import ThreadPoolExecutor
from json import dumps

from .base_board import BaseBoard
from .table_board import TableBoard
from .table_game import TableGame

__all__ = ['Board']


class Board(BaseBoard):
    """
    Chess board interaction model.
    """

    PORT = 8080
    API_URL = 'http://localhost:{}'.format(PORT)

    def __init__(self, board=None, _id=None):
        """
        Set up board.
        """
        super().__init__(board, _id)
        self.executor = ThreadPoolExecutor()

    def __bool__(self):
        """
        Ensure active player king on board.
        """
        return bool(self._board)

    def __contains__(self, piece):
        """
        Ensure piece on board.
        """
        return piece in self._board

    def __iter__(self):
        """
        Provide next boards at one lookahead.
        """
        return self._board.lookahead_boards(1)

    def __repr__(self):
        """
        Output the raw view of board.
        """
        return f'Board({ self.board !r})'

    def __str__(self):
        """
        Output the emoji view of board.
        """
        return str(self._board)

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
                board_state=dumps(self.board),
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

    def handle_future(self, future):
        """
        Handle a future from and async request.
        """
        future.result().json()

    def lookahead_boards(self, n=4):
        return self._board.lookahead_boards(n)

    def slice_cursor_v1(self, cursor=None, lookahead=1):
        """
        Retrieve REST cursor slice.
        """
        return self.board.slice_cursor_v1(cursor, lookahead)

    def update(self, state):
        """
        Validate and return new board state.
        """
        return Board(self._board.update(state), self.id)

    def update_state_v1(self, dbsession, state):
        """
        Make a move to a new state on the board.
        """
        moving_player = self.active_player()
        board = self.update(state)
        board.player1 = self.player1
        board.player2 = self.player2
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
