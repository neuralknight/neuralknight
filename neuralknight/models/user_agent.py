from .base_agent import BaseAgent


class UserAgent(BaseAgent):
    '''Human Agent'''

    def __init__(self, game_id, player):
        super().__init__(game_id, player)
        self.request('POST', '/issue-agent', {'id': game_id, 'player': 2})

    def play_round(self, move):
        proposal = self.state
        proposal[move[1][0]][move[1][1]] = proposal[move[0][0]][move[0][1]]
        proposal[move[0][0]][move[0][1]] = 0
        self.put_board(proposal)
