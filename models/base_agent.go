package models

import (
	"math"
	"math/rand"
)

// baseAgent agent.
type baseAgent interface {
	playRound(<-chan board) board
}

// Slayer of chess
//
// Override the following method to provide choice options.
// This method is called by multiprocessing.
//
// def evaluate_boards(self, best_boards):
//         """
//         // best_boards <- [<board_matrix>, ...]
//         // return <- (selection_weight, [<board_matrix>, ...])
//
//         select a sub slice of input and provide a collection weight.
//         """
//         ...
//         return (0, sample(best_boards, 3))
// type coreBaseAgent struct{}

type scoredBoard struct {
	score int
	board
}

// select a sub slice of input and provide a collection weight.
// boards <- [<board_matrix>, ...]
// return <- (selection_weight, [<board_matrix>, ...])
func (agent coreBaseAgent) evaluateBoards(boards <-chan board) <-chan scoredBoard {
	out := make(chan scoredBoard)
	go func() {
		out <- scoredBoard{0, <-boards}
		for b := range boards {
			if rand.Int() > 0 {
				out <- scoredBoard{0, b}
			}
		}
		close(out)
	}()
	return out
}

// Play a game round
func (agent coreBaseAgent) playRound(boards <-chan board) board {
	scoredBoards := make(chan scoredBoard)
	for i := 0; i < 4; i++ {
		go func() {
			for b := range agent.evaluateBoards(boards) {
				scoredBoards <- b
			}
		}()
	}
	maxBoard := make(chan board)
	go func() {
		maxBoards := make([]board, 0)
		max := -99
		for b := range scoredBoards {
			if b.score > max {
				maxBoards = make([]board, 0)
				maxBoards = append(maxBoards, b.board)
				max = b.score
			} else if b.score == max {
				maxBoards = append(maxBoards, b.board)
			}
		}
		for _, b := range maxBoards {
			maxBoard <- b
		}
		close(maxBoard)
	}()
	out := <-maxBoard
	for b := range maxBoard {
		if rand.Int() > 0 {
			out = b
		}
	}
	return out
}

type pieceValues struct {
	piece     int
	positions [8][8]int
}

func getScore(leaf board, posY int, posX int, piece uint8, valueMap map[string]pieceValues) int {
	values := valueMap["EMPTY_SPACE"]
	switch piece & 0xF {
	case 2:
		values = valueMap["OppBISHOP"]
	case 3:
		values = valueMap["OwnBISHOP"]
	case 4:
		values = valueMap["OppKING"]
	case 5:
		values = valueMap["OwnKING"]
	case 6:
		values = valueMap["OppKNIGHT"]
	case 7:
		values = valueMap["OwnKNIGHT"]
	case 8:
		values = valueMap["OppPAWN"]
	case 9:
		values = valueMap["OwnPAWN"]
	case 10:
		values = valueMap["OppQUEEN"]
	case 11:
		values = valueMap["OwnQUEEN"]
	case 12:
		values = valueMap["OppROOK"]
	case 13:
		values = valueMap["OwnROOK"]
	}
	return values.piece + values.positions[posY][posX]
}

// Uses a piece and square weighting to implement .
//
// override the following values to implement.
//
// Own<PIECE>Val = int
// ...
//
// Opp<PIECE>Val = int
// ...
//
// Own<PIECE>Squares = <board_matrix>
// ...
//
// Opp<PIECE>Squares = <board_matrix>
// ...
//
// ZEROSquares = <board_matrix>
type weightAgent struct {
	coreBaseAgent
	OwnPAWNVal   int
	OwnKNIGHTVal int
	OwnBISHOPVal int
	OwnROOKVal   int
	OwnQUEENVal  int
	OwnKINGVal   int

	OppPAWNVal   int
	OppKNIGHTVal int
	OppBISHOPVal int
	OppROOKVal   int
	OppQUEENVal  int
	OppKINGVal   int

	OwnPAWNSquares   [8][8]int
	OwnKNIGHTSquares [8][8]int
	OwnBISHOPSquares [8][8]int
	OwnROOKSquares   [8][8]int
	OwnQUEENSquares  [8][8]int
	OwnKINGSquares   [8][8]int

	OppPAWNSquares   [8][8]int
	OppKNIGHTSquares [8][8]int
	OppBISHOPSquares [8][8]int
	OppROOKSquares   [8][8]int
	OppQUEENSquares  [8][8]int
	OppKINGSquares   [8][8]int
	ZEROSquares      [8][8]int
}

func (agent weightAgent) checkSequence(sequence []board, valueMap map[string]pieceValues) int {
	leaf := sequence[len(sequence)-2]
	sum := 0
	for posY, r := range leaf {
		for posX, piece := range r {
			sum += getScore(leaf, posY, posX, piece, valueMap)
		}
	}
	return sum
}

func (agent weightAgent) sequenceGrouper(root board, sequences [][]board, valueMap map[string]pieceValues) scoredBoard {
	rootValue := 0
	for _, sequence := range sequences {
		if rand.Int() > 0 {
			rootValue = agent.checkSequence(sequence, valueMap)
		}
	}
	return scoredBoard{int(math.Round(float64(rootValue) / 100)), root}
}

// Determine value for each board state in array of board states
//
// Inputs:
//     boards: Array of board states
//
// Outputs:
//     best_state: The highest valued board state in the array
func (agent weightAgent) evaluateBoards(boards <-chan board) <-chan scoredBoard {
	// Pair encoded pieces to values
	valueMap := make(map[string]pieceValues)

	valueMap["OwnPAWN"] = pieceValues{agent.OwnPAWNVal, agent.OwnPAWNSquares}
	valueMap["OwnKNIGHT"] = pieceValues{agent.OwnKNIGHTVal, agent.OwnKNIGHTSquares}
	valueMap["OwnBISHOP"] = pieceValues{agent.OwnBISHOPVal, agent.OwnBISHOPSquares}
	valueMap["OwnROOK"] = pieceValues{agent.OwnROOKVal, agent.OwnROOKSquares}
	valueMap["OwnQUEEN"] = pieceValues{agent.OwnQUEENVal, agent.OwnQUEENSquares}
	valueMap["OwnKING"] = pieceValues{agent.OwnKINGVal, agent.OwnKINGSquares}

	valueMap["OppPAWN"] = pieceValues{agent.OppPAWNVal, agent.OppPAWNSquares}
	valueMap["OppKNIGHT"] = pieceValues{agent.OppKNIGHTVal, agent.OppKNIGHTSquares}
	valueMap["OppBISHOP"] = pieceValues{agent.OppBISHOPVal, agent.OppBISHOPSquares}
	valueMap["OppROOK"] = pieceValues{agent.OppROOKVal, agent.OppROOKSquares}
	valueMap["OppQUEEN"] = pieceValues{agent.OppQUEENVal, agent.OppQUEENSquares}
	valueMap["OppKING"] = pieceValues{agent.OppKINGVal, agent.OppKINGSquares}

	valueMap["EMPTY_SPACE"] = pieceValues{50, agent.ZEROSquares}

	scoredBoards := make(chan scoredBoard)
	go func() {
		for b := range boards {
			sequences := make([][]board, 0)
			scoredBoards <- agent.sequenceGrouper(b, sequences, valueMap)
		}
	}()

	maxBoard := make(chan scoredBoard)
	go func() {
		maxBoards := make([]board, 0)
		max := -99
		for b := range scoredBoards {
			if b.score > max {
				maxBoards = make([]board, 0)
				maxBoards = append(maxBoards, b.board)
				max = b.score
			} else if b.score == max {
				maxBoards = append(maxBoards, b.board)
			}
		}
		for _, b := range maxBoards {
			maxBoard <- scoredBoard{max, b}
		}
		close(maxBoard)
	}()

	return maxBoard
}

// class WeightAgent(BaseAgent):
//     def evaluate_boards(self, boards):
//
//          best_boards = [(rootValue, root), ...]
//         best_boards = starmap(
//             partial(self.sequence_grouper, **value_map), groupby(boards, itemgetter(0)))
//          best_boards = [(rootValue, [(rootValue, root), ...]), ...]
//         best_boards = groupby(sorted(best_boards), itemgetter(0))
//          best_boards = (rootValue, [(rootValue, root), ...])
//         try:
//             best_boards = next(best_boards)
//         except StopIteration:
//             return (self.OppKINGVal * 64, [])
//          best_boards = [(rootValue, root), ...]
//         best_average, best_boards = best_boards
//          best_boards = [root, ...]
//         best_boards = tuple(map(itemgetter(1), best_boards))
//
//         return (best_average, best_boards)

func positiveWeightAgent() weightAgent {
	var agent weightAgent
	// Piece values
	agent.OwnPAWNVal = 20100
	agent.OwnKNIGHTVal = 20320
	agent.OwnBISHOPVal = 20330
	agent.OwnROOKVal = 20500
	agent.OwnQUEENVal = 29000
	agent.OwnKINGVal = 40000

	agent.OppPAWNVal = 19900
	agent.OppKNIGHTVal = 19680
	agent.OppBISHOPVal = 19670
	agent.OppROOKVal = 19500
	agent.OppQUEENVal = 11000
	agent.OppKINGVal = 0

	// pylama:ignore=E201,E203,E231
	// Piece squares - from http://www.chessbin.com/post/Piece-Square-Table
	// Own piece squares
	agent.OwnPAWNSquares = [8][8]int{
		{50, 50, 50, 50, 50, 50, 50, 50},
		{100, 100, 100, 100, 100, 100, 100, 100},
		{60, 60, 70, 80, 80, 70, 60, 60},
		{55, 55, 60, 75, 75, 60, 55, 55},
		{50, 50, 50, 70, 70, 50, 50, 50},
		{55, 45, 40, 50, 50, 40, 45, 55},
		{55, 60, 60, 30, 30, 60, 60, 55},
		{50, 50, 50, 50, 50, 50, 50, 50},
	}
	agent.OwnKNIGHTSquares = [8][8]int{
		{0, 10, 20, 20, 20, 20, 10, 0},
		{10, 30, 50, 50, 50, 50, 30, 10},
		{20, 50, 60, 65, 65, 60, 50, 20},
		{20, 55, 65, 70, 70, 65, 55, 20},
		{20, 50, 65, 70, 70, 65, 50, 20},
		{20, 55, 60, 65, 65, 60, 55, 20},
		{10, 30, 50, 55, 55, 50, 30, 10},
		{0, 10, 30, 20, 20, 30, 10, 0},
	}
	agent.OwnBISHOPSquares = [8][8]int{
		{30, 40, 40, 40, 40, 40, 40, 30},
		{40, 50, 50, 50, 50, 50, 50, 40},
		{40, 50, 55, 60, 60, 55, 50, 40},
		{40, 55, 55, 60, 60, 55, 55, 40},
		{40, 50, 60, 60, 60, 60, 50, 40},
		{40, 60, 60, 60, 60, 60, 60, 40},
		{40, 55, 50, 50, 50, 50, 55, 40},
		{30, 40, 10, 40, 40, 10, 40, 30},
	}
	agent.OwnROOKSquares = [8][8]int{
		{50, 50, 50, 50, 50, 50, 50, 50},
		{55, 60, 60, 60, 60, 60, 60, 55},
		{45, 50, 50, 50, 50, 50, 50, 45},
		{45, 50, 50, 50, 50, 50, 50, 45},
		{45, 50, 50, 50, 50, 50, 50, 45},
		{45, 50, 50, 50, 50, 50, 50, 45},
		{45, 50, 50, 50, 50, 50, 50, 45},
		{50, 50, 50, 55, 55, 50, 50, 50},
	}
	agent.OwnQUEENSquares = [8][8]int{
		{30, 40, 40, 45, 45, 40, 40, 30},
		{40, 50, 50, 50, 50, 50, 50, 40},
		{40, 50, 55, 55, 55, 55, 50, 40},
		{45, 50, 55, 55, 55, 55, 50, 45},
		{50, 50, 55, 55, 55, 55, 50, 45},
		{40, 55, 55, 55, 55, 55, 50, 40},
		{40, 50, 55, 50, 50, 50, 50, 40},
		{30, 40, 40, 45, 45, 40, 40, 30},
	}
	agent.OwnKINGSquares = [8][8]int{
		{20, 10, 10, 0, 0, 10, 10, 20},
		{20, 10, 10, 0, 0, 10, 10, 20},
		{20, 10, 10, 0, 0, 10, 10, 20},
		{20, 10, 10, 0, 0, 10, 10, 20},
		{30, 20, 20, 10, 10, 20, 20, 30},
		{40, 30, 30, 30, 30, 30, 30, 40},
		{70, 70, 50, 50, 50, 50, 70, 70},
		{70, 80, 60, 50, 50, 60, 80, 70},
	}

	// Opp piece squares
	agent.OppPAWNSquares = [8][8]int{
		{50, 50, 50, 50, 50, 50, 50, 50},
		{45, 40, 40, 70, 70, 40, 40, 45},
		{45, 55, 60, 50, 50, 60, 55, 45},
		{50, 50, 50, 30, 30, 50, 50, 50},
		{45, 45, 40, 25, 25, 40, 45, 45},
		{40, 40, 30, 20, 20, 30, 40, 40},
		{0, 0, 0, 0, 0, 0, 0, 0},
		{50, 50, 50, 50, 50, 50, 50, 50},
	}
	agent.OppKNIGHTSquares = [8][8]int{
		{100, 90, 70, 80, 80, 70, 90, 100},
		{90, 70, 50, 45, 45, 50, 70, 90},
		{80, 45, 40, 35, 35, 40, 45, 80},
		{80, 50, 35, 30, 30, 35, 50, 80},
		{80, 45, 35, 30, 30, 35, 45, 80},
		{80, 50, 40, 35, 35, 40, 50, 80},
		{90, 70, 50, 50, 50, 50, 70, 90},
		{100, 10, 30, 20, 20, 30, 10, 100},
	}
	agent.OppBISHOPSquares = [8][8]int{
		{70, 60, 90, 60, 60, 90, 60, 70},
		{60, 45, 50, 50, 50, 50, 45, 60},
		{60, 40, 40, 40, 40, 40, 40, 60},
		{60, 50, 40, 40, 40, 40, 50, 60},
		{60, 45, 45, 40, 40, 45, 45, 60},
		{60, 50, 45, 40, 40, 45, 50, 60},
		{60, 50, 50, 50, 50, 50, 50, 60},
		{70, 60, 90, 60, 60, 90, 60, 70},
	}
	agent.OppROOKSquares = [8][8]int{
		{50, 50, 50, 45, 45, 50, 50, 50},
		{55, 50, 50, 50, 50, 50, 50, 55},
		{55, 50, 50, 50, 50, 50, 50, 55},
		{55, 50, 50, 50, 50, 50, 50, 55},
		{55, 50, 50, 50, 50, 50, 50, 55},
		{55, 50, 50, 50, 50, 50, 50, 55},
		{45, 40, 40, 40, 40, 40, 40, 45},
		{50, 50, 50, 50, 50, 50, 50, 50},
	}
	agent.OppQUEENSquares = [8][8]int{
		{70, 60, 60, 55, 55, 60, 60, 70},
		{60, 50, 50, 50, 50, 45, 50, 60},
		{60, 50, 45, 45, 45, 45, 45, 60},
		{50, 50, 45, 45, 45, 45, 50, 55},
		{55, 50, 45, 45, 45, 45, 50, 55},
		{60, 50, 45, 45, 45, 45, 50, 60},
		{60, 50, 50, 50, 50, 50, 50, 60},
		{70, 60, 60, 55, 55, 60, 60, 70},
	}
	agent.OppKINGSquares = [8][8]int{
		{30, 20, 40, 50, 50, 40, 20, 30},
		{30, 30, 50, 50, 50, 50, 30, 30},
		{60, 70, 70, 70, 70, 70, 70, 60},
		{70, 80, 80, 90, 90, 80, 80, 70},
		{80, 90, 90, 100, 100, 90, 90, 80},
		{80, 90, 90, 100, 100, 90, 90, 80},
		{80, 90, 90, 100, 100, 90, 90, 80},
		{80, 90, 90, 100, 100, 90, 90, 80},
	}
	agent.ZEROSquares = [8][8]int{
		{50, 50, 50, 50, 50, 50, 50, 50},
		{50, 50, 50, 50, 50, 50, 50, 50},
		{50, 50, 50, 50, 50, 50, 50, 50},
		{50, 50, 50, 50, 50, 50, 50, 50},
		{50, 50, 50, 50, 50, 50, 50, 50},
		{50, 50, 50, 50, 50, 50, 50, 50},
		{50, 50, 50, 50, 50, 50, 50, 50},
		{50, 50, 50, 50, 50, 50, 50, 50},
	}
	return agent
}

func balanceWeightAgent() weightAgent {
	var agent weightAgent
	// Piece values
	agent.OwnPAWNVal = 100
	agent.OwnKNIGHTVal = 320
	agent.OwnBISHOPVal = 330
	agent.OwnROOKVal = 500
	agent.OwnQUEENVal = 9000
	agent.OwnKINGVal = 20000

	agent.OppPAWNVal = -agent.OwnPAWNVal
	agent.OppKNIGHTVal = -agent.OwnKNIGHTVal
	agent.OppBISHOPVal = -agent.OwnBISHOPVal
	agent.OppROOKVal = -agent.OwnROOKVal
	agent.OppQUEENVal = -agent.OwnQUEENVal
	agent.OppKINGVal = -agent.OwnKINGVal

	// pylama:ignore=E201,E203,E231
	// Piece squares - from http://www.chessbin.com/post/Piece-Square-Table
	// Own piece squares
	agent.OwnPAWNSquares = [8][8]int{
		{0, 0, 0, 0, 0, 0, 0, 0},
		{50, 50, 50, 50, 50, 50, 50, 50},
		{10, 10, 20, 30, 30, 20, 10, 10},
		{5, 5, 10, 25, 25, 10, 5, 5},
		{0, 0, 0, 20, 20, 0, 0, 0},
		{5, -5, -10, 0, 0, -10, -5, 5},
		{5, 10, 10, -20, -20, 10, 10, 5},
		{0, 0, 0, 0, 0, 0, 0, 0},
	}
	agent.OwnKNIGHTSquares = [8][8]int{
		{-50, -40, -30, -30, -30, -30, -40, -50},
		{-40, -20, 0, 0, 0, 0, -20, -40},
		{-30, 0, 10, 15, 15, 10, 0, -30},
		{-30, 5, 15, 20, 20, 15, 5, -30},
		{-30, 0, 15, 20, 20, 15, 0, -30},
		{-30, 5, 10, 15, 15, 10, 5, -30},
		{-40, -20, 0, 5, 5, 0, -20, -40},
		{-50, -40, -20, -30, -30, -20, -40, -50},
	}
	agent.OwnBISHOPSquares = [8][8]int{
		{-20, -10, -10, -10, -10, -10, -10, -20},
		{-10, 0, 0, 0, 0, 0, 0, -10},
		{-10, 0, 5, 10, 10, 5, 0, -10},
		{-10, 5, 5, 10, 10, 5, 5, -10},
		{-10, 0, 10, 10, 10, 10, 0, -10},
		{-10, 10, 10, 10, 10, 10, 10, -10},
		{-10, 5, 0, 0, 0, 0, 5, -10},
		{-20, -10, -40, -10, -10, -40, -10, -20},
	}
	agent.OwnROOKSquares = [8][8]int{
		{0, 0, 0, 0, 0, 0, 0, 0},
		{5, 10, 10, 10, 10, 10, 10, 5},
		{-5, 0, 0, 0, 0, 0, 0, -5},
		{-5, 0, 0, 0, 0, 0, 0, -5},
		{-5, 0, 0, 0, 0, 0, 0, -5},
		{-5, 0, 0, 0, 0, 0, 0, -5},
		{-5, 0, 0, 0, 0, 0, 0, -5},
		{0, 0, 0, 5, 5, 0, 0, 0},
	}
	agent.OwnQUEENSquares = [8][8]int{
		{-20, -10, -10, -5, -5, -10, -10, -20},
		{-10, 0, 0, 0, 0, 0, 0, -10},
		{-10, 0, 5, 5, 5, 5, 0, -10},
		{-5, 0, 5, 5, 5, 5, 0, -5},
		{0, 0, 5, 5, 5, 5, 0, -5},
		{-10, 5, 5, 5, 5, 5, 0, -10},
		{-10, 0, 5, 0, 0, 0, 0, -10},
		{-20, -10, -10, -5, -5, -10, -10, -20},
	}
	agent.OwnKINGSquares = [8][8]int{
		{-30, -40, -40, -50, -50, -40, -40, -30},
		{-30, -40, -40, -50, -50, -40, -40, -30},
		{-30, -40, -40, -50, -50, -40, -40, -30},
		{-30, -40, -40, -50, -50, -40, -40, -30},
		{-20, -30, -30, -40, -40, -30, -30, -20},
		{-10, -20, -20, -20, -20, -20, -20, -10},
		{20, 20, 0, 0, 0, 0, 20, 20},
		{20, 30, 10, 0, 0, 10, 30, 20},
	}

	// Opp piece squares
	agent.OppPAWNSquares = [8][8]int{
		{0, 0, 0, 0, 0, 0, 0, 0},
		{-5, -10, -10, 20, 20, -10, -10, -5},
		{-5, 5, 10, 0, 0, 10, 5, -5},
		{0, 0, 0, -20, -20, 0, 0, 0},
		{-5, -5, -10, -25, -25, -10, -5, -5},
		{-10, -10, -20, -30, -30, -20, -10, -10},
		{-50, -50, -50, -50, -50, -50, -50, -50},
		{0, 0, 0, 0, 0, 0, 0, 0},
	}
	agent.OppKNIGHTSquares = [8][8]int{
		{50, 40, 20, 30, 30, 20, 40, 50},
		{40, 20, 0, -5, -5, 0, 20, 40},
		{30, -5, -10, -15, -15, -10, -5, 30},
		{30, 0, -15, -20, -20, -15, 0, 30},
		{30, -5, -15, -20, -20, -15, -5, 30},
		{30, 0, -10, -15, -15, -10, 0, 30},
		{40, 20, 0, 0, 0, 0, 20, 40},
		{50, -40, -20, -30, -30, -20, -40, 50},
	}
	agent.OppBISHOPSquares = [8][8]int{
		{20, 10, 40, 10, 10, 40, 10, 20},
		{10, -5, 0, 0, 0, 0, -5, 10},
		{10, -10, -10, -10, -10, -10, -10, 10},
		{10, 0, -10, -10, -10, -10, 0, 10},
		{10, -5, -5, -10, -10, -5, -5, 10},
		{10, 0, -5, -10, -10, -5, 0, 10},
		{10, 0, 0, 0, 0, 0, 0, 10},
		{20, 10, 40, 10, 10, 40, 10, 20},
	}
	agent.OppROOKSquares = [8][8]int{
		{0, 0, 0, -5, -5, 0, 0, 0},
		{5, 0, 0, 0, 0, 0, 0, 5},
		{5, 0, 0, 0, 0, 0, 0, 5},
		{5, 0, 0, 0, 0, 0, 0, 5},
		{5, 0, 0, 0, 0, 0, 0, 5},
		{5, 0, 0, 0, 0, 0, 0, 5},
		{-5, -10, -10, -10, -10, -10, -10, -5},
		{0, 0, 0, 0, 0, 0, 0, 0},
	}
	agent.OppQUEENSquares = [8][8]int{
		{20, 10, 10, 5, 5, 10, 10, 20},
		{10, 0, 0, 0, 0, -5, 0, 10},
		{10, 0, -5, -5, -5, -5, -5, 10},
		{0, 0, -5, -5, -5, -5, 0, 5},
		{5, 0, -5, -5, -5, -5, 0, 5},
		{10, 0, -5, -5, -5, -5, 0, 10},
		{10, 0, 0, 0, 0, 0, 0, 10},
		{20, 10, 10, 5, 5, 10, 10, 20},
	}
	agent.OppKINGSquares = [8][8]int{
		{-20, -30, -10, 0, 0, -10, -30, -20},
		{-20, -20, 0, 0, 0, 0, -20, -20},
		{10, 20, 20, 20, 20, 20, 20, 10},
		{20, 30, 30, 40, 40, 30, 30, 20},
		{30, 40, 40, 50, 50, 40, 40, 30},
		{30, 40, 40, 50, 50, 40, 40, 30},
		{30, 40, 40, 50, 50, 40, 40, 30},
		{30, 40, 40, 50, 50, 40, 40, 30},
	}
	agent.ZEROSquares = [8][8]int{
		{0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0},
	}
	return agent
}

// Use strategy to evaluate a sequence of root values.
//
// STRATEGY = lambda <int_sequence>: int
type strategyAgent interface {
	strategy([]int) int
}

type baseStrategyAgent struct {
	coreBaseAgent
}

// STRATEGY = harmonic_mean
func (agent baseStrategyAgent) strategy(values []int) int {
	return values[0]
}

func (agent baseStrategyAgent) checkSequence(sequence []board, valueMap map[string]pieceValues) int {
	leaf := sequence[len(sequence)-2]
	sum := 0
	for posY, r := range leaf {
		for posX, piece := range r {
			sum += getScore(leaf, posY, posX, piece, valueMap)
		}
	}
	return sum
}

func (agent baseStrategyAgent) sequenceGrouper(root board, sequences [][]board, valueMap map[string]pieceValues) scoredBoard {
	values := make([]int, len(sequences))
	for _, sequence := range sequences {
		if rand.Int() > 0 {
			values = append(values, agent.checkSequence(sequence, valueMap))
		}
	}
	rootValue := agent.strategy(values)
	return scoredBoard{int(math.Round(float64(rootValue) / 100)), root}
}

// BaseAgent Computer Agent.
type coreBaseAgent struct{}

// class BalanceAgent(StrategyAgent, BalanceWeightAgent):
//     """Computer Agent"""
//     def STRATEGY(values):
//         return harmonic_mean(map(lambda value: value if value > 0 else 0, values))
//
//
// class NewAgent(StrategyAgent, BalanceWeightAgent):
//     """Computer Agent"""
//     STRATEGY = min
//
//
// class MaxBalanceAgent(StrategyAgent, BalanceWeightAgent):
//     """Computer Agent"""
//     STRATEGY = max
//
//
// class MaxPositiveAgent(StrategyAgent, PositiveWeightAgent):
//     """Computer Agent"""
//     STRATEGY = max
//
//
// class MinPositiveAgent(StrategyAgent, PositiveWeightAgent):
//     """Computer Agent"""
//     STRATEGY = min

// agents agents.
var agents = map[string]baseAgent{
	"base-agent": coreBaseAgent{},
	// "balance-agent":      BalanceAgent,
	// "new-agent":          NewAgent,
	// "max-balance-agent":  MaxPositiveAgent,
	// "max-positive-agent": MaxPositiveAgent,
	// "min-positive-agent": MinPositiveAgent,
}
