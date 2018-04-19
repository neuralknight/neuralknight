from ..models.base_agent import BaseAgent


class MockAgent(BaseAgent):
    def __init__(self, testapp, moves, game_id, player):
        self.testapp = testapp
        self.args = []
        self.kwargs = []
        self.moves = iter(moves)
        self.past_end = False
        super().__init__(game_id, player)

    def play_round(self, *args, **kwargs):
        self.args.append(args)
        self.kwargs.append(kwargs)
        try:
            return self.put_board(next(self.moves))
        except StopIteration:
            self.past_end = True
        return {}


def test_home_endpoint(testapp):
    response = testapp.get('/')
    assert response.status_code == 200


def test_games_endpoint(testapp):
    response = testapp.get('/v1.0/games')
    assert response.status_code == 200
    assert 'ids' in response.json


def test_agent_play_no_moves(testapp):
    game = testapp.post_json('/v1.0/games').json
    player1 = MockAgent(testapp, [], game['id'], 1)
    player2 = MockAgent(testapp, [], game['id'], 2)
    assert player1.agent_id != player2.agent_id
    assert player1.args.pop() == ()
    assert player1.kwargs.pop() == {}
    assert player1.past_end
    assert not player2.args
    assert not player2.kwargs
    assert not player2.past_end


# def test_agent_play_through(testapp):
#     player1_moves = [tuple(map(bytes, (
#         (12, 6, 2, 10, 4, 2, 6, 12),
#         (8, 8, 8, 8, 8, 8, 8, 8),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 0, 0, 9, 0, 0, 0),
#         (9, 9, 9, 9, 0, 9, 9, 9),
#         (13, 7, 3, 11, 5, 3, 7, 13)))), tuple(map(bytes, (
#
#         (12, 6, 2, 10, 4, 2, 6, 12),
#         (8, 8, 8, 8, 8, 0, 8, 8),
#         (0, 0, 0, 0, 0, 8, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 11),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 0, 0, 9, 0, 0, 0),
#         (9, 9, 9, 9, 0, 9, 9, 9),
#         (13, 7, 3, 0, 5, 3, 7, 13))))]
#     player1_moves = [player1_moves[0]]
#     player2_moves = [tuple(map(bytes, (
#         (12, 6, 2, 4, 10, 2, 6, 12),
#         (8, 8, 8, 0, 8, 8, 8, 8),
#         (0, 0, 0, 8, 0, 0, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 9, 0, 0, 0, 0, 0),
#         (9, 9, 0, 9, 9, 9, 9, 9),
#         (13, 7, 3, 5, 11, 3, 7, 13)))), tuple(map(bytes, (
#
#         (12, 6, 2, 4, 0, 2, 6, 12),
#         (8, 8, 8, 0, 8, 8, 8, 8),
#         (0, 0, 0, 8, 0, 0, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (10, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 9, 0, 0, 0, 0, 0),
#         (9, 9, 0, 9, 9, 9, 9, 9),
#         (13, 7, 3, 5, 11, 3, 7, 13))))]
#     player2_moves = []
#     game = testapp.post_json('/v1.0/games').json
#     player1 = MockAgent(testapp, player1_moves, game['id'], 1)
#     player2 = MockAgent(testapp, player2_moves, game['id'], 2)
#     assert len(player1.args) == 1
#     assert len(player2.args) == 1
#     assert not player1.past_end
#     assert player2.past_end
