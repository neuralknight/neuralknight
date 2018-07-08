import cProfile

from ..models.board import Board


def main():
    cProfile.runctx(
        'assert set(map(len, Board().lookahead_boards(4))) == {4}',
        globals(), {'Board': Board})
