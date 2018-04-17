from .base_agent import BaseAgent
import requests

API_URL = 'http://localhost:8080'


class Agent(BaseAgent):
    '''Computer Agent'''

    def get_boards(self):
        '''Retrieves potential board states'''
        response = requests.get('{}/v1.0/games/{}/states'.format(API_URL, self.game_id))
        data = response.json()
        boards = data['boards']
        while data['cursor'] is not None:
            params = {'cursor': data['cursor']}
            response = requests.get(
                '{}/v1.0/games/{}/states'.format(API_URL, self.game_id), params=params)
            data = response.json()
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
            game_over = self.play_round(self.game_id)
