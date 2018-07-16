package neuralknightviews

import (
	"net/http"
	"regexp"

	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
)

var routerV1Agents = regexp.MustCompile("^api/v1.0/agents/?$")
var routerV1AgentsID = regexp.MustCompile("^api/v1.0/agents/[\\w-]+/?$")
var extractV1AgentsID = regexp.MustCompile("(?:/)[\\w-]+(?:/?)$")

// ServeAPIAgentsHTTP neuralknightviews.
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
		neuralknightmodels.MakeAgent(w, r)
		return
	}
	http.NotFound(w, r)
}

func serveAPIAgentsIDHTTP(w http.ResponseWriter, r *http.Request) {
	agentID, err := uuid.FromString(extractV1AgentsID.FindString(r.URL.Path))
	if err != nil {
		panic(err)
	}
	agent := neuralknightmodels.AgentPool[agentID]
	switch r.Method {
	case http.MethodGet:
		agent.GetState(w, r)
		return
	case http.MethodPut:
		agent.PlayRound(w, r)
		return
	}
	http.NotFound(w, r)
}
