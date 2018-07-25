package views

import (
	"encoding/json"
	"log"
	"net/http"
	"regexp"

	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
)

var routerV1Agents = regexp.MustCompile("^api/v1.0/agents/?$")
var routerV1AgentsID = regexp.MustCompile("^api/v1.0/agents/[\\w-]+/?$")
var extractV1AgentsID = regexp.MustCompile("(?:/)[\\w-]+(?:/?)$")

// ServeAPIAgentsHTTP views.
func ServeAPIAgentsHTTP(w http.ResponseWriter, r *http.Request) {
	if routerV1Agents.MatchString(r.URL.Path) {
		serveAPIAgentsListHTTP(w, r)
		return
	}
	if routerV1AgentsID.MatchString(r.URL.Path) {
		serveAPIAgentsIDHTTP(w, r)
		return
	}
	http.NotFound(w, r)
}

func serveAPIAgentsListHTTP(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodPost:
		message := models.MakeAgent(r)
		w.WriteHeader(http.StatusCreated)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	default:
		http.NotFound(w, r)
	}
}

func serveAPIAgentsIDHTTP(w http.ResponseWriter, r *http.Request) {
	agentID, err := uuid.FromString(extractV1AgentsID.FindString(r.URL.Path))
	if err != nil {
		log.Panicln(err)
	}
	agent := models.GetAgent(agentID)
	switch r.Method {
	case http.MethodGet:
		message := agent.GetState(r)
		w.WriteHeader(http.StatusCreated)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	case http.MethodPut:
		message := agent.PlayRound(r)
		w.WriteHeader(http.StatusCreated)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	default:
		http.NotFound(w, r)
	}
}
