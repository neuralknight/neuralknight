from ..models import BaseBoard, BaseAgent


class MockBoard(BaseBoard):
    def __init__(self, testapp, cursor=None):
        self.testapp = testapp
        self.args = {}
        self.kwargs = {}
        self.cursor = cursor
        super().__init__([[0 for i in range(8)] for j in range(8)])

    def slice_cursor_v1(self, *args, **kwargs):
        self.args['slice_cursor_v1'] = args
        self.kwargs['slice_cursor_v1'] = kwargs
        return {
            'cursor': self.cursor,
            'boards': [(self.board,)]
        }

    def add_player_v1(self, *args, **kwargs):
        self.args['add_player_v1'] = args
        self.kwargs['add_player_v1'] = kwargs
        player = args[1]
        if self.player1:
            self.player2 = player
        else:
            self.player1 = player
        self.poke_player(False)
        return {}

    def update_state_v1(self, *args, **kwargs):
        self.args['update_state_v1'] = args
        self.kwargs['update_state_v1'] = kwargs
        return {'end': True}


# def test_player_connection(testapp):
#     '''Assert players connect to board'''
#     mockboard = MockBoard(testapp)
#     player1 = testapp.post_json('/issue-agent', {'id': mockboard.id}).json
#     player2 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'player': 2}).json
#     assert player1
#     assert player2


# this needs to change - need to check multi-gets
# def test_get_boards(testapp):
#     mockboard = MockBoard(testapp, 1)
#     player1 = testapp.post_json('/issue-agent', {'id': mockboard.id}).json
#     assert player1['agent_id'] in BaseAgent.AGENT_POOL
#     player2 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'player': 2}).json
#     assert player2
#     assert player1['agent_id'] not in BaseAgent.AGENT_POOL


# def test_choose_valid_move(testapp):
#     '''Assert agent chooses valid move and game ends'''
#     mockboard = MockBoard(testapp)
#     state = mockboard.current_state_v1()
#     player1 = testapp.post_json('/issue-agent', {'id': mockboard.id}).json
#     # assert player1['agent_id'] in BaseAgent.AGENT_POOL
#     player2 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'player': 2}).json
#     assert state == mockboard.current_state_v1()
#     assert player2
#     assert player1['agent_id'] not in BaseAgent.AGENT_POOL


# def test_play_game(testapp):
#     mockboard = MockBoard(testapp)
#     player1 = testapp.post_json('/issue-agent', {'id': mockboard.id}).json
#     # assert player1['agent_id'] in BaseAgent.AGENT_POOL
#     player2 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'player': 2}).json
#     assert player2
#     assert player1['agent_id'] not in BaseAgent.AGENT_POOL


def test_user_connection(testapp):
    mockboard = MockBoard(testapp)
    player1 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'user': True}).json
    assert player1
