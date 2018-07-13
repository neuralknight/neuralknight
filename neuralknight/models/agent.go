package neuralknightmodels

import (
	"bytes"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"

	"github.com/satori/go.uuid"
)

// Agent agent.
type Agent interface {
	PlayRound(w http.ResponseWriter, r *http.Request)
	GetState(w http.ResponseWriter, r *http.Request)
}

// Slayer of chess
type simpleAgent struct {
	apiURL           url.URL
	port             int
	agentID          uuid.UUID
	delegate         baseAgent
	gameID           uuid.UUID
	gameOver         bool
	lookahead        int
	player           int
	requestCount     int
	requestCountData int
}

// AgentPool agent.
var AgentPool = make(map[uuid.UUID]Agent)

type agentCreateResponse struct {
	AgentID string
}

type agentCreateMessage struct {
	user      bool
	gameID    string
	player    int
	lookahead int
	delegate  string
}

// MakeAgent agent.
func MakeAgent(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	var agent simpleAgent
	var message agentCreateMessage
	json.NewDecoder(r.Body).Decode(message)
	gameID, err := uuid.FromString(message.gameID)
	if err != nil {
		panic(err)
	}
	var port = os.Getenv("PORT")
	n, err := fmt.Sscanf(port, "%d", &agent.port)
	if err != nil || n == 0 {
		agent.port = 8080
	}
	agent.agentID = uuid.Must(uuid.NewV4())
	agent.gameID = gameID
	agent.player = message.player
	if message.user {
		user := userAgent{agent}
		AgentPool[user.agentID] = user
		resp := user.joinGame()
		defer resp.Body.Close()
		json.NewEncoder(w).Encode(agentCreateResponse{user.agentID.String()})
		return
	}
	agent.delegate = agents[message.delegate]
	agent.lookahead = message.lookahead
	AgentPool[agent.agentID] = agent
	resp := agent.joinGame()
	defer resp.Body.Close()
	json.NewEncoder(w).Encode(agentCreateResponse{agent.agentID.String()})
}

// GetAgent agent.
func getAgent(agentID uuid.UUID) Agent {
	agent, err := AgentPool[agentID]
	if !err {
		panic(err)
	}
	return agent
}

// Close agent.
func (agent simpleAgent) close(w http.ResponseWriter, r *http.Request) {
	delete(AgentPool, agent.agentID)
}

// getBoards agent.
func (agent simpleAgent) getBoards(cursor *uuid.UUID) *http.Response {
	params := url.Values{"lookahead": {}}
	if cursor != nil {
		params.Add("cursor", cursor.String())
	}
	path, err := url.Parse("v1.0/games/" + agent.gameID.String() + "/states?" + params.Encode())
	if err != nil {
		panic(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	resp, err := http.Get(apiURL.RequestURI())
	if err != nil {
		panic(err)
	}
	return resp
}

type cursorMessage struct {
	cursor string
	boards [][8]string
}

func (agent simpleAgent) getBoardsCursorOne(boards chan<- board, cursor *uuid.UUID) *uuid.UUID {
	boardOptions := agent.getBoards(cursor)
	defer boardOptions.Body.Close()
	var message cursorMessage
	err := json.NewDecoder(boardOptions.Body).Decode(message)
	if err != nil {
		panic(err)
	}
	for _, b := range message.boards {
		var out board
		for i, r := range b {
			row, err := hex.DecodeString(r)
			if err != nil {
				panic(err)
			}
			if len(row) != 8 {
				panic(row)
			}
			copy(out[i][:], row)
		}
		boards <- out
	}
	if message.cursor != "" {
		cur, err := uuid.FromString(message.cursor)
		if err != nil {
			panic(err)
		}
		return &cur
	}
	return nil
}

// getBoardsCursor agent.
func (agent simpleAgent) getBoardsCursor() <-chan board {
	boards := make(chan board)
	go func() {
		cursor := agent.getBoardsCursorOne(boards, nil)
		for cursor != nil {
			cursor = agent.getBoardsCursorOne(boards, cursor)
		}
		close(boards)
	}()
	return boards
}

// stateMessage models.
type stateMessage struct {
	end, invalid bool
	state        [8]string
}

// GetState Gets current board state.
func (agent simpleAgent) GetState(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	message := agent.getState()
	err := json.NewEncoder(w).Encode(message)
	if err != nil {
		panic(err)
	}
}

// GetState Gets current board state.
func (agent simpleAgent) getState() stateMessage {
	if agent.gameOver {
		var message stateMessage
		message.end = true
		return message
	}
	path, err := url.Parse("v1.0/games/" + agent.gameID.String())
	if err != nil {
		panic(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	resp, err := http.Get(apiURL.RequestURI())
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	var message stateMessage
	err = json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		panic(err)
	}
	return message
}

func (agent simpleAgent) joinGame() *http.Response {
	var json = make(map[string]uuid.UUID, 1)
	json["id"] = agent.agentID
	resp, err := http.PostForm(agent.apiURL.EscapedPath(), url.Values{"id": {agent.agentID.String()}})
	if err != nil {
		panic(err)
	}
	return resp
}

// PlayRound Play a game round
func (agent simpleAgent) PlayRound(w http.ResponseWriter, r *http.Request) {
	println(agent.requestCount, agent.requestCountData)
	resp := agent.putBoard(agent.delegate.playRound(agent.getBoardsCursor()))
	defer resp.Body.Close()
	var message stateMessage
	err := json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		panic(err)
	}
	agent.gameOver = message.end
	if agent.gameOver {
		agent.close(w, r)
	}
	if message.invalid {
		agent.PlayRound(w, r)
		return
	}
}

type playMessage struct{ state [8]string }

// Sends move selection to board state manager
func (agent simpleAgent) putBoard(board board) *http.Response {
	path, err := url.Parse("v1.0/games/" + agent.gameID.String())
	if err != nil {
		panic(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	var message playMessage
	for i, r := range board {
		message.state[i] = hex.EncodeToString(r[:])
	}
	data, err := json.Marshal(message)
	if err != nil {
		panic(err)
	}
	req, err := http.NewRequest(http.MethodPut, apiURL.RequestURI(), bytes.NewReader(data))
	if err != nil {
		panic(err)
	}
	defer req.Body.Close()
	var client http.Client
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	return resp
}
