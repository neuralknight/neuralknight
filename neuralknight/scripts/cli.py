from cmd import Cmd
import requests

from ..models.board_model import BoardModel

PORT = 8080
API_URL = 'http://localhost:{}'.format(PORT)

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


class CLIAgent(Cmd):
    intro = '''
'''
    prompt = '> '

    def __init__(self):
        """
        Init player board.
        """
        self.board = BoardModel()
        self.piece = None
        self.user = None
        game = requests.post(API_URL + '/v1.0/games').json()
        self.user = requests.post(API_URL + '/issue-agent', json=game).json()
        self.user['user'] = 1
        super().__init__()

    def do_piece(self, arg_str):
        """
        Select piece for move.
        """
        args = self.parse(arg_str)
        if len(args) != 2:
            return self.print_invalid('piece ' + arg_str)
        self.piece = args
        try:
            piece = self.board.board[args[1]][args[0]]
        except IndexError:
            return self.print_invalid('piece ' + arg_str)
        if not (piece and (piece & 1)):
            return self.print_invalid('piece ' + arg_str)
        board = [list(row) for row in str(self.board).splitlines()]
        board[args[1]][args[0]] = SELECTED_PIECE.format(
            board[args[1]][args[0]])
        self.print_board(map(' '.join, board))
        print(f'Selected: { PIECE_NAME[piece] }')

    def do_move(self, arg_str):
        """
        Make move.
        """
        args = self.parse(arg_str)
        if len(args) != 2:
            return self.print_invalid('move ' + arg_str)

        move = (tuple(reversed(self.piece)), tuple(reversed(args)))

        requests.put(API_URL + f"/agent/{self.user['agent_id']}", json=move)

        board = [list(row) for row in str(self.board).splitlines()]
        self.print_board(map(' '.join, board))

    def print_invalid(self, args):
        self.print_board(' '.join(row) for row in str(self.board).splitlines())
        print('invalid command:', args)

    @staticmethod
    def print_board(board):
        """
        Print board in shell.
        """
        print(TOP_BOARD_OUTPUT_SHELL)
        for shell, line in zip(
                BOARD_OUTPUT_SHELL, tuple(board)):
            print(f'{ shell }{ "".join(line) }')

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


def main():
    try:
        CLIAgent().cmdloop()
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
