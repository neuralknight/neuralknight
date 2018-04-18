from .base_agent import BaseAgent


class Agent(BaseAgent):
    '''Computer Agent'''

    def get_boards(self):
        '''Retrieves potential board states'''
        params = {'lookahead': self.lookahead}
        data = self.request('GET', '/v1.0/games/{}/states'.format(self.game_id))
        boards = data['boards']
        while data['cursor'] is not None:
            params = {'cursor': data['cursor'], 'lookahead': self.lookahead}
            data = self.request(
                'GET', '/v1.0/games/{}/states'.format(self.game_id), params=params)
            for board in data['boards']:
                boards.append(board)
        return boards

    def play_round(self):
        '''Play a game round'''
        boards = self.get_boards()
        best_board = self.evaluate_boards(boards)
        return self.put_board(best_board)

    def play_game(self):
        '''Play a game'''
        game_over = False
        while not game_over:
            game_over = self.play_round()
        return game_over
