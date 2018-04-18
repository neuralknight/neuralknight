from ..models import BaseBoard, BaseAgent, BoardModel


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
        return self._board.slice_cursor_v1(self.cursor)
        return {
            'cursor': self.cursor,
            'boards': self.board
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


def test_player_connection(testapp):
    '''Assert players connect to board'''
    mockboard = MockBoard(testapp)
    player1 = testapp.post_json('/issue-agent', {'id': mockboard.id}).json
    player2 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'player': 2}).json
    assert player1
    assert player2

# this needs to change - need to check multi-gets
def test_get_boards(testapp):
    mockboard = MockBoard(testapp, 1)
    player1 = testapp.post_json('/issue-agent', {'id': mockboard.id}).json
    player2 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'player': 2}).json
    assert BaseAgent.AGENT_POOL[player1['agent_id']].get_boards()
    

def test_choose_valid_move(testapp):
    '''Assert agent chooses valid move and game ends'''
    mockboard = MockBoard(testapp)
    player1 = testapp.post_json('/issue-agent', {'id': mockboard.id}).json
    player2 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'player': 2}).json
    state = mockboard.current_state_v1()
    assert BaseAgent.AGENT_POOL[player1['agent_id']].play_round()
    assert state == mockboard.current_state_v1()

def test_play_game(testapp):
    mockboard = MockBoard(testapp)
    player1 = testapp.post_json('/issue-agent', {'id': mockboard.id}).json
    player2 = testapp.post_json('/issue-agent', {'id': mockboard.id, 'player': 2}).json
    assert BaseAgent.AGENT_POOL[player1['agent_id']].play_game()
