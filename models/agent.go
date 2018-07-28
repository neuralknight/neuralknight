package models

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"net/url"
	"time"

	"github.com/jinzhu/gorm"
	"github.com/satori/go.uuid"
)

// Agent agent.
type Agent interface {
	PlayRound(r *http.Request) BoardStateMessage
	GetState(r *http.Request) BoardStateMessage
}

const connStr = "postgres://pqgotest:password@localhost/pqgotest?sslmode=verify-full"

// Slayer of chess
type agentModel struct {
	ID        uuid.UUID `gorm:"primary_key"`
	CreatedAt time.Time
	UpdatedAt time.Time
	DeletedAt *time.Time `sql:"index"`
	GameURL   url.URL
	Delegate  string
	GameID    uuid.UUID
	GameOver  bool
	Lookahead int
}

// AgentCreatedMessage model.
type AgentCreatedMessage struct {
	AgentID uuid.UUID
}

// AgentCreateMessage model.
type AgentCreateMessage struct {
	User      bool
	GameID    uuid.UUID
	Lookahead int
	Delegate  string
}

func (agent agentModel) gameURI(path *url.URL) string {
	// gameURL := path.ResolveReference(&agent.GameURL)
	gameURL := agent.GameURL.ResolveReference(path)
	return gameURL.RequestURI()
}

// MakeAgent agent.
func MakeAgent(r *http.Request) AgentCreatedMessage {
	defer r.Body.Close()
	db := openDB()
	defer closeDB(db)
	var agent agentModel
	var message AgentCreateMessage
	json.NewDecoder(r.Body).Decode(message)
	agent.ID = uuid.NewV5(uuid.NamespaceOID, "chess.agent")
	agent.GameID = message.GameID
	agent.GameURL = *r.URL
	if message.User {
		agent.Delegate = "user-agent"
	} else {
		agent.Delegate = message.Delegate
	}
	agent.Lookahead = message.Lookahead
	db.Create(&agent)
	resp := agent.joinGame()
	defer resp.Body.Close()
	return AgentCreatedMessage{agent.ID}
}

// GetAgent agent.
func GetAgent(ID uuid.UUID) Agent {
	db := openDB()
	defer closeDB(db)
	var agent agentModel
	db.First(&agent, "id = ?", ID)
	if agent.ID != ID {
		log.Panicln(agent)
	}
	return agent
}

// Close agent.
func (agent agentModel) close(db *gorm.DB) {
	db.Model(&agent).Update("gameOver", true)
}

// getBoards agent.
func (agent agentModel) getBoards(cursor *uuid.UUID) *http.Response {
	params := url.Values{"lookahead": {}}
	if cursor != nil {
		params.Add("cursor", cursor.String())
	}
	path, err := url.Parse("v1.0/games/" + agent.GameID.String() + "/states?" + params.Encode())
	if err != nil {
		log.Panicln(err)
	}
	resp, err := http.Get(agent.gameURI(path))
	if err != nil {
		log.Panicln(err)
	}
	return resp
}

type cursorMessage struct {
	cursor string
	boards []board
}

func (agent agentModel) getBoardsCursorOne(boards chan<- board, cursor *uuid.UUID) *uuid.UUID {
	boardOptions := agent.getBoards(cursor)
	defer boardOptions.Body.Close()
	var message cursorMessage
	err := json.NewDecoder(boardOptions.Body).Decode(message)
	if err != nil {
		log.Panicln(err)
	}
	for _, b := range message.boards {
		boards <- b
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
func (agent agentModel) getBoardsCursor() <-chan board {
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
func (agent agentModel) GetState(r *http.Request) BoardStateMessage {
	defer r.Body.Close()
	if agent.GameOver {
		var message BoardStateMessage
		message.End = true
		return message
	}
	path, err := url.Parse("v1.0/games/" + agent.GameID.String())
	if err != nil {
		log.Panicln(err)
	}
	resp, err := http.Get(agent.gameURI(path))
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

func (agent agentModel) joinGame() *http.Response {
	var json = make(map[string]uuid.UUID, 1)
	json["id"] = agent.ID
	resp, err := http.PostForm(agent.gameURI(&url.URL{}), url.Values{"id": {agent.ID.String()}})
	if err != nil {
		log.Panicln(err)
	}
	return resp
}

// PlayRound Play a game round
func (agent agentModel) PlayRound(r *http.Request) BoardStateMessage {
	db := openDB()
	defer closeDB(db)
	if agent.Delegate == "user-agent" {
		return userAgentDelegate{}.playRound(r, agent, db)
	}
	delegate := agents[agent.Delegate]
	resp := agent.putBoard(delegate.playRound(agent.getBoardsCursor()))
	defer resp.Body.Close()
	var message BoardStateMessage
	err := json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		log.Panicln(err)
	}
	agent.GameOver = message.End
	if agent.GameOver {
		agent.close(db)
		return BoardStateMessage{}
	}
	if message.Invalid {
		return agent.PlayRound(r)
	}
	return BoardStateMessage{}
}

type playMessage struct{ state board }

// Sends move selection to board state manager
func (agent agentModel) putBoard(board board) *http.Response {
	path, err := url.Parse("v1.0/games/" + agent.GameID.String())
	if err != nil {
		log.Panicln(err)
	}
	data, err := json.Marshal(playMessage{board})
	if err != nil {
		log.Panicln(err)
	}
	req, err := http.NewRequest(http.MethodPut, agent.gameURI(path), bytes.NewReader(data))
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
