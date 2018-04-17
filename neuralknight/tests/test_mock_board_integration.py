from neuralknight.models.base_agent import BaseAgent


class MockAgent(BaseAgent):
    def __init__(self, testapp, moves, game_id, player):
        self.testapp = testapp
        self.args = []
        self.kwargs = []
        self.moves = iter(moves)
        super().__init__(game_id, player)

    def play_round(self, *args, **kwargs):
        self.args.append(args)
        self.kwargs.append(kwargs)


def test_home_response(testapp):
    response = testapp.get('/')
    assert response.status_code == 200


def test_agent_play_through(testapp):
    response = testapp.get('/v1.0/games')
    assert response.status_code == 200


def test_agent_play_no_moves(testapp):
    game = testapp.post_json('/v1.0/games').json
    player1 = MockAgent(testapp, [], game['id'], 1)
    player2 = MockAgent(testapp, [], game['id'], 2)
    assert game
    assert player1
    assert player2
