import requests
import sys

from cmd import Cmd
from multiprocessing import Process
from time import sleep

from ..models.board_model import BoardModel

PORT = 8080
API_URL = f'http://localhost:{ PORT }'

PIECE_NAME = {
    3: 'bishop',
    5: 'king',
    7: 'knight',
    9: 'pawn',
    11: 'queen',
    13: 'rook',
}
BRIGHT_GREEN = '\u001b[42;1m'
RESET = '\u001b[0m'
SELECTED_PIECE = f'{ BRIGHT_GREEN }{{}}{ RESET }'
TOP_BOARD_OUTPUT_SHELL = '''
  A B C D E F G H
 +---------------'''
BOARD_OUTPUT_SHELL = ('1|', '2|', '3|', '4|', '5|', '6|', '7|', '8|')

BOARD = BoardModel()


def format_board(board):
    return map(' '.join, str(board).splitlines())


def print_board(board):
    """
    Print board in shell.
    """
    print(TOP_BOARD_OUTPUT_SHELL)
    for shell, line in zip(
            BOARD_OUTPUT_SHELL, tuple(board)):
        print(f'{ shell }{ "".join(line) }')


def update_board(user, in_board):
    board = in_board
    while in_board.board == board.board:
        sleep(60)
        response = requests.get(f'{ API_URL }/agent/{ user }')
        board = BoardModel(response.json()['state'])
    return board


def poll_move_response(user):
    global BOARD
    BOARD = update_board(user, BOARD)
    print_board(format_board(BOARD))


class CLIAgent(Cmd):
    prompt = '> '

    def __init__(self):
        """
        Init player board.
        """
        self.future = None
        self.piece = None
        game = requests.post(f'{ API_URL }/v1.0/games').json()
        game['user'] = 1
        self.user = requests.post(f'{ API_URL }/issue-agent', json=game).json()['agent_id']
        super().__init__()

    def do_piece(self, arg_str):
        """
        Select piece for move.
        """
        global BOARD
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
        try:
            piece = BOARD.board[args[1]][args[0]]
        except IndexError:
            return self.print_invalid('piece ' + arg_str)
        if not (piece and (piece & 1)):
            return self.print_invalid('piece ' + arg_str)
        board = [list(row) for row in str(BOARD).splitlines()]
        board[args[1]][args[0]] = SELECTED_PIECE.format(
            board[args[1]][args[0]])
        print_board(map(' '.join, board))
        print(f'Selected: { PIECE_NAME[piece] }')

    def do_move(self, arg_str):
        """
        Make move.
        """
        global BOARD
        if not self.piece:
            return self.print_invalid('move ' + arg_str)

        args = self.parse(arg_str)
        if len(args) != 2:
            return self.print_invalid('move ' + arg_str)

        move = {'move': (tuple(reversed(self.piece)), tuple(reversed(args)))}
        self.piece = None

        requests.put(f'{ API_URL }/agent/{ self.user }', json=move)
        sleep(1)
        BOARD = update_board(self.user, BOARD)
        print_board(format_board(BOARD.swap()))
        self.process = Process(target=poll_move_response, args=(self.user,))
        self.process.start()

    def print_invalid(self, args):
        print_board(format_board(BOARD))
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
            args[1] = int(args[1]) - 1
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

    def play_round(self, *args):
        """
        User round play.
        """
        assert args
        move = (1, 1)
        return {[move]}


def main(argv=sys.argv):
    global API_URL
    try:
        if len(argv) > 1:
            API_URL = argv[1]
        print_board(format_board(BOARD))
        CLIAgent().cmdloop()
    except KeyboardInterrupt:
        print()
