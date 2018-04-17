from ..models import BaseBoard
from ..models import Agent


class MockBoard(BaseBoard):
    def __init__(self, testapp, _id=None):
        self.testapp = testapp
        self.args = {}
        self.kwargs = {}
        super().__init__(_id, [[[[0 for i in range(8)] for j in range(8)]]])

    def request(self, method, resource, *args, data=None, json=None, **kwargs):
        if method == 'POST':
            return self.testapp.post_json(resource, data).json
        if method == 'PUT':
            return self.testapp.put(resource, json).json
        if method == 'GET':
            return self.testapp.get(resource, data).json

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
    mockboard = MockBoard(testapp)
    player1 = testapp.post_json('/issue-agent', {'id': mockboard.id}).json
    player2 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'player': 2}).json

    assert player1
    assert player2
