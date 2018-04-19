from concurrent.futures import ProcessPoolExecutor
from functools import partial
from itertools import groupby, repeat
from operator import itemgetter, methodcaller
from random import randint

from .base_agent import BaseAgent


def call(_call, *args, **kwargs):
    return _call(*args, **kwargs)


class Agent(BaseAgent):
    '''Computer Agent'''

    def get_boards(self, cursor):
        '''Retrieves potential board states'''
        params = {'lookahead': self.lookahead}
        if cursor:
            params['cursor'] = cursor
        return self.request('GET', '/v1.0/games/{}/states'.format(self.game_id), params=params)

    def get_boards_cursor(self):
        cursor = True
        while cursor:
            board_options = self.get_boards(cursor)
            cursor = board_options['cursor']
            yield board_options['boards']

    def play_round(self):
        '''Play a game round'''
        with ProcessPoolExecutor(4) as executor:
            print('starting thoughts', executor)
            # best_boards = [(root_value, root), ...]
            best_boards = executor.map(
                call,
                map(partial(methodcaller, 'evaluate_boards'), self.get_boards_cursor()),
                repeat(self),
                chunksize=30)
            # best_boards = [(root_value, [(root_value, root), ...]), ...]
            best_boards = groupby(sorted(best_boards, reverse=True), itemgetter(0))
            # _, best_boards = (root_value, [(root_value, root), ...])
            _, best_boards = next(best_boards)
            # best_boards = [root, ...]
            best_boards = tuple(map(itemgetter(1), best_boards))
            return self.put_board(best_boards[randint(0, len(best_boards)-1)])

    def play_game(self):
        '''Play a game'''
        game_over = False
        while not game_over:
            game_over = self.play_round()
        return game_over
