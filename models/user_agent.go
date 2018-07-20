package models

import (
	"encoding/hex"
	"encoding/json"
	"io"
	"log"
	"net/http"
)

// UserAgent Human Agent
type userAgent struct {
	simpleAgent
}

// UserMoveMessage Human Agent
type UserMoveMessage struct {
	Move [2][2]int
}

func getMove(r io.Reader) [2][2]int {
	var message UserMoveMessage
	err := json.NewDecoder(r).Decode(message)
	if err != nil {
		log.Panicln(err)
	}
	return message.Move
}

// PlayRound Play a game round
func (agent userAgent) PlayRound(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	move := getMove(r.Body)
	proposal := agent.getState()
	if proposal.End {
		json.NewEncoder(w).Encode(proposal)
		return
	}
	var out board
	for i, r := range proposal.State {
		row, err := hex.DecodeString(r)
		if err != nil {
			log.Panicln(err)
		}
		if len(row) != 8 {
			log.Panicln(row)
		}
		copy(out[i][:], row)
	}
	out[move[1][0]][move[1][1]] = out[move[0][0]][move[0][1]]
	out[move[0][0]][move[0][1]] = 0
	resp := agent.putBoard(out)
	defer resp.Body.Close()
	var message BoardStateMessage
	err := json.NewDecoder(resp.Body).Decode(message)
	if err != nil {
		log.Panicln(err)
	}
	agent.gameOver = message.End
	if agent.gameOver {
		agent.close(w, r)
		return
	}
	json.NewEncoder(w).Encode(message)
}
