from cmd import Cmd

from ..models import Board

PIECE_NAME = {
    3: 'bishop',
    5: 'king',
    7: 'knight',
    9: 'pawn',
    11: 'queen',
    13: 'rook',
}
BRIGHT_GREEN = '\u001b[32;1m'
RESET = '\u001b[0m'
SELECTED_PIECE = f'{ BRIGHT_GREEN }{{}}{ RESET }'
BOARD_OUTPUT_SHELL = '''
  A B C D E F G H
 +---------------
1|
2|
3|
4|
5|
6|
7|
8|
'''


class MockAgent(Cmd):
    intro = '''
'''
    prompt = '> '

    def __init__(self):
        """
        Init player board.
        """
        self.board = Board()
        super().__init__()

    def do_piece(self, args):
        """
        Select piece for move.
        """
        args = self.parse(args)
        if len(args) == 2:
            try:
                piece = self.board.board[args[1]][args[0]]
            except IndexError:
                return
            if not (piece and (piece & 1)):
                return
            board = [list(row) for row in str(self.board).splitlines()]
            board[args[1]][args[0]] = SELECTED_PIECE.format(
                board[args[1]][args[0]])
            self.print_board(map(''.join, board))
            print(f'Selected: { PIECE_NAME[piece] }')

    def do_move(self, args):
        """
        Make move.
        """
        args = self.parse(args)
        if len(args) == 2:
            self.print_board(str(self.board).splitlines())

    @staticmethod
    def print_board(board):
        """
        Print board in shell.
        """
        for shell, line in zip(
                BOARD_OUTPUT_SHELL,
                ('', '') + tuple(board)):
            print(f'{ shell }{ " ".join(line) }')

    @staticmethod
    def parse(args):
        """
        Split arguments.
        """
        return tuple(map(int, args.split()[1:]))

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
    MockAgent().cmdloop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
