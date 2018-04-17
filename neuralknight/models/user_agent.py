from .base_agent import BaseAgent


class UserAgent(BaseAgent):
    '''Human Agent'''
    
    def __init__(self, _id):
        super().__init__(_id)
        self.request('POST', f'/games/{_id}', {'id': self.agent_id}).json()
        self.request('POST', '/issue-agent', {'id': _id}).json()

    def play_round(self, move):
        proposal = self.state
        proposal[move[1][0]][move[1][1]] = proposal[move[0][0]][move[0][1]]
        proposal[move[0][0]][move[0][1]] = 0
        self.put_board(proposal)
