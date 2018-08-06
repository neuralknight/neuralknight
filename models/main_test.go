package models_test

import (
	"math"
	"testing"

	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"github.com/leanovate/gopter"
	"github.com/leanovate/gopter/gen"
	"github.com/leanovate/gopter/prop"
	. "gopkg.in/check.v1"
)

func Test(t *testing.T) { TestingT(t) }

type BoardSuite struct{}

var _ = Suite(&BoardSuite{})

func TestBoard(t *testing.T) {
	properties := gopter.NewProperties(nil)

	properties.Property("greater one of all greater one", prop.ForAll(
		func(v float64) bool {
			return math.Sqrt(v) >= 1
		},
		gen.Float64Range(1, math.MaxFloat64),
	))

	properties.Property("squared is equal to value", prop.ForAll(
		func(v float64) bool {
			r := math.Sqrt(v)
			return math.Abs(r*r-v) < 1e-10*v
		},
		gen.Float64Range(0, math.MaxFloat64),
	))

	properties.TestingRun(t)
}

// from collections import deque
// from itertools import starmap
// from pytest import raises
//
// from ..models.board_constants import KING, QUEEN
//
//
// def test_board_creation_valid(start_board):
//     assert start_board
//     assert start_board.board == tuple(map(bytes, (
//         (12, 6, 2, 10, 4, 2, 6, 12),
//         (8, 8, 8, 8, 8, 8, 8, 8),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (9, 9, 9, 9, 9, 9, 9, 9),
//         (13, 7, 3, 11, 5, 3, 7, 13))))
//
//
// def test_pieces_on_board(start_board):
//     assert KING in start_board
//     assert QUEEN in start_board
//     assert KING | 1 in start_board
//     assert QUEEN | 1 in start_board
//
//
// def test_first_move_available(start_board):
//     assert next(start_board.lookahead_boards(1))
//
//
// def test_iterates_future_boards(start_board):
//     assert isinstance(next(iter(start_board))[0], tuple)
//
//
// def test_string_represention(start_board):
//     assert str(start_board) == """\
// ♜♞♝♛♚♝♞♜
// ♟♟♟♟♟♟♟♟
// ▪▫▪▫▪▫▪▫
// ▫▪▫▪▫▪▫▪
// ▪▫▪▫▪▫▪▫
// ▫▪▫▪▫▪▫▪
// ♙♙♙♙♙♙♙♙
// ♖♘♗♕♔♗♘♖\
// """
//
//
// def test_string_represention_swap(start_board):
//     start = str(start_board)
//     start_board._board = start_board._board.swap()
//     assert str(start_board) == start
//
//
// def test_string_represention_end(end_game_board):
//     assert str(end_game_board) == """\
// ▪▫▪▫▪▫▪▫
// ▫▪▫▪▫▪▫▪
// ▪▫▪▫▪▫▪▫
// ▫▪▫♚▫▪▫▪
// ▪▫▪▫▪▫♕▫
// ▫▪▫♔▫▪▫▪
// ▪▫▪▫▪▫▪▫
// ▫▪▫▪▫▪▫▪\
// """
//
//
// def test_lookahead_length(start_board):
//     assert set(map(len, start_board.lookahead_boards(1))) == {1}
//     assert set(map(len, start_board.lookahead_boards(3))) == {3}
//     assert set(map(len, start_board.prune_lookahead_boards(4))) == {2}
//
//
// def test_more_than_one_next_move(start_board):
//     it = start_board.lookahead_boards(1)
//     assert next(it)
//     assert next(it)
//
//
// def test_moves_consumption_lookahead_1(start_board):
//     it = start_board.lookahead_boards(1)
//     deque(it, maxlen=0)
//     with raises(StopIteration):
//         next(it)
//
//
// def test_moves_consumption_lookahead_2(start_board):
//     it = start_board.lookahead_boards(2)
//     deque(it, maxlen=0)
//     with raises(StopIteration):
//         next(it)
//
//
// def test_moves_to_end(start_board):
//     def test(*args):
//         assert all(isinstance(board, type(start_board)) for board in args)
//         return None if args[-1] else args
//     win = next(filter(None, starmap(test, start_board.lookahead_boards(5))))
//     assert not win[-1]
//
//
// def test_moves_pawn_init_board(pawn_capture_board):
//     for state, _ in pawn_capture_board.lookahead_boards(2):
//         assert pawn_capture_board.update(state)
//
//
// def test_moves_pawn_final_board(min_pawn_board):
//     for state, _, _ in min_pawn_board.lookahead_boards(3):
//         assert min_pawn_board.update(state)
//
//
// def test_board_mutations_are_valid(start_board):
//     mutated_board = next(start_board.lookahead_boards(1))[0]
//     assert -1 not in mutated_board
//
//
// def test_invalid_board_move_two(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 6, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (9, 9, 0, 0, 0, 0, 0, 0),
//             (0, 0, 9, 9, 9, 9, 9, 9),
//             (13, 7, 3, 11, 5, 3, 7, 13)))))
//
//
// def test_invalid_board_move_extra_pieces(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 6, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (9, 9, 0, 0, 0, 0, 0, 0),
//             (0, 9, 9, 9, 9, 9, 9, 9),
//             (13, 7, 3, 11, 5, 3, 7, 13)))))
//
//
// def test_invalid_board_duplicate_pieces(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 6, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (7, 0, 0, 0, 0, 0, 0, 0),
//             (9, 9, 9, 9, 9, 9, 9, 9),
//             (13, 7, 3, 11, 5, 3, 7, 13)))))
//
//
// def test_invalid_board_move_invalid(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 6, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 7, 0, 0, 0, 0, 0, 0),
//             (9, 9, 9, 9, 9, 9, 9, 9),
//             (13, 0, 3, 11, 5, 3, 7, 13)))))
//
//
// def test_invalid_board_move_inactive_piece(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 0, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 6, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (9, 9, 9, 9, 9, 9, 9, 9),
//             (13, 7, 3, 11, 5, 3, 7, 13)))))
//
//
// def test_invalid_board_move_capture_own(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 6, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (9, 9, 9, 3, 9, 9, 9, 9),
//             (13, 7, 0, 11, 5, 3, 7, 13)))))
//
//
// def test_invalid_board_move_blocked(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 6, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 0, 0, 0, 0, 0, 3),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (9, 9, 9, 9, 9, 9, 9, 9),
//             (13, 7, 0, 11, 5, 3, 7, 13)))))
//
//
// def test_invalid_board_move_modifies_piece(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 6, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 0, 0, 0, 0, 0, 11),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (9, 9, 9, 9, 9, 9, 9, 9),
//             (13, 7, 0, 11, 5, 3, 7, 13)))))
//
//
// def test_invalid_board_move_piece_swap(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 6, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (7, 9, 9, 9, 9, 9, 9, 9),
//             (13, 9, 3, 11, 5, 3, 7, 13)))))
//
//
// def test_invalid_board_move_no_change(start_board):
//     with raises(RuntimeError):
//         start_board.update(tuple(map(bytes, (
//             (12, 6, 2, 10, 4, 2, 6, 12),
//             (8, 8, 8, 8, 8, 8, 8, 8),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (0, 0, 0, 0, 0, 0, 0, 0),
//             (9, 9, 9, 9, 9, 9, 9, 9),
//             (13, 7, 3, 11, 5, 3, 7, 13)))))
//
//
// def test_valid_board_move_backwards(end_game_board):
//     assert end_game_board.update(tuple(map(bytes, (
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 4, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 5, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 11, 0)))))
//
//
// def test_board_provides_update(start_board):
//     mutated_board = next(iter(start_board))[0]
//     assert start_board.update(mutated_board).board == tuple(map(bytes, (
//         (12, 6, 2, 4, 10, 2, 6, 12),
//         (8, 8, 8, 8, 8, 8, 8, 0),
//         (0, 0, 0, 0, 0, 0, 0, 8),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (9, 9, 9, 9, 9, 9, 9, 9),
//         (13, 7, 3, 5, 11, 3, 7, 13))))
//
//
// def test_board_lookahead_player_is_constant(start_board):
//     states = next(start_board.lookahead_boards(3))
//     assert states[0] == tuple(map(bytes, (
//         (12, 6, 2, 10, 4, 2, 6, 12),
//         (8, 8, 8, 8, 8, 8, 8, 8),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (9, 0, 0, 0, 0, 0, 0, 0),
//         (0, 9, 9, 9, 9, 9, 9, 9),
//         (13, 7, 3, 11, 5, 3, 7, 13))))
//     assert states[1] == tuple(map(bytes, (
//         (12, 6, 2, 10, 4, 2, 6, 12),
//         (8, 8, 8, 8, 8, 8, 8, 0),
//         (0, 0, 0, 0, 0, 0, 0, 8),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (9, 0, 0, 0, 0, 0, 0, 0),
//         (0, 9, 9, 9, 9, 9, 9, 9),
//         (13, 7, 3, 11, 5, 3, 7, 13))))
//     assert states[2] == tuple(map(bytes, (
//         (12, 6, 2, 10, 4, 2, 6, 12),
//         (8, 8, 8, 8, 8, 8, 8, 0),
//         (0, 0, 0, 0, 0, 0, 0, 8),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (9, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 9, 9, 9, 9, 9, 9, 9),
//         (13, 7, 3, 11, 5, 3, 7, 13))))
// from os import environ
// from pyramid.testing import DummyRequest, setUp, tearDown
// from pytest import fixture
//
// from ..models.board import Board
// from ..models.meta import Base
//
//
// @fixture
// def configuration(request):
//     """
//     Create database models for testing purposes.
//     """
//     config = setUp(settings={
//         "sqlalchemy.url": environ.get(
//             "TEST_DATABASE_URL", "postgres://localhost:5432/testing_neuralknight")
//     })
//     config.include("neuralknight.models")
//     config.include("neuralknight.routes")
//     yield config
//     tearDown()
//
//
// @fixture
// def db_session(configuration, request):
//     """
//     Create a database session for interacting with the test database.
//     """
//     SessionFactory = configuration.registry["dbsession_factory"]
//     session = SessionFactory()
//     engine = session.bind
//     Base.metadata.create_all(engine)
//     yield session
//     session.transaction.rollback()
//     Base.metadata.drop_all(engine)
//
//
// @fixture
// def dummy_request(db_session):
//     """
//     Create a dummy GET request with a dbsession.
//     """
//     return DummyRequest(dbsession=db_session)
//
//
// @fixture
// def dummy_post_request(db_session):
//     """
//     Create a dummy POST request with a dbsession.
//     """
//     return DummyRequest(dbsession=db_session, post={}, json={})
//
//
// @fixture(scope="session")
// def testapp(request):
//     """
//     Functional test for app to support mocking.
//     """
//     import neuralknight
//     from webtest import TestApp
//
//     app = neuralknight.main({}, **{
//         "sqlalchemy.url": environ.get(
//             "TEST_DATABASE_URL", "postgres://localhost:5432/testing_neuralknight")
//     })
//
//     SessionFactory = app.registry["dbsession_factory"]
//     engine = SessionFactory().bind
//     Base.metadata.create_all(bind=engine)
//     neuralknight.testapp = TestApp(app)
//     yield neuralknight.testapp
//     Base.metadata.drop_all(bind=engine)
//
//
// @fixture
// def start_board():
//     return Board()
//
//
// @fixture
// def pawn_capture_board():
//     return Board(tuple(map(bytes, [
//         [12, 6, 2, 10, 4, 2, 6, 12],
//         [8, 8, 8, 0, 8, 0, 8, 8],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 8, 0, 8, 0, 0],
//         [0, 0, 0, 0, 9, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [9, 9, 9, 9, 0, 9, 9, 9],
//         [13, 7, 3, 11, 5, 3, 7, 13]])))
//
//
// @fixture
// def min_pawn_board():
//     return Board(tuple(map(bytes, [
//         [0, 0, 0, 0, 4, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 0, 9, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 0, 5, 0, 0, 0]])))
//
//
// @fixture
// def end_game_board():
//     return Board(tuple(map(bytes, [
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 4, 0, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 11, 0],
//         [0, 0, 0, 5, 0, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0],
//         [0, 0, 0, 0, 0, 0, 0, 0]])))

// from ..models import BaseBoard, BaseAgent
//
//
// class MockBoard(BaseBoard):
//     def __init__(self, testapp, cursor=None):
//         self.testapp = testapp
//         self.args = {}
//         self.kwargs = {}
//         self.cursor = cursor
//         super().__init__([[0 for i in range(8)] for j in range(8)])
//
//     def slice_cursor_v1(self, *args, **kwargs):
//         self.args["slice_cursor_v1"] = args
//         self.kwargs["slice_cursor_v1"] = kwargs
//         return {
//             "cursor": self.cursor,
//             "boards": [(self.board,)]
//         }
//
//     def add_player_v1(self, *args, **kwargs):
//         self.args["add_player_v1"] = args
//         self.kwargs["add_player_v1"] = kwargs
//         player = args[1]
//         if self.player1:
//             self.player2 = player
//         else:
//             self.player1 = player
//         self.poke_player(False)
//         return {}
//
//     def update_state_v1(self, *args, **kwargs):
//         self.args["update_state_v1"] = args
//         self.kwargs["update_state_v1"] = kwargs
//         return {"end": True}
//
//
// def test_player_connection(testapp):
//     """Assert players connect to board"""
//     mockboard = MockBoard(testapp)
//     player1 = testapp.post_json("/issue-agent", {"id": mockboard.id}).json
//     player2 = testapp.post_json("/issue-agent", {"id": mockboard.id, "player": 2}).json
//     assert player1
//     assert player2
//
//
// this needs to change - need to check multi-gets
// def test_get_boards(testapp):
//     mockboard = MockBoard(testapp, 1)
//     player1 = testapp.post_json("/issue-agent", {"id": mockboard.id}).json
//     assert player1["AgentID"] in BaseAgent.AGENT_POOL
//     player2 = testapp.post_json("/issue-agent", {"id": mockboard.id, "player": 2}).json
//     assert player2
//     assert player1["AgentID"] not in BaseAgent.AGENT_POOL
//
//
// def test_choose_valid_move(testapp):
//     """Assert agent chooses valid move and game ends"""
//     mockboard = MockBoard(testapp)
//     state = mockboard.current_state_v1()
//     player1 = testapp.post_json("/issue-agent", {"id": mockboard.id}).json
//      assert player1["AgentID"] in BaseAgent.AGENT_POOL
//     player2 = testapp.post_json("/issue-agent", {"id": mockboard.id, "player": 2}).json
//     assert state == mockboard.current_state_v1()
//     assert player2
//     assert player1["AgentID"] not in BaseAgent.AGENT_POOL
//
//
// def test_play_game(testapp):
//     mockboard = MockBoard(testapp)
//     player1 = testapp.post_json("/issue-agent", {"id": mockboard.id}).json
//      assert player1["AgentID"] in BaseAgent.AGENT_POOL
//     player2 = testapp.post_json("/issue-agent", {"id": mockboard.id, "player": 2}).json
//     assert player2
//     assert player1["AgentID"] not in BaseAgent.AGENT_POOL
//
//
// def test_user_connection(testapp):
//     mockboard = MockBoard(testapp)
//     player1 = testapp.post_json("/issue-agent", {"id": mockboard.id, "user": True}).json
//     assert player1
// from ..models.base_agent import BaseAgent
//
//
// class MockAgent(BaseAgent):
//     def __init__(self, testapp, moves, game_id, player):
//         self.testapp = testapp
//         self.args = []
//         self.kwargs = []
//         self.moves = iter(moves)
//         self.past_end = False
//         super().__init__(game_id, player)
//
//     def play_round(self, *args, **kwargs):
//         self.args.append(args)
//         self.kwargs.append(kwargs)
//         try:
//             return self.put_board(next(self.moves))
//         except StopIteration:
//             self.past_end = True
//         return {}
//
//
// def test_home_endpoint(testapp):
//     response = testapp.get("/")
//     assert response.status_code == 200
//
//
// def test_games_endpoint(testapp):
//     response = testapp.get("/v1.0/games")
//     assert response.status_code == 200
//     assert "ids" in response.json
//
//
// def test_agent_play_no_moves(testapp):
//     game = testapp.post_json("/v1.0/games").json
//     player1 = MockAgent(testapp, [], game["id"], 1)
//     player2 = MockAgent(testapp, [], game["id"], 2)
//     assert player1.AgentID != player2.AgentID
//     assert player1.args.pop() == ()
//     assert player1.kwargs.pop() == {}
//     assert player1.past_end
//     assert not player2.args
//     assert not player2.kwargs
//     assert not player2.past_end
//
//
// def test_agent_play_through(testapp):
//     player1_moves = [tuple(map(bytes, (
//         (12, 6, 2, 10, 4, 2, 6, 12),
//         (8, 8, 8, 8, 8, 8, 8, 8),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 9, 0, 0, 0),
//         (9, 9, 9, 9, 0, 9, 9, 9),
//         (13, 7, 3, 11, 5, 3, 7, 13)))), tuple(map(bytes, (
//
//         (12, 6, 2, 10, 4, 2, 6, 12),
//         (8, 8, 8, 8, 8, 0, 8, 8),
//         (0, 0, 0, 0, 0, 8, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 11),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 9, 0, 0, 0),
//         (9, 9, 9, 9, 0, 9, 9, 9),
//         (13, 7, 3, 0, 5, 3, 7, 13))))]
//     player1_moves = [player1_moves[0]]
//     player2_moves = [tuple(map(bytes, (
//         (12, 6, 2, 4, 10, 2, 6, 12),
//         (8, 8, 8, 0, 8, 8, 8, 8),
//         (0, 0, 0, 8, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 9, 0, 0, 0, 0, 0),
//         (9, 9, 0, 9, 9, 9, 9, 9),
//         (13, 7, 3, 5, 11, 3, 7, 13)))), tuple(map(bytes, (
//
//         (12, 6, 2, 4, 0, 2, 6, 12),
//         (8, 8, 8, 0, 8, 8, 8, 8),
//         (0, 0, 0, 8, 0, 0, 0, 0),
//         (0, 0, 0, 0, 0, 0, 0, 0),
//         (10, 0, 0, 0, 0, 0, 0, 0),
//         (0, 0, 9, 0, 0, 0, 0, 0),
//         (9, 9, 0, 9, 9, 9, 9, 9),
//         (13, 7, 3, 5, 11, 3, 7, 13))))]
//     player2_moves = []
//     game = testapp.post_json("/v1.0/games").json
//     player1 = MockAgent(testapp, player1_moves, game["id"], 1)
//     player2 = MockAgent(testapp, player2_moves, game["id"], 2)
//     assert len(player1.args) == 1
//     assert len(player2.args) == 1
//     assert not player1.past_end
//     assert player2.past_end
