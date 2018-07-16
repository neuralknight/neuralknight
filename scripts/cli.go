package main

import (
	"bytes"
	"encoding/json"
	"flag"
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

// CLIAgent agent.
type CLIAgent struct {
	apiURL url.URL
	piece  *string
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
	var message neuralknightmodels.AgentCreateMessage
	apiURL = agent.apiURL.ResolveReference(path)
	resp, err = http.Post(apiURL.RequestURI(), "")
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
}

func (agent CLIAgent) cmdLoop() {}

// class CLIAgent(Cmd):
//     prompt = PROMPT
//
//     def do_reset(self, *args):
//         self.user = requests.post(
//             f"{ self.api_url }/issue-agent",
//             json={
//                 "game_id": self.game_id,
//                 "user": True},
//             headers={
//                 "content-type": "application/json"
//             },
//         ).json()["AgentID"]
//         try:
//             self.user = game["id"]
//         except KeyError:
//             return print("failed to reset")
//         requests.post(
//             f"{ self.api_url }/issue-agent",
//             json={
//                 "game_id": self.game_id,
//                 "player": 2,
//                 "lookahead": 2,
//                 "delegate": "max-balance-agent"},
//             headers={
//                 "content-type": "application/json"
//             })
//         print("> piece <col> <row>  # select piece")
//         print("> move <col> <row>   # move selected piece to")
//         print("> reset              # start a new game")
//         print_board(format_board(get_info(self.api_url, self.game_id)))
//
//     def do_piece(self, arg_str):
//         """
//         Select piece for move.
//         """
//         args = self.parse(arg_str)
//         if len(args) != 2:
//             return self.print_invalid("piece " + arg_str)
//         self.piece = args
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
//     def do_move(self, arg_str):
//         """
//         Make move.
//         """
//         if not self.piece:
//             return self.print_invalid("move " + arg_str)
//
//         args = self.parse(arg_str)
//         if len(args) != 2:
//             return self.print_invalid("move " + arg_str)
//
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
//     def print_invalid(self, args):
//         print_board(format_board(get_info(self.api_url, self.game_id)))
//         print("invalid command:", args)
//         print("> piece <col> <row>  # select piece")
//         print("> move <col> <row>   # move selected piece to")
//         print("> reset              # start a new game")
//
//     @staticmethod
//     def parse(args):
//         """
//         Split arguments.
//         """
//         args = args.split()
//         if len(args) != 2:
//             return args
//         try:
//             args[1] = 8 - int(args[1])
//             if not (0 <= args[1] < 8):
//                 print("out of range row")
//                 raise ValueError
//         except ValueError:
//             print("not int", args[1])
//             return ()
//         try:
//             args[0] = ord(args[0]) - ord("a")
//             if not (0 <= args[1] < 8):
//                 print("out of range column")
//                 raise ValueError
//         except ValueError:
//             print("not char", args[0])
//             return ()
//         return args
//
//     def emptyline(self):
//         """
//         Do nothing on empty command.
//         """
//
//     def precmd(self, line):
//         """
//         Sanitize data.
//         """
//         return line.strip().lower()

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
