package main

import (
	"bytes"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
)

type board [8][8]uint8

var pieceName = map[uint8]string{
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
	topBoardOutputShell = `
  A B C D E F G H
  +---------------`
)

var boardOutputShell = [8]string{"8|", "7|", "6|", "5|", "4|", "3|", "2|", "1|"}

func getInfo(apiURL url.URL, gameID uuid.UUID) string {
	path, err := url.Parse("v1.0/games/" + gameID.String() + "/info")
	if err != nil {
		log.Panicln(err)
	}
	apiURL = *apiURL.ResolveReference(path)
	resp, err := http.Get(apiURL.RequestURI())
	if err != nil {
		log.Panicln(err)
	}
	var message models.BoardInfoMessage
	err = json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		log.Panicln(err)
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
		log.Panicln(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	resp, err := http.Post(apiURL.RequestURI(), "", bytes.NewReader([]byte{}))
	if err != nil {
		log.Panicln(err)
	}
	var game models.BoardCreateMessage
	err = json.NewDecoder(resp.Body).Decode(game)
	if err != nil {
		log.Panicln(err)
	}
	gameID, err := uuid.FromString(game.ID)
	if err != nil {
		log.Panicln(err)
	}
	agent.gameID = gameID
	path, err = url.Parse("v1.0/agent/")
	if err != nil {
		log.Panicln(err)
	}
	apiURL = agent.apiURL.ResolveReference(path)
	var messageCreate models.AgentCreateMessage
	messageCreate.GameID = agent.gameID.String()
	messageCreate.Player = 1
	messageCreate.User = true
	buffer, err := json.Marshal(messageCreate)
	if err != nil {
		log.Panicln(err)
	}
	resp, err = http.Post(apiURL.RequestURI(), "", bytes.NewReader(buffer))
	if err != nil {
		log.Panicln(err)
	}
	var message models.AgentCreateResponse
	err = json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		log.Panicln(err)
	}
	agentID, err := uuid.FromString(message.AgentID)
	if err != nil {
		log.Panicln(err)
	}
	agent.user = agentID
	messageCreate.User = false
	messageCreate.Player = 2
	messageCreate.Lookahead = 2
	messageCreate.Delegate = "max-balance-agent"
	buffer, err = json.Marshal(messageCreate)
	if err != nil {
		log.Panicln(err)
	}
	resp, err = http.Post(apiURL.RequestURI(), "", bytes.NewReader(buffer))
	if err != nil {
		log.Panicln(err)
	}
	err = json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		log.Panicln(err)
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
	path, err := url.Parse("v1.0/games/" + agent.gameID.String())
	if err != nil {
		log.Panicln(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	resp, err := http.Get(apiURL.RequestURI())
	if err != nil {
		log.Panicln(err)
	}
	var message models.BoardStateMessage
	err = json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		log.Panicln(err)
	}
	if message.End {
		println("game over")
		return
	}
	var state board
	for i, r := range message.State {
		row, err := hex.DecodeString(r)
		if err != nil {
			log.Panicln(err)
		}
		if len(row) != 8 {
			log.Panicln(row)
		}
		copy(state[i][:], row)
	}
	piece := state[args[1]][args[0]]
	if piece&1 == 0 {
		agent.printInvalid("piece " + col + " " + row)
		return
	}
	board := strings.Split(getInfo(agent.apiURL, agent.gameID), "\n")
	for i, boardRow := range board {
		board[i] = strings.Join(strings.Split(boardRow, ""), " ")
	}
	boardRow := board[args[1]]
	boardRowSelection := strings.Split(boardRow, " ")
	boardRowSelection[args[0]] = brightGreen + boardRowSelection[args[0]] + reset
	board[args[1]] = strings.Join(boardRowSelection, " ")
	printBoard(board)
	println("Selected:", pieceName[piece&0xF])
}

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
	path, err := url.Parse("v1.0/agent/" + agent.user.String())
	if err != nil {
		log.Panicln(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	var message models.UserMoveMessage
	message.Move = [2][2]int{[2]int{agent.piece[1], agent.piece[0]}, [2]int{args[1], args[0]}}
	data, err := json.Marshal(message)
	if err != nil {
		log.Panicln(err)
	}
	req, err := http.NewRequest(http.MethodPut, apiURL.RequestURI(), bytes.NewReader(data))
	if err != nil {
		log.Panicln(err)
	}
	defer req.Body.Close()
	var client http.Client
	resp, err := client.Do(req)
	if err != nil {
		log.Panicln(err)
	}
	defer resp.Body.Close()
	var boardStateMessage models.BoardStateMessage
	json.NewDecoder(resp.Body).Decode(boardStateMessage)
	if boardStateMessage.Invalid {
		println("Invalid move.")
		return
	}
	if boardStateMessage.End {
		printBoard(formatBoard(getInfo(agent.apiURL, agent.gameID)))
		println("you won")
		agent.doReset()
		return
	}
	state := boardStateMessage.State
	nextState := state
	path, err = url.Parse("v1.0/games/" + agent.gameID.String())
	if err != nil {
		log.Panicln(err)
	}
	apiURL = agent.apiURL.ResolveReference(path)
	printBoard(formatBoard(getInfo(agent.apiURL, agent.gameID)))
	println("making move ...")
	for state == nextState {
		time.Sleep(2)
		resp, err = http.Get(apiURL.RequestURI())
		if err != nil {
			log.Panicln(err)
		}
		err = json.NewDecoder(resp.Body).Decode(boardStateMessage)
		if err != nil {
			log.Panicln(err)
		}
		if boardStateMessage.End {
			println("you won")
			agent.doReset()
			return
		}
	}
	printBoard(formatBoard(getInfo(agent.apiURL, agent.gameID)))
}

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
		log.Panicln(nil)
	}
	apiURL, err := url.Parse(*apiURLFlag)
	if err != nil {
		log.Panicln(err)
	}
	makeCLIAgent(*apiURL).cmdLoop()
}
