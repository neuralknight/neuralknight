package models

import (
	"bytes"
	"encoding/hex"
	"encoding/json"
	"log"
	"net/http"
	"net/url"

	"github.com/jinzhu/gorm"
	"github.com/satori/go.uuid"
)

// Agent agent.
type Agent interface {
	PlayRound(w http.ResponseWriter, r *http.Request)
	GetState(w http.ResponseWriter, r *http.Request)
}

const connStr = "postgres://pqgotest:password@localhost/pqgotest?sslmode=verify-full"

// Slayer of chess
type simpleAgent struct {
	gorm.Model
	apiURL           url.URL
	agentID          uuid.UUID
	delegate         baseAgent
	gameID           uuid.UUID
	gameOver         bool
	lookahead        int
	player           int
	requestCount     int
	requestCountData int
}

// AgentCreateResponse model.
type AgentCreateResponse struct {
	AgentID string
}

// AgentCreateMessage model.
type AgentCreateMessage struct {
	User      bool
	GameID    string
	Player    int
	Lookahead int
	Delegate  string
}

// MakeAgent agent.
func MakeAgent(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	db, err := gorm.Open("postgres", connStr)
	if err != nil {
		log.Panicln("failed to connect database", err, connStr)
	}
	defer db.Close()
	db.AutoMigrate(&simpleAgent{})
	var agent simpleAgent
	var message AgentCreateMessage
	json.NewDecoder(r.Body).Decode(message)
	gameID, err := uuid.FromString(message.GameID)
	if err != nil {
		log.Panicln(err)
	}
	agent.agentID = uuid.Must(uuid.NewV4())
	agent.gameID = gameID
	agent.player = message.Player
	if message.User {
		db.AutoMigrate(&userAgent{})
		user := userAgent{agent}
		db.Create(&user)
		resp := user.joinGame()
		defer resp.Body.Close()
		json.NewEncoder(w).Encode(AgentCreateResponse{user.agentID.String()})
		return
	}
	agent.delegate = agents[message.Delegate]
	agent.lookahead = message.Lookahead
	db.Create(&agent)
	resp := agent.joinGame()
	defer resp.Body.Close()
	json.NewEncoder(w).Encode(AgentCreateResponse{agent.agentID.String()})
}

// GetAgent agent.
func GetAgent(agentID uuid.UUID) Agent {
	db, err := gorm.Open("postgres", connStr)
	if err != nil {
		log.Panicln("failed to connect database", err, connStr)
	}
	defer db.Close()
	var agent simpleAgent
	db.First(&agent, "agentID = ?", agentID.String())
	if agent.agentID != agentID {
		var user userAgent
		db.First(&user, "agentID = ?", agentID.String())
		if user.agentID != agentID {
			log.Panicln(agent)
		}
		return user
	}
	return agent
}

// Close agent.
func (agent simpleAgent) close(w http.ResponseWriter, r *http.Request) {
	db, err := gorm.Open("postgres", connStr)
	if err != nil {
		log.Panicln("failed to connect database", err, connStr)
	}
	defer db.Close()
	db.Model(&agent).Update("gameOver", true)
}

// getBoards agent.
func (agent simpleAgent) getBoards(cursor *uuid.UUID) *http.Response {
	params := url.Values{"lookahead": {}}
	if cursor != nil {
		params.Add("cursor", cursor.String())
	}
	path, err := url.Parse("v1.0/games/" + agent.gameID.String() + "/states?" + params.Encode())
	if err != nil {
		log.Panicln(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	resp, err := http.Get(apiURL.RequestURI())
	if err != nil {
		log.Panicln(err)
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
		log.Panicln(err)
	}
	for _, b := range message.boards {
		var out board
		for i, r := range b {
			row, err := hex.DecodeString(r)
			if err != nil {
				log.Panicln(err)
			}
			if len(row) != 8 {
				log.Panicln(row)
			}
			copy(out[i][:], row)
		}
		boards <- out
	}
	if message.cursor != "" {
		cur, err := uuid.FromString(message.cursor)
		if err != nil {
			log.Panicln(err)
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

// GetState Gets current board state.
func (agent simpleAgent) GetState(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	message := agent.getState()
	err := json.NewEncoder(w).Encode(message)
	if err != nil {
		log.Panicln(err)
	}
}

// GetState Gets current board state.
func (agent simpleAgent) getState() BoardStateMessage {
	if agent.gameOver {
		var message BoardStateMessage
		message.End = true
		return message
	}
	path, err := url.Parse("v1.0/games/" + agent.gameID.String())
	if err != nil {
		log.Panicln(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	resp, err := http.Get(apiURL.RequestURI())
	if err != nil {
		log.Panicln(err)
	}
	defer resp.Body.Close()
	var message BoardStateMessage
	err = json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		log.Panicln(err)
	}
	return message
}

func (agent simpleAgent) joinGame() *http.Response {
	var json = make(map[string]uuid.UUID, 1)
	json["id"] = agent.agentID
	resp, err := http.PostForm(agent.apiURL.EscapedPath(), url.Values{"id": {agent.agentID.String()}})
	if err != nil {
		log.Panicln(err)
	}
	return resp
}

// PlayRound Play a game round
func (agent simpleAgent) PlayRound(w http.ResponseWriter, r *http.Request) {
	println(agent.requestCount, agent.requestCountData)
	resp := agent.putBoard(agent.delegate.playRound(agent.getBoardsCursor()))
	defer resp.Body.Close()
	var message BoardStateMessage
	err := json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		log.Panicln(err)
	}
	agent.gameOver = message.End
	if agent.gameOver {
		agent.close(w, r)
	}
	if message.Invalid {
		agent.PlayRound(w, r)
		return
	}
}

type playMessage struct{ state [8]string }

// Sends move selection to board state manager
func (agent simpleAgent) putBoard(board board) *http.Response {
	path, err := url.Parse("v1.0/games/" + agent.gameID.String())
	if err != nil {
		log.Panicln(err)
	}
	apiURL := agent.apiURL.ResolveReference(path)
	var message playMessage
	for i, r := range board {
		message.state[i] = hex.EncodeToString(r[:])
	}
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
	return resp
}
