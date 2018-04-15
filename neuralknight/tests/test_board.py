from collections import deque
from pytest import raises

from neuralknight.models.board import KING, QUEEN


def test_board_creation_valid(start_board):
    assert start_board


def test_pieces_on_board(start_board):
    assert KING in start_board
    assert QUEEN in start_board
    assert KING | 1 in start_board
    assert QUEEN | 1 in start_board


def test_first_move_available(start_board):
    assert next(start_board.lookahead_boards(1))


def test_lookahead_length(start_board):
    assert len(next(start_board.lookahead_boards(5))) == 5


def test_more_than_one_next_move(start_board):
    it = start_board.lookahead_boards(1)
    assert next(it)
    assert next(it)


def test_moves_consumption_lookahead_1(start_board):
    it = start_board.lookahead_boards(1)
    deque(it, maxlen=0)
    with raises(StopIteration):
        next(it)


def test_moves_consumption_lookahead_2(start_board):
    it = start_board.lookahead_boards(2)
    deque(it, maxlen=0)
    with raises(StopIteration):
        next(it)
