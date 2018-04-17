from neuralknight.models.base_agent import BaseAgent


class MockAgent(BaseAgent):
    def __init__(self, api_url, moves, game_id=None):
        self.api_url = api_url
        self.args = []
        self.kwargs = []
        self.moves = iter(moves)
        super().__init__(game_id)

    def play_round(self, *args, **kwargs):
        self.args.append(args)
        self.kwargs.append(kwargs)
        return next(self.moves)


def test_home_response(testapp):
    response = testapp.get('/', status='*')
    assert response.status_code == 200


def test_agent_play_through(testapp):
    response = testapp.get('/v1.0/games', status='*')
    assert response.status_code == 200


def test_agent_play_no_moves(testapp):
    player1 = MockAgent('', [])
    game = testapp.post_json('/v1.0/games', {'id': player1.agent_id}, status='*').json
    player2 = MockAgent('', [], game['id'])
    assert game
    assert player1
    assert player2
