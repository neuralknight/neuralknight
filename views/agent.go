package views

import (
	"encoding/json"
	"net/http"
	"regexp"

	"github.com/neuralknight/neuralknight/models"
)

var routerV1Agents = regexp.MustCompile("^/api/v1.0/agents/?$")
var routerV1AgentsID = regexp.MustCompile("^/api/v1.0/agents/[\\w-]+/?$")
var extractV1AgentsID = regexp.MustCompile("(?:/)[\\w-]+(?:/?)$")

// ServeAPIAgentsHTTP views.
func ServeAPIAgentsHTTP(path string, method string, decoder *json.Decoder) interface{} {
	if routerV1Agents.MatchString(path) {
		return serveAPIAgentsListHTTP(method, decoder)
	}
	if routerV1AgentsID.MatchString(path) {
		return serveAPIAgentsIDHTTP(models.GetAgent(viewID(path, extractV1AgentsID, "")), method, decoder)
	}
	return nil
}

func serveAPIAgentsListHTTP(method string, decoder *json.Decoder) interface{} {
	switch method {
	case http.MethodPost:
		return models.MakeAgent(decoder)
	}
	return nil
}

func serveAPIAgentsIDHTTP(agent models.Agent, method string, decoder *json.Decoder) interface{} {
	switch method {
	case http.MethodGet:
		return agent.GetState(decoder)
	case http.MethodPut:
		return agent.PlayRound(decoder)
	}
	return nil
}
