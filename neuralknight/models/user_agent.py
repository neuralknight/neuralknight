from .base_agent import BaseAgent


class UserAgent(BaseAgent):
    '''Human Agent'''

    def make_move(self, move):
        proposal = self.state
        proposal[move[1][0]][move[1][1]] = proposal[move[0][0]][move[0][1]]
        proposal[move[0][0]][move[0][1]] = 0
        self.put_board(proposal)
