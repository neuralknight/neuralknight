# from collections import deque
# # from itertools import starmap
# from pytest import raises
#
# from ..models.board_constants import KING, QUEEN
#
#
# # def test_board_creation_valid(start_board):
# #     assert start_board
# #     assert start_board.board == tuple(map(bytes, (
# #         (12, 6, 2, 10, 4, 2, 6, 12),
# #         (8, 8, 8, 8, 8, 8, 8, 8),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (9, 9, 9, 9, 9, 9, 9, 9),
# #         (13, 7, 3, 11, 5, 3, 7, 13))))
#
#
# def test_pieces_on_board(start_board):
#     assert KING in start_board
#     assert QUEEN in start_board
#     assert KING | 1 in start_board
#     assert QUEEN | 1 in start_board
#
#
# def test_first_move_available(start_board):
#     assert next(start_board.lookahead_boards(1))
#
#
# def test_iterates_future_boards(start_board):
#     assert isinstance(next(iter(start_board))[0], tuple)
#
#
# def test_string_represention(start_board):
#     assert str(start_board) == '''\
# ♜♞♝♛♚♝♞♜
# ♟♟♟♟♟♟♟♟
# ▪▫▪▫▪▫▪▫
# ▫▪▫▪▫▪▫▪
# ▪▫▪▫▪▫▪▫
# ▫▪▫▪▫▪▫▪
# ♙♙♙♙♙♙♙♙
# ♖♘♗♕♔♗♘♖\
# '''
#
#
# def test_string_represention_swap(start_board):
#     start = str(start_board)
#     start_board._board = start_board._board.swap()
#     assert str(start_board) == start
#
#
# def test_string_represention_end(end_game_board):
#     assert str(end_game_board) == '''\
# ▪▫▪▫▪▫▪▫
# ▫▪▫▪▫▪▫▪
# ▪▫▪▫▪▫▪▫
# ▫▪▫♚▫▪▫▪
# ▪▫▪▫▪▫♕▫
# ▫▪▫♔▫▪▫▪
# ▪▫▪▫▪▫▪▫
# ▫▪▫▪▫▪▫▪\
# '''
#
#
# def test_lookahead_length(start_board):
#     assert set(map(len, start_board.lookahead_boards(1))) == {1}
#     assert set(map(len, start_board.lookahead_boards(3))) == {3}
#     assert set(map(len, start_board.prune_lookahead_boards(4))) == {2}
#
#
# def test_more_than_one_next_move(start_board):
#     it = start_board.lookahead_boards(1)
#     assert next(it)
#     assert next(it)
#
#
# def test_moves_consumption_lookahead_1(start_board):
#     it = start_board.lookahead_boards(1)
#     deque(it, maxlen=0)
#     with raises(StopIteration):
#         next(it)
#
#
# def test_moves_consumption_lookahead_2(start_board):
#     it = start_board.lookahead_boards(2)
#     deque(it, maxlen=0)
#     with raises(StopIteration):
#         next(it)
#
#
# # def test_moves_to_end(start_board):
# #     def test(*args):
# #         assert all(isinstance(board, type(start_board)) for board in args)
# #         return None if args[-1] else args
# #     win = next(filter(None, starmap(test, start_board.lookahead_boards(5))))
# #     assert not win[-1]
#
#
# # def test_moves_pawn_init_board(pawn_capture_board):
# #     for state, _ in pawn_capture_board.lookahead_boards(2):
# #         assert pawn_capture_board.update(state)
#
#
# # def test_moves_pawn_final_board(min_pawn_board):
# #     for state, _, _ in min_pawn_board.lookahead_boards(3):
# #         assert min_pawn_board.update(state)
#
#
# def test_board_mutations_are_valid(start_board):
#     mutated_board = next(start_board.lookahead_boards(1))[0]
#     assert -1 not in mutated_board
#
#
# # def test_invalid_board_move_two(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 6, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (9, 9, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 9, 9, 9, 9, 9, 9),
# #             (13, 7, 3, 11, 5, 3, 7, 13)))))
#
#
# # def test_invalid_board_move_extra_pieces(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 6, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (9, 9, 0, 0, 0, 0, 0, 0),
# #             (0, 9, 9, 9, 9, 9, 9, 9),
# #             (13, 7, 3, 11, 5, 3, 7, 13)))))
#
#
# # def test_invalid_board_duplicate_pieces(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 6, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (7, 0, 0, 0, 0, 0, 0, 0),
# #             (9, 9, 9, 9, 9, 9, 9, 9),
# #             (13, 7, 3, 11, 5, 3, 7, 13)))))
#
#
# # def test_invalid_board_move_invalid(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 6, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 7, 0, 0, 0, 0, 0, 0),
# #             (9, 9, 9, 9, 9, 9, 9, 9),
# #             (13, 0, 3, 11, 5, 3, 7, 13)))))
#
#
# # def test_invalid_board_move_inactive_piece(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 0, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 6, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (9, 9, 9, 9, 9, 9, 9, 9),
# #             (13, 7, 3, 11, 5, 3, 7, 13)))))
#
#
# # def test_invalid_board_move_capture_own(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 6, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (9, 9, 9, 3, 9, 9, 9, 9),
# #             (13, 7, 0, 11, 5, 3, 7, 13)))))
#
#
# # def test_invalid_board_move_blocked(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 6, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 0, 0, 0, 0, 0, 3),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (9, 9, 9, 9, 9, 9, 9, 9),
# #             (13, 7, 0, 11, 5, 3, 7, 13)))))
#
#
# # def test_invalid_board_move_modifies_piece(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 6, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 0, 0, 0, 0, 0, 11),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (9, 9, 9, 9, 9, 9, 9, 9),
# #             (13, 7, 0, 11, 5, 3, 7, 13)))))
#
#
# # def test_invalid_board_move_piece_swap(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 6, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (7, 9, 9, 9, 9, 9, 9, 9),
# #             (13, 9, 3, 11, 5, 3, 7, 13)))))
#
#
# # def test_invalid_board_move_no_change(start_board):
# #     with raises(RuntimeError):
# #         start_board.update(tuple(map(bytes, (
# #             (12, 6, 2, 10, 4, 2, 6, 12),
# #             (8, 8, 8, 8, 8, 8, 8, 8),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (0, 0, 0, 0, 0, 0, 0, 0),
# #             (9, 9, 9, 9, 9, 9, 9, 9),
# #             (13, 7, 3, 11, 5, 3, 7, 13)))))
#
#
# # def test_valid_board_move_backwards(end_game_board):
# #     assert end_game_board.update(tuple(map(bytes, (
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 4, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 5, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 11, 0)))))
#
#
# # def test_board_provides_update(start_board):
# #     mutated_board = next(iter(start_board))[0]
# #     assert start_board.update(mutated_board).board == tuple(map(bytes, (
# #         (12, 6, 2, 4, 10, 2, 6, 12),
# #         (8, 8, 8, 8, 8, 8, 8, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 8),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (0, 0, 0, 0, 0, 0, 0, 0),
# #         (9, 9, 9, 9, 9, 9, 9, 9),
# #         (13, 7, 3, 5, 11, 3, 7, 13))))
#
#
# def test_board_lookahead_player_is_constant(start_board):
#     states = next(start_board.lookahead_boards(3))
#     assert states[0] == tuple(map(bytes, (
#         (12, 6, 2, 10, 4, 2, 6, 12),
#         (8, 8, 8, 8, 8, 8, 8, 8),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (9, 0, 0, 0, 0, 0, 0, 0),
#         (0, 9, 9, 9, 9, 9, 9, 9),
#         (13, 7, 3, 11, 5, 3, 7, 13))))
#     assert states[1] == tuple(map(bytes, (
#         (12, 6, 2, 10, 4, 2, 6, 12),
#         (8, 8, 8, 8, 8, 8, 8, 0),
#         (0, 0, 0, 0, 0, 0, 0, 8),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (9, 0, 0, 0, 0, 0, 0, 0),
#         (0, 9, 9, 9, 9, 9, 9, 9),
#         (13, 7, 3, 11, 5, 3, 7, 13))))
#     assert states[2] == tuple(map(bytes, (
#         (12, 6, 2, 10, 4, 2, 6, 12),
#         (8, 8, 8, 8, 8, 8, 8, 0),
#         (0, 0, 0, 0, 0, 0, 0, 8),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (9, 0, 0, 0, 0, 0, 0, 0),
#         (0, 0, 0, 0, 0, 0, 0, 0),
#         (0, 9, 9, 9, 9, 9, 9, 9),
#         (13, 7, 3, 11, 5, 3, 7, 13))))
