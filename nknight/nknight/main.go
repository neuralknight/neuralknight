package nknight

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/neuralknight/neuralknight/models"
	log "github.com/sirupsen/logrus"
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
	apiURL  url.URL
	piece   *[2]int
	gameURL *url.URL
	userURL *url.URL
}

func (agent CLIAgent) gameURI() string {
	if agent.gameURL == nil {
		log.Fatalln("no game url found")
	}
	return agent.gameURL.String()
}

func (agent CLIAgent) agentURI() string {
	if agent.userURL == nil {
		log.Fatalln("no agent url found")
	}
	return agent.userURL.String()
}

func (agent CLIAgent) getInfo() string {
	resp, err := http.Get(agent.gameURI() + "/info")
	if err != nil {
		log.Panicln(err)
	}
	var message models.BoardInfoMessage
	err = json.NewDecoder(resp.Body).Decode(&message)
	if err != nil {
		log.Panicln(err)
	}
	return message.Print
}

// MakeCLIAgent agent.
func MakeCLIAgent(apiURL url.URL) CLIAgent {
	var agent CLIAgent
	agent.apiURL = apiURL
	agent.doReset()
	return agent
}

func (agent CLIAgent) newAgent(create models.AgentCreateMessage) models.AgentCreatedMessage {
	buffer, err := json.Marshal(create)
	if err != nil {
		log.Panicln(err)
	}
	agentURL, err := url.Parse("api/v1.0/agents/")
	if err != nil {
		log.Panicln(err)
	}
	agentURL = agent.apiURL.ResolveReference(agentURL)
	resp, err := http.Post(agentURL.String(), "text/json; charset=utf-8", bytes.NewReader(buffer))
	if err != nil {
		log.Panicln(err)
	}
	var message models.AgentCreatedMessage
	err = json.NewDecoder(resp.Body).Decode(&message)
	if err != nil {
		log.Panicln(err)
	}
	return message
}

func (agent CLIAgent) doReset() {
	agent.gameURL = nil
	agent.userURL = nil
	agent.piece = nil
	gameURL, err := url.Parse("api/v1.0/games/")
	if err != nil {
		log.Panicln(err)
	}
	gameURL = agent.apiURL.ResolveReference(gameURL)
	resp, err := http.Post(gameURL.String(), "text/json; charset=utf-8", bytes.NewBufferString("{}"))
	if err != nil {
		log.Panicln(err)
	}
	var game models.BoardCreatedMessage
	err = json.NewDecoder(resp.Body).Decode(&game)
	if err != nil {
		log.Panicln(err)
	}
	gameURL, err = url.Parse("api/v1.0/games/" + game.ID.String())
	if err != nil {
		log.Panicln(err)
	}
	agent.gameURL = agent.apiURL.ResolveReference(gameURL)
	player := agent.newAgent(models.AgentCreateMessage{
		GameURL: *gameURL,
		User:    true,
	})
	ai := agent.newAgent(models.AgentCreateMessage{
		Lookahead: 2,
		Delegate:  "max-balance-agent",
	})
	agentURL, err := url.Parse("api/v1.0/agents/" + player.ID.String())
	if err != nil {
		log.Panicln(err)
	}
	agent.userURL = agent.apiURL.ResolveReference(agentURL)
	log.Infoln(ai)
	printCmds()
	printBoard(formatBoard(agent.getInfo()))
}

// Select piece for move.
func (agent CLIAgent) doPiece(col, row string) {
	args := agent.parse(col, row)
	if args == nil {
		agent.printInvalid("piece " + col + " " + row)
		return
	}
	agent.piece = args
	resp, err := http.Get(agent.gameURI())
	if err != nil {
		log.Panicln(err)
	}
	var message models.BoardStateMessage
	err = json.NewDecoder(resp.Body).Decode(&message)
	if err != nil {
		log.Panicln(err)
	}
	if message.End {
		println("game over")
		return
	}
	state := message.State
	piece := state[args[1]][args[0]]
	if piece&1 == 0 {
		agent.printInvalid("piece " + col + " " + row)
		return
	}
	board := strings.Split(agent.getInfo(), "\n")
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
	var message models.UserMoveMessage
	message.Move = [2][2]int{[2]int{agent.piece[1], agent.piece[0]}, [2]int{args[1], args[0]}}
	data, err := json.Marshal(message)
	if err != nil {
		log.Panicln(err)
	}
	req, err := http.NewRequest(http.MethodPut, agent.agentURI(), bytes.NewReader(data))
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
	err = json.NewDecoder(resp.Body).Decode(&boardStateMessage)
	if err != nil {
		log.Panicln(err)
	}
	if boardStateMessage.Invalid {
		println("Invalid move.")
		return
	}
	if boardStateMessage.End {
		printBoard(formatBoard(agent.getInfo()))
		println("you won")
		agent.doReset()
		return
	}
	state := boardStateMessage.State
	nextState := state
	printBoard(formatBoard(agent.getInfo()))
	println("making move ...")
	for state == nextState {
		time.Sleep(2)
		resp, err = http.Get(agent.gameURI())
		if err != nil {
			log.Panicln(err)
		}
		err = json.NewDecoder(resp.Body).Decode(&boardStateMessage)
		if err != nil {
			log.Panicln(err)
		}
		if boardStateMessage.End {
			println("you won")
			agent.doReset()
			return
		}
	}
	printBoard(formatBoard(agent.getInfo()))
}

func (agent CLIAgent) printInvalid(args string) {
	printBoard(formatBoard(agent.getInfo()))
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

// CmdLoop Sanitize data.
func (agent CLIAgent) CmdLoop() {
	for {
		print(prompt)
		var cmd, col, row string
		n, err := fmt.Scanln(&cmd, &col, &row)
		cmd = strings.ToLower(cmd)
		if n == 1 && cmd == "reset" {
			agent.doReset()
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
