from .board import Board
from pytest import fixture


@fixture
def start_board():
    return Board()
