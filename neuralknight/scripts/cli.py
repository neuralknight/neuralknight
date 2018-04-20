import requests
import sys

from cmd import Cmd
from time import sleep

PIECE_NAME = {
    3: 'bishop',
    5: 'king',
    7: 'knight',
    9: 'pawn',
    11: 'queen',
    13: 'rook',
}
PROMPT = '> '
BRIGHT_GREEN = '\u001b[42;1m'
RESET = '\u001b[0m'
SELECTED_PIECE = f'{ BRIGHT_GREEN }{{}}{ RESET }'
TOP_BOARD_OUTPUT_SHELL = '''
  A B C D E F G H
 +---------------'''
BOARD_OUTPUT_SHELL = ('8|', '7|', '6|', '5|', '4|', '3|', '2|', '1|')


def get_info(api_url, game_id):
    response = requests.get(f'{ api_url }/v1.0/games/{ game_id }/info')
    return response.json()['print']


def format_board(board):
    return map(' '.join, board.splitlines())


def print_board(board):
    """
    Print board in shell.
    """
    print(TOP_BOARD_OUTPUT_SHELL)
    for shell, line in zip(
            BOARD_OUTPUT_SHELL, tuple(board)):
        print(f'{ shell }{ "".join(line) }')


class CLIAgent(Cmd):
    prompt = PROMPT

    def __init__(self, api_url):
        """
        Init player board.
        """
        super().__init__()
        self.api_url = api_url
        self.do_reset()

    def do_reset(self, *args):
        self.board = None
        self.future = None
        self.piece = None
        game = requests.post(f'{ self.api_url }/v1.0/games').json()
        game['user'] = 1
        self.game_id = game['id']
        self.user = requests.post(
            f'{ self.api_url }/issue-agent',
            json=game,
            headers={
                'content-type': 'application/json'
            },
        ).json()['agent_id']
        requests.post(
            f'{ self.api_url }/issue-agent-lookahead',
            json={'id': self.game_id, 'player': 2, 'lookahead': 4})
        print_board(format_board(get_info(self.api_url, self.game_id)))

    def do_piece(self, arg_str):
        """
        Select piece for move.
        """
        if self.future:
            if not self.future.started():
                print('not your turn yet')
                return
            try:
                self.future.result(0)
            except TimeoutError:
                print('not your turn yet')
                return
            self.future = None
        args = self.parse(arg_str)
        if len(args) != 2:
            return self.print_invalid('piece ' + arg_str)
        self.piece = args
        response = requests.get(f'{ self.api_url }/v1.0/games/{ self.game_id }')
        state = response.json()['state']
        if state == {'end': True}:
            return print('game over')
        board = tuple(map(bytes.fromhex, state))
        try:
            piece = board[args[1]][args[0]]
        except IndexError:
            return self.print_invalid('piece ' + arg_str)
        if not (piece and (piece & 1)):
            return self.print_invalid('piece ' + arg_str)
        board = list(map(list, get_info(self.api_url, self.game_id).splitlines()))
        board[args[1]][args[0]] = SELECTED_PIECE.format(
            board[args[1]][args[0]])
        print_board(map(' '.join, board))
        print(f'Selected: { PIECE_NAME[piece & 0xf] }')

    def do_move(self, arg_str):
        """
        Make move.
        """
        if not self.piece:
            return self.print_invalid('move ' + arg_str)

        args = self.parse(arg_str)
        if len(args) != 2:
            return self.print_invalid('move ' + arg_str)

        move = {'move': (tuple(reversed(self.piece)), tuple(reversed(args)))}
        self.piece = None

        response = requests.put(
            f'{ self.api_url }/agent/{ self.user }',
            json=move,
            headers={
                'content-type': 'application/json',
            }
        )
        if response.status_code != 200:
            print_board(format_board(get_info(self.api_url, self.game_id)))
            return print('Invalid move.')
        if response.json().get('state', {}).get('end', False):
            print_board(format_board(get_info(self.api_url, self.game_id)))
            return print('you won')
        response = requests.get(f'{ self.api_url }/v1.0/games/{ self.game_id }')
        in_board = response.json()['state']
        print_board(format_board(get_info(self.api_url, self.game_id)))
        if in_board == {'end': True}:
            return print('you won')
        print('making move ...')
        board = in_board
        while in_board == board:
            sleep(2)
            response = requests.get(f'{ self.api_url }/v1.0/games/{ self.game_id }')
            state = response.json()['state']
            if state == {'end': True}:
                return print('game over')
            board = state
        print_board(format_board(get_info(self.api_url, self.game_id)))

    def print_invalid(self, args):
        print_board(format_board(get_info(self.api_url, self.game_id)))
        print('invalid command:', args)

    @staticmethod
    def parse(args):
        """
        Split arguments.
        """
        args = args.split()
        if len(args) != 2:
            return args
        try:
            args[1] = 8 - int(args[1])
            if not (0 <= args[1] < 8):
                print('out of range')
                raise ValueError
        except ValueError:
            print('not int', args[1])
            return ()
        try:
            args[0] = ord(args[0]) - ord('a')
            if not (0 <= args[1] < 8):
                print('out of range')
                raise ValueError
        except ValueError:
            print('not char', args[0])
            return ()
        return args

    def emptyline(self):
        """
        Do nothing on empty command.
        """

    def precmd(self, line):
        """
        Sanitize data.
        """
        return line.strip().lower()


def main(argv=sys.argv):
    try:
        port = 8080
        api_url = f'http://localhost:{ port }'
        if len(argv) > 1:
            api_url = argv[1]
        CLIAgent(api_url).cmdloop()
    except KeyboardInterrupt:
        print()
