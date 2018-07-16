package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"net/url"
	"strings"

	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
)

var pieceName = map[int]string{
	3:  "bishop",
	5:  "king",
	7:  "knight",
	9:  "pawn",
	11: "queen",
	13: "rook",
}

const (
	prompt              = "> "
	brightGreen         = "\u001b[42;1m"
	reset               = "\u001b[0m"
	selectedPiece       = brightGreen + "{}" + reset
	topBoardOutputShell = `
  A B C D E F G H
  +---------------`
)

var boardOutputShell = [8]string{"8|", "7|", "6|", "5|", "4|", "3|", "2|", "1|"}

func getInfo(apiURL url.URL, gameID uuid.UUID) string {
	path, err := url.Parse("v1.0/games/" + gameID.String() + "/info")
	if err != nil {
		panic(err)
	}
	apiURL = *apiURL.ResolveReference(path)
	resp, err := http.Get(apiURL.RequestURI())
	if err != nil {
		panic(err)
	}
	var message neuralknightmodels.BoardInfoMessage
	err = json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		panic(err)
	}
	return message.Print
}

func formatBoard(board string) []string {
	lines := strings.Split(board, "\n")
	for i, line := range lines {
		lines[i] = strings.Join(strings.Split(line, ""), " ")
	}
	return lines
}

// Print board in shell.
func printBoard(board []string) {
	println(topBoardOutputShell)
	for i, line := range board {
		println(boardOutputShell[i] + line)
	}
}

func printCmds() {
	println("> piece <col> <row>  # select piece")
	println("> move <col> <row>   # move selected piece to")
	println("> reset              # start a new game")
}

// CLIAgent agent.
type CLIAgent struct {
	apiURL url.URL
	piece  *[2]int
	gameID uuid.UUID
	user   uuid.UUID
}

// MakeCLIAgent agent.
func makeCLIAgent(apiURL url.URL) CLIAgent {
	var agent CLIAgent
	agent.apiURL = apiURL
	agent.doReset()
	return agent
}

func (agent CLIAgent) doReset() {
	agent.piece = nil
	path, err := url.Parse("v1.0/games/")
	if err != nil {
		panic(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	resp, err := http.Post(apiURL.RequestURI(), "", bytes.NewReader([]byte{}))
	if err != nil {
		panic(err)
	}
	var game neuralknightmodels.BoardCreateMessage
	err = json.NewDecoder(resp.Body).Decode(game)
	if err != nil {
		panic(err)
	}
	gameID, err := uuid.FromString(game.ID)
	if err != nil {
		panic(err)
	}
	agent.gameID = gameID
	path, err = url.Parse("v1.0/agent/")
	if err != nil {
		panic(err)
	}
	apiURL = agent.apiURL.ResolveReference(path)
	var messageCreate neuralknightmodels.AgentCreateMessage
	messageCreate.GameID = agent.gameID.String()
	messageCreate.Player = 1
	messageCreate.User = true
	buffer, err := json.Marshal(messageCreate)
	if err != nil {
		panic(err)
	}
	resp, err = http.Post(apiURL.RequestURI(), "", bytes.NewReader(buffer))
	if err != nil {
		panic(err)
	}
	var message neuralknightmodels.AgentCreateResponse
	err = json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		panic(err)
	}
	agentID, err := uuid.FromString(message.AgentID)
	if err != nil {
		panic(err)
	}
	agent.user = agentID
	messageCreate.User = false
	messageCreate.Player = 2
	messageCreate.Lookahead = 2
	messageCreate.Delegate = "max-balance-agent"
	buffer, err = json.Marshal(messageCreate)
	if err != nil {
		panic(err)
	}
	resp, err = http.Post(apiURL.RequestURI(), "", bytes.NewReader(buffer))
	if err != nil {
		panic(err)
	}
	err = json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		panic(err)
	}
	printCmds()
	printBoard(formatBoard(getInfo(agent.apiURL, agent.gameID)))
}

// Select piece for move.
func (agent CLIAgent) doPiece(col, row string) {
	args := agent.parse(col, row)
	if args == nil {
		agent.printInvalid("piece " + col + " " + row)
		return
	}
	agent.piece = args
}

// class CLIAgent(Cmd):
//     prompt = PROMPT
//
//     def do_piece(self, arg_str):
//         response = requests.get(f"{ self.api_url }/v1.0/games/{ self.game_id }")
//         state = response.json()["state"]
//         if state == {"end": True}:
//             return print("game over")
//         board = tuple(map(bytes.fromhex, state))
//         try:
//             piece = board[args[1]][args[0]]
//         except IndexError:
//             return self.print_invalid("piece " + arg_str)
//         if not (piece and (piece & 1)):
//             return self.print_invalid("piece " + arg_str)
//         board = list(map(list, get_info(self.api_url, self.game_id).splitlines()))
//         board[args[1]][args[0]] = SELECTED_PIECE.format(
//             board[args[1]][args[0]])
//         print_board(map(" ".join, board))
//         print(f"Selected: { PIECE_NAME[piece & 0xF] }")
//

// Make move.
func (agent CLIAgent) doMove(col, row string) {
	if agent.piece == nil {
		agent.printInvalid("move " + col + " " + row)
		return
	}
	args := agent.parse(col, row)
	if args == nil {
		agent.printInvalid("move " + col + " " + row)
		return
	}
}

//     def do_move(self, arg_str):
//         move = {"move": (tuple(reversed(self.piece)), tuple(reversed(args)))}
//         self.piece = None
//
//         response = requests.put(
//             f"{ self.api_url }/agent/{ self.user }",
//             json=move,
//             headers={
//                 "content-type": "application/json",
//             }
//         )
//         if response.status_code != 200 or response.json().get("invalid", False):
//             print_board(format_board(get_info(self.api_url, self.game_id)))
//             return print("Invalid move.")
//         if response.json().get("state", {}).get("end", False):
//             print_board(format_board(get_info(self.api_url, self.game_id)))
//             return print("you won")
//         response = requests.get(f"{ self.api_url }/v1.0/games/{ self.game_id }")
//         in_board = response.json()["state"]
//         print_board(format_board(get_info(self.api_url, self.game_id)))
//         if in_board == {"end": True}:
//             return print("you won")
//         print("making move ...")
//         board = in_board
//         while in_board == board:
//             sleep(2)
//             response = requests.get(f"{ self.api_url }/v1.0/games/{ self.game_id }")
//             state = response.json()["state"]
//             if state == {"end": True}:
//                 return print("game over")
//             response = requests.get(
//                 f"{ self.api_url }/agent/{ self.user }",
//                 headers={
//                     "content-type": "application/json",
//                 }
//             )
//             if response.status_code != 200:
//                 return self.do_reset()
//             try:
//                 if response.json()["state"] == {"end": True}:
//                     return self.do_reset()
//             except Exception:
//                 return self.do_reset()
//             board = state
//         print_board(format_board(get_info(self.api_url, self.game_id)))
//

func (agent CLIAgent) printInvalid(args string) {
	printBoard(formatBoard(getInfo(agent.apiURL, agent.gameID)))
	println("invalid command:", args)
	printCmds()
}

// Split arguments.
func (agent CLIAgent) parse(col, row string) *[2]int {
	var output [2]int
	if len(col) != 1 {
		println("not valid column", col)
		return nil
	}
	switch col[0] {
	case 'a':
		output[0] = 0
	case 'b':
		output[0] = 1
	case 'c':
		output[0] = 2
	case 'd':
		output[0] = 3
	case 'e':
		output[0] = 4
	case 'f':
		output[0] = 5
	case 'g':
		output[0] = 6
	case 'h':
		output[0] = 7
	default:
		println("out of range column", col)
		return nil
	}
	n, err := fmt.Sscanf(row, "%d", &output[1])
	if n != 1 || err != nil {
		println(err, row)
		return nil
	}
	if output[1] > 8 || output[1] <= 0 {
		println("out of range row", output[1])
		return nil
	}
	output[1] = 8 - output[1]
	return &output
}

// Sanitize data.
func (agent CLIAgent) cmdLoop() {
	for {
		print(prompt)
		var cmd, col, row string
		n, err := fmt.Scanln(&cmd, &col, &row)
		cmd = strings.ToLower(cmd)
		if n == 1 && cmd == "reset" {
			continue
		}
		if err != nil {
			agent.printInvalid("Invalid command")
			continue
		}
		col = strings.ToLower(col)
		row = strings.ToLower(row)
		if cmd == "piece" {
			agent.doPiece(col, row)
			continue
		}
		if cmd == "move" {
			agent.doMove(col, row)
			continue
		}
	}
}

func main() {
	apiURLFlag := flag.String("api_url", "http://localhost:8080", "api_url")
	flag.Parse()
	if apiURLFlag == nil {
		panic(nil)
	}
	apiURL, err := url.Parse(*apiURLFlag)
	if err != nil {
		panic(err)
	}
	makeCLIAgent(*apiURL).cmdLoop()
}
