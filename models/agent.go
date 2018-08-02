package models

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/url"
	"time"

	log "github.com/sirupsen/logrus"

	"github.com/satori/go.uuid"
)

// Agent agent.
type Agent interface {
	PlayRound(decoder *json.Decoder) BoardStateMessage
	GetState(decoder *json.Decoder) BoardStateMessage
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
	Lookahead int
}

// AgentCreatedMessage model.
type AgentCreatedMessage struct {
	ID uuid.UUID
}

// AgentCreateMessage model.
type AgentCreateMessage struct {
	User      bool
	GameURL   url.URL
	Lookahead int
	Delegate  string
}

// PlayMessage agent
type PlayMessage struct {
	State board
}

func (agent agentModel) gameURI(input string) string {
	path, err := url.Parse(input)
	if err != nil {
		log.Panicln(err)
	}
	return agent.GameURL.ResolveReference(path).String()
}

// MakeAgent agent.
func MakeAgent(decoder *json.Decoder) AgentCreatedMessage {
	db := openDB()
	defer closeDB(db)
	var agent agentModel
	var message AgentCreateMessage
	err := decoder.Decode(&message)
	if err != nil {
		log.Panicln(err)
	}
	agent.ID = uuid.NewV5(uuid.NamespaceOID, "chess.agent")
	agent.GameURL = message.GameURL
	if message.User {
		agent.Delegate = "user-agent"
	} else {
		agent.Delegate = message.Delegate
	}
	agent.Lookahead = message.Lookahead
	db.Create(&agent)
	agent.joinGame()
	return AgentCreatedMessage{agent.ID}
}

// GetAgent agent.
func GetAgent(ID uuid.UUID) Agent {
	db := openDB()
	defer closeDB(db)
	var agent agentModel
	rows, err := db.First(&agent, "id = ?", ID).Rows()
	if err != nil {
		log.Panicln(err)
	}
	if agent.ID != ID {
		log.Panicln(agent)
	}
	if !rows.Next() {
		log.Panicln(ID)
	}
	err = rows.Scan(&agent.ID)
	if err != nil {
		log.Panicln(err)
	}
	return agent
}

// getBoards agent.
func (agent agentModel) getBoards(cursor uuid.UUID) cursorMessage {
	params := url.Values{"lookahead": {}, "cursor": {cursor.String()}}
	resp, err := http.Get(agent.gameURI("states?" + params.Encode()))
	if err != nil {
		log.Panicln(err)
	}
	defer resp.Body.Close()
	var message cursorMessage
	err = json.NewDecoder(resp.Body).Decode(&message)
	if err != nil {
		log.Panicln(err)
	}
	return message
}

type cursorMessage struct {
	cursor uuid.UUID
	boards []board
}

func (agent agentModel) getBoardsCursorOne(boards chan<- board, cursor uuid.UUID) uuid.UUID {
	message := agent.getBoards(cursor)
	for _, b := range message.boards {
		boards <- b
	}
	return message.cursor
}

// getBoardsCursor agent.
func (agent agentModel) getBoardsCursor() <-chan board {
	boards := make(chan board)
	go func() {
		cursor := agent.getBoardsCursorOne(boards, uuid.UUID{})
		for cursor.Version() == uuid.V5 {
			cursor = agent.getBoardsCursorOne(boards, cursor)
		}
		close(boards)
	}()
	return boards
}

// GetState Gets current board state.
func (agent agentModel) GetState(decoder *json.Decoder) BoardStateMessage {
	resp, err := http.Get(agent.gameURI(""))
	if err != nil {
		log.Panicln(err)
	}
	defer resp.Body.Close()
	var message BoardStateMessage
	err = json.NewDecoder(resp.Body).Decode(&message)
	if err != nil {
		log.Panicln(err)
	}
	return message
}

func (agent agentModel) joinGame() {
	buffer, err := json.Marshal(GameJoinMessage{})
	if err != nil {
		log.Panicln(err)
	}
	resp, err := http.Post(agent.GameURL.String(), "text/json; charset=utf-8", bytes.NewReader(buffer))
	if err != nil {
		log.Panicln(err)
	}
	defer resp.Body.Close()
	var message BoardStateMessage
	err = json.NewDecoder(resp.Body).Decode(&message)
	if err != nil {
		log.Panicln(err)
	}
}

// PlayRound Play a game round
func (agent agentModel) PlayRound(decoder *json.Decoder) BoardStateMessage {
	db := openDB()
	defer closeDB(db)
	if agent.Delegate == "user-agent" {
		return userAgentDelegate{}.playRound(decoder, agent, db)
	}
	return agent.playRound()
}

// PlayRound Play a game round
func (agent agentModel) playRound() BoardStateMessage {
	delegate, ok := agents[agent.Delegate]
	if !ok {
		log.Panicln("No agent found to play game: ", agent.Delegate)
	}
	message := agent.putBoard(delegate.playRound(agent.getBoardsCursor()))
	if message.Invalid && !message.End {
		return agent.playRound()
	}
	return message
}

// Sends move selection to board state manager
func (agent agentModel) putBoard(board board) BoardStateMessage {
	data, err := json.Marshal(PlayMessage{board})
	if err != nil {
		log.Panicln(err)
	}
	req, err := http.NewRequest(http.MethodPut, agent.gameURI(""), bytes.NewReader(data))
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
	var message BoardStateMessage
	err = json.NewDecoder(resp.Body).Decode(&message)
	if err != nil {
		log.Panicln(err)
	}
	return message
}
