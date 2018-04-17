from neuralknight.models.base_agent import BaseAgent


class MockAgent(BaseAgent):
    def __init__(self, testapp, moves, game_id=None):
        self.testapp = testapp
        self.args = []
        self.kwargs = []
        self.moves = iter(moves)
        super().__init__(game_id)

    def request(self, method, resource, *args, data=None, json=None, **kwargs):
        if method == 'POST':
            return self.testapp.post_json(resource, data, status='*')
        if method == 'PUT':
            return self.testapp.put(resource, json, status='*')
        if method == 'GET':
            return self.testapp.get(resource, data, status='*')

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
    player1 = MockAgent(testapp, [])
    game = testapp.post_json('/v1.0/games', {'id': player1.agent_id}, status='*').json
    player1.game_id = game['id']
    player2 = MockAgent(testapp, [], game['id'])
    assert game
    assert player1
    assert player2
