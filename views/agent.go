package views

import (
	"net/http"
	"regexp"

	"github.com/neuralknight/neuralknight/models"
)

var routerV1Agents = regexp.MustCompile("^/api/v1.0/agents/?$")
var routerV1AgentsID = regexp.MustCompile("^/api/v1.0/agents/[\\w-]+/?$")
var extractV1AgentsID = regexp.MustCompile("(?:/)[\\w-]+(?:/?)$")

// ServeAPIAgentsHTTP views.
func ServeAPIAgentsHTTP(r *http.Request) interface{} {
	if routerV1Agents.MatchString(r.URL.Path) {
		return serveAPIAgentsListHTTP(r)
	}
	if routerV1AgentsID.MatchString(r.URL.Path) {
		return serveAPIAgentsIDHTTP(r)
	}
	return nil
}

func serveAPIAgentsListHTTP(r *http.Request) interface{} {
	switch r.Method {
	case http.MethodPost:
		return models.MakeAgent(r)
	}
	return nil
}

func serveAPIAgentsIDHTTP(r *http.Request) interface{} {
	agent := models.GetAgent(viewID(r, extractV1AgentsID, ""))
	switch r.Method {
	case http.MethodGet:
		return agent.GetState(r)
	case http.MethodPut:
		return agent.PlayRound(r)
	}
	return nil
}
