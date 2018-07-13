package neuralknightmodels

import "math"

// """
// Chess state handling model.
// """
//
// from itertools import chain, count, groupby, islice, starmap
// from functools import partial, lru_cache
// from operator import itemgetter
// from uuid import uuid4
//
// from .board_constants import (
//     INITIAL_BOARD, BISHOP, KING, KNIGHT, QUEEN, ROOK, unit,
//     BISHOP_MOVES, KING_MOVES, KNIGHT_MOVES, QUEEN_MOVES, ROOK_MOVES)
//
// __all__ = ["BoardModel", "CursorDelegate", "InvalidMove"]
//
//

// InvalidMove error.
type InvalidMove struct{}

type cursorDelegate struct{}

// class CursorDelegate:
//     def __init__(self):
//         self.cursors = {}

// Retrieve iterable for cursor.
func (cursor cursorDelegate) getCursor() {
}

//     def get_cursor(self, board, cursor, lookahead, complete):
//         if cursor in self.cursors:
//             return self.cursors.pop(cursor)
//         if complete:
//             it = board.lookahead_boards(lookahead)
//         else:
//             it = board.prune_lookahead_boards(lookahead)
//         it = groupby(it, itemgetter(0))
//         try:
//             return next(it)[1], it
//         except StopIteration:
//             pass
//         return iter(()), iter(())

// Retrieve REST cursor slice.
func (cursor cursorDelegate) sliceCursorV1() {
}

//     def slice_cursor_v1(self, board, cursor, lookahead, complete):
//         it, cur = self.get_cursor(board, cursor, lookahead, complete)
//         slen = (900 // lookahead) if complete else 450
//         boards = tuple(islice(it, slen))
//         if len(boards) < slen:
//             try:
//                 it = next(cur)[1]
//             except StopIteration:
//                 return {"cursor": None, "boards": boards}
//         cursor = str(uuid4())
//         self.cursors[cursor] = (it, cur)
//         return {"cursor": cursor, "boards": boards}

// Validate a move against board bounds.
func isOnBoard(posX int8, posY int8, move [2]int8) bool {
	posX = posX + move[0]
	posY = posY + move[1]
	return 0 <= posX && posX < 8 && 0 <= posY && posY < 8
}

// Validate a move against ending location.
func validateEnding(board board, posX int8, posY int8, move [2]int8) bool {
	return !activePiece(board[posY+move[1]][posX+move[0]])
}

// Validate clear path along move.
func validateMove(board board, posX int8, posY int8, move [2]int8) bool {
	limit := int8(math.Max(math.Abs(float64(move[0])), math.Abs(float64(move[1]))))
	x := unit(move[0])
	y := unit(move[1])
	var i int8
	for i = 1; i < limit; i++ {
		if board[posY+y*i][posX+x*i] != 0 {
			return false
		}
	}
	return validateEnding(board, posX, posY, move)
}

func validateTrue(board, int8, int8, [2]int8) bool { return true }

// Get final validation function for piece.
func validationForPiece(piece uint8) func(board, int8, int8, [2]int8) bool {
	switch piece & 0xE / 2 {
	case 1, 5, 6:
		return validateMove
	case 2, 3:
		return validateEnding
	}
	return validateTrue
}

// def validation_for_piece(board, piece, posX, posY):
//     return partial((
//         validate_true,  # No piece
//         partial(validate_move, board),  # Bishop
//         partial(validate_ending, board),  # King
//         partial(validate_ending, board),  # Knight
//         validate_true,  # Pawn
//         partial(validate_move, board),  # Queen
//         partial(validate_move, board)  # Rook
//         )[(piece & 0xE) // 2], posX, posY)

// Get all possible moves for pawn.
func movesForPawn(board board, piece uint8, posX int8, posY int8) <-chan [2]int8 {
	out := make(chan [2]int8)
	go func() {
		if isOnBoard(posX, posY, [2]int8{0, -1}) && board[posY-1][posX] == 0 {
			out <- [2]int8{0, -1}
		}
		if posY == 6 && board[5][posX] == 0 && board[4][posX] == 0 {
			out <- [2]int8{0, -2}
		}
		if isOnBoard(posX, posY, [2]int8{-1, -1}) && inactivePiece(board[posY-1][posX-1]) {
			out <- [2]int8{-1, -1}
		}
		if isOnBoard(posX, posY, [2]int8{1, -1}) && inactivePiece(board[posY-1][posX+1]) {
			out <- [2]int8{1, -1}
		}
		if piece&0x10 != 0 {
		}
		close(out)
	}()
	return out
}

// Get castling.
func movesForKing(board board, piece uint8, posX int8, posY int8) <-chan [2]int8 {
	out := make(chan [2]int8)
	go func() {
		if piece&0x10 != 0 {
			leftPiece := board[posY][0]
			if leftPiece&0x10 != 0 && leftPiece&0x1 != 0 && leftPiece&0xE == ROOK {
				out <- [2]int8{-2}
				out <- [2]int8{-3}
			}
			rightPiece := board[posY][7]
			if rightPiece&0x10 != 0 && rightPiece&0x1 != 0 && rightPiece&0xE == ROOK {
				out <- [2]int8{2}
			}
		}
		close(out)
	}()
	return out
}

// Get all possible moves for piece type.
func movesForPiece(board board, piece uint8, posX int8, posY int8) <-chan [2]int8 {
	out := make(chan [2]int8)
	go func() {
		switch piece & 0xE / 2 {
		case 1:
			for _, m := range bishopMoves {
				out <- m
			}
		case 2:
			for _, m := range kingMoves {
				out <- m
			}
			for m := range movesForKing(board, piece, posX, posY) {
				out <- m
			}
		case 3:
			for _, m := range knightMoves {
				out <- m
			}
		case 4:
			for m := range movesForPawn(board, piece, posX, posY) {
				out <- m
			}
		case 5:
			for _, m := range queenMoves {
				out <- m
			}
		case 6:
			for _, m := range rookMoves {
				out <- m
			}
		}
		close(out)
	}()
	return out
}

// Get all valid moves for piece type.
func validMovesForPiece(board board, piece uint8, posX int8, posY int8) <-chan [2]int8 {
	out := make(chan [2]int8)
	go func() {
		filter := validationForPiece(piece)
		for m := range movesForPiece(board, piece, posX, posY) {
			if filter(board, posY, posX, m) {
				out <- m
			}
		}
		close(out)
	}()
	return out
}

// Get all future board states.
func lookaheadBoardsForPiece(b board, check bool, piece uint8, posX int8, posY int8) <-chan board {
	out := make(chan board)

	go func() {
		mutateBoard := func(move [2]int8) {
			newState := b
			newState[posY][posX] = 0
			if piece == 9 && posY == 1 {
				for _, promote := range [4]uint8{BISHOP, KNIGHT, QUEEN, ROOK} {
					newState[posY+move[1]][posX+move[0]] = promote | 1
					out <- swap(newState)
				}
			} else {
				newState[posY+move[1]][posX+move[0]] = piece & 0xF
				out <- swap(newState)
			}
		}

		validMovesForPiece := validMovesForPiece(b, piece, posX, posY)
		if check {
			for move := range validMovesForPiece {
				if b[posY+move[1]][posX+move[0]]&0xF == KING {
					mutateBoard(move)
				}
			}
		} else {
			for move := range validMovesForPiece {
				mutateBoard(move)
			}
		}
		close(out)
	}()
	return out
}

// Get possiblity of check in all future board states.
func lookaheadCheckForPiece(board board, piece uint8, posX int8, posY int8) bool {
	for move := range validMovesForPiece(board, piece, posX, posY) {
		if board[posY+move[1]][posX+move[0]]&0xF == KING {
			return true
		}
	}
	return false
}

// Get possiblity of check in all future board states.
func lookaheadCheck(board board) bool {
	for piece := range activePieces(board) {
		if lookaheadCheckForPiece(board, piece.piece, piece.posX, piece.posY) {
			return true
		}
	}
	return false
}

// Validate piece as active.
func activePiece(piece uint8) bool {
	return piece&1 != 0 && piece&0xE != 0
}

// Validate piece as inactive.
func inactivePiece(piece uint8) bool {
	return piece&1 == 0 && piece&0xE != 0
}

// Piece with position.
type Piece struct {
	piece uint8
	posX  int8
	posY  int8
}

// Get all pieces for current player.
func activePieces(board board) <-chan Piece {
	out := make(chan Piece)
	go func() {
		for posY, r := range board {
			for posX, piece := range r {
				if activePiece(piece) {
					out <- Piece{piece, int8(posX), int8(posY)}
				}
			}
		}
	}()
	return out
}

// Rotate active player.
func swap(b board) board {
	var out board
	for posY, r := range b {
		for posX, piece := range r {
			if piece != 0 {
				out[7-posY][7-posX] = piece ^ 1
			}
		}
	}
	return out
}

// Chess board model.
type boardModel struct {
	board
	moveCount      int
	movesSincePawn int
}

// Ensure active player king on board.
func (board boardModel) active() bool {
	return board.movesSincePawn < 50 || board.hasKings()
}

// Ensure piece on board.
func (board boardModel) contains(piece uint8) bool {
	for _, r := range board.board {
		for _, p := range r {
			if p == piece&0xF {
				return true
			}
		}
	}
	return false
}

// Rotate active player.
func (board boardModel) swap() board {
	return swap(board.board)
}

type mutation struct {
	posX      int8
	posY      int8
	prevPiece uint8
	nextPiece uint8
}

func (board boardModel) validateMutation(mutation []mutation, state board) board {
	if len(mutation) != 2 {
		panic(InvalidMove{})
	}
	old := mutation[0]
	new := mutation[1]
	if mutation[0].prevPiece == 0 {
	} else if mutation[1].prevPiece == 0 {
		temp := old
		old = new
		new = temp
	} else {
		panic(InvalidMove{})
	}
	new.nextPiece = new.nextPiece & 0xF
	if activePiece(new.prevPiece) {
		panic(InvalidMove{})
	}
	old.prevPiece = old.prevPiece & 0xF
	if !activePiece(old.prevPiece) {
		panic(InvalidMove{})
	}
	if old.prevPiece != new.nextPiece {
		if old.prevPiece != 9 || new.posY != 0 {
			panic(InvalidMove{})
		}
	}
	move := [2]int8{new.posX - old.posX, new.posY - old.posY}
	valid := false
	for m := range validMovesForPiece(board.board, old.prevPiece, old.posX, old.posY) {
		if move[0] == m[0] && move[1] == m[1] {
			valid = true
		}
	}
	if !valid {
		panic(InvalidMove{})
	}
	if old.prevPiece == 9 {
		board.movesSincePawn = 0
		if new.posY == 0 && new.nextPiece == 9 {
			state[new.posY][new.posX] = QUEEN | 1
		}
	}
	return swap(state)
}

// Validate and return new board state.
func (board boardModel) update(state board) boardModel {
	m := make([]mutation, 0)
	for posY, r := range board.board {
		for posX, piece := range r {
			if piece != state[posY][posX] {
				m = append(m, mutation{int8(posX), int8(posY), piece, state[posY][posX]})
			}
		}
	}
	var next boardModel
	next.board = board.validateMutation(m, state)
	next.moveCount = board.moveCount + 1
	next.movesSincePawn = board.movesSincePawn + 1
	return next
}

//     def lookahead_boards_for_board(self, check):
//         return chain.from_iterable(
//             starmap(
//                 partial(lookahead_boards_for_piece, self.board, check),
//                 active_pieces(self.board)))
//
//     def _valid_root_lookahead_boards_end(self):
//         """
//         Provide an iterable of valid moves for current board state.
//         """
//         check = lookahead_check(self.board)
//         return all(map(
//             lambda board: (KING | 1) in BoardModel(board),
//             self.lookahead_boards_for_board(check)))
//
//     def _valid_root_lookahead_boards(self, check):
//         """
//         Provide an iterable of valid moves for current board state.
//         """
//         return filter(
//             lambda board: BoardModel(board)._valid_root_lookahead_boards_end(),
//             self.lookahead_boards_for_board(check))
//
//     def _prune_lookahead_boards(self, n, active=True):
//         """
//         Provide an iterable of valid moves for current board state.
//         """
//         check = lookahead_check(self.board)
//         if n == 1:
//             return iter((self.board if active else swap(self.board),))
//         return chain.from_iterable(map(
//             lambda board: BoardModel(board)._prune_lookahead_boards(n - 1, not active),
//             self.lookahead_boards_for_board(check)))
//
//     def prune_lookahead_boards(self, n):
//         """
//         Provide an iterable of valid moves for current board state.
//         """
//         check = lookahead_check(self.board)
//         return chain.from_iterable(
//             map(
//                 lambda board: map(
//                     partial(make_tuple, swap(board)),
//                     BoardModel(board)._prune_lookahead_boards(n - 1)),
//                 self._valid_root_lookahead_boards(check)))
//
//     def _lookahead_boards(self, n, active=False):
//         """
//         Provide an iterable of valid moves for current board state.
//         """
//         check = lookahead_check(self.board)
//         if not self:
//             return iter((((self.board if active else swap(self.board)) for _ in range(n)),))
//         if n == 0:
//             return iter(((),))
//         return chain.from_iterable(
//             map(
//                 lambda board: map(
//                     lambda t: (board if active else swap(board),) + tuple(t),
//                     BoardModel(board)._lookahead_boards(n - 1, not active)),
//                 self.lookahead_boards_for_board(check)))
//
//     def lookahead_boards(self, n, active=False):
//         """
//         Provide an iterable of valid moves for current board state.
//         """
//         check = lookahead_check(self.board)
//         if not self:
//             return iter((((self.board if active else swap(self.board)) for _ in range(n)),))
//         if n == 0:
//             return iter(((),))
//         return chain.from_iterable(
//             map(
//                 lambda board: map(
//                     lambda t: (board if active else swap(board),) + tuple(t),
//                     BoardModel(board)._lookahead_boards(n - 1, not active)),
//                 self._valid_root_lookahead_boards(check)))

// Ensure active kings on board.
func (board boardModel) hasKings() bool {
	return board.contains(KING|1) && board.contains(KING)
}
