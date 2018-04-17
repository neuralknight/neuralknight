from ..models import BaseBoard
from ..models import Agent


class MockBoard(BaseBoard):
    def __init__(self, _id=None):
        super().__init__(_id)
        self.args = {}
        self.kwargs = {}
        self.board = [[[[0 for i in range(8)] for j in range(8)]]]

    def slice_cursor_v1(self, *args, **kwargs):
        self.args['slice_cursor_v1'] = args
        self.kwargs['slice_cursor_v1'] = kwargs
        return {
            'cursor': None,
            'boards': self.board
        }

    def add_player_v1(self, *args, **kwargs):
        self.args['add_player_v1'] = args
        self.kwargs['add_player_v1'] = kwargs
        self.player2 = 1
        self.poke_player(False)
        return {}

    def update_state_v1(self, *args, **kwargs):
        self.args['update_state_v1'] = args
        self.kwargs['update_state_v1'] = kwargs
        return {'end': True}


def test_make_move(testapp):
    mockboard = MockBoard()
    player1 = Agent(mockboard.id)
    player1.player = 2
    player2 = Agent(mockboard.id)

    assert player1.play_round()
