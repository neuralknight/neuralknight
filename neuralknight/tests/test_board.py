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
    assert len(next(start_board.lookahead_boards(1))) == 1
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


def test_board_mutations_are_valid(start_board):
    mutated_board = next(start_board.lookahead_boards(1))[0]
    assert -1 not in mutated_board


def test_board_lookahead_player_is_constant(start_board):
    states = next(start_board.lookahead_boards(3))
    assert states[0].board == [
        [12, 6, 2, 10, 4, 2, 6, 12],
        [8, 8, 8, 8, 8, 8, 8, 8],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [9, 0, 0, 0, 0, 0, 0, 0],
        [0, 9, 9, 9, 9, 9, 9, 9],
        [13, 7, 3, 11, 5, 3, 7, 13]]
    assert states[1].board == [
        [12, 0, 2, 10, 4, 2, 6, 12],
        [8, 8, 8, 8, 8, 8, 8, 8],
        [6, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [9, 0, 0, 0, 0, 0, 0, 0],
        [0, 9, 9, 9, 9, 9, 9, 9],
        [13, 7, 3, 11, 5, 3, 7, 13]]
    assert states[2].board == [
        [12, 0, 2, 10, 4, 2, 6, 12],
        [8, 8, 8, 8, 8, 8, 8, 8],
        [6, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [9, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 9, 9, 9, 9, 9, 9, 9],
        [13, 7, 3, 11, 5, 3, 7, 13]]
