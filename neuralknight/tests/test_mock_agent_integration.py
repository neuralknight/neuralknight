from ..models import BaseBoard
from ..models import Agent


class MockBoard(BaseBoard):
    def __init__(self, _id=None):
        super().__init__(_id)
        self.args = {}
        self.kwargs = {}
        self.board = [[[[0 for i in range(8)] for j in range(8)]]]

    def request(self, method, resource, *args, data=None, json=None, **kwargs):
        if method == 'POST':
            return self.testapp.post_json(resource, data, status='*')
        if method == 'PUT':
            return self.testapp.put(resource, json, status='*')
        if method == 'GET':
            return self.testapp.get(resource, data, status='*')

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
    player1 = Agent(str(mockboard.id))
    player1.player = 2
    player2 = Agent(str(mockboard.id))

    assert player1.play_round()
