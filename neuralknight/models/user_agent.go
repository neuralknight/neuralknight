from operator import methodcaller

from .agent import Agent


class UserAgent(Agent):
    '''Human Agent'''

    def play_round(self, move):
        if move is None:
            return
        proposal = self.get_state()
        if isinstance(proposal, dict):
            return
        proposal = list(map(list, map(bytes.fromhex, proposal)))
        proposal[move[1][0]][move[1][1]] = proposal[move[0][0]][move[0][1]]
        proposal[move[0][0]][move[0][1]] = 0
        return self.put_board(tuple(map(bytes, proposal)))

    def put_board(self, board):
        '''Sends move selection to board state manager'''
        data = {'state': tuple(map(methodcaller('hex'), board))}
        data = self.request('PUT', f'/v1.0/games/{ self.game_id }', json=data)
        self.game_over = data.get('end', False)
        if self.game_over:
            return self.close()
        return data
