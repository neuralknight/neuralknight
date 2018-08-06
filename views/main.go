package views

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/url"
	"regexp"
	"strings"

	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
	log "github.com/sirupsen/logrus"
)

var routerV1Agents = regexp.MustCompile("^/api/v1.0/agents/?$")
var routerV1AgentsID = regexp.MustCompile("^/api/v1.0/agents/[\\w-]+/?$")
var extractV1AgentsID = regexp.MustCompile("(?:/)[\\w-]+(?:/?)$")

// ServeAPIAgentsHTTP views.
func serveAPIAgentsHTTP(path string, method string, decoder *json.Decoder) interface{} {
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

func viewID(path string, re *regexp.Regexp, suffix string) uuid.UUID {
	ID, err := uuid.FromString(strings.Trim(strings.TrimSuffix(strings.Trim(re.FindString(path), "/"), suffix), "/"))
	if err != nil {
		log.Panicln(err)
	}
	return ID
}

var routerV1Games = regexp.MustCompile("^/api/v1.0/games/?$")
var routerV1GamesID = regexp.MustCompile("^/api/v1.0/games/[\\w-]+/?$")
var extractV1GamesID = regexp.MustCompile("(?:/)[\\w-]+(?:/?)$")
var routerV1GamesIDStates = regexp.MustCompile("^/api/v1.0/games/[\\w-]+/states/?$")
var extractV1GamesIDStates = regexp.MustCompile("(?:/)[\\w-]+(?:/states/?)$")
var routerV1GamesIDInfo = regexp.MustCompile("^/api/v1.0/games/[\\w-]+/info/?$")
var extractV1GamesIDInfo = regexp.MustCompile("(?:/)[\\w-]+(?:/info/?)$")

// ServeAPIGamesHTTP views.
func serveAPIGamesHTTP(path string, method string, values url.Values, decoder *json.Decoder) interface{} {
	if routerV1Games.MatchString(path) {
		return serveAPIGamesListHTTP(method, decoder)
	}
	if routerV1GamesID.MatchString(path) {
		return serveAPIGamesIDHTTP(models.GetGame(viewID(path, extractV1GamesID, "")), method, values, decoder)
	}
	if routerV1GamesIDStates.MatchString(path) {
		return serveAPIGamesIDStatesHTTP(models.GetGame(viewID(path, extractV1GamesID, "states")), method, decoder)
	}
	if routerV1GamesIDInfo.MatchString(path) {
		return serveAPIGamesIDInfoHTTP(models.GetGame(viewID(path, extractV1GamesID, "info")), method, decoder)
	}
	return nil
}

func serveAPIGamesListHTTP(method string, decoder *json.Decoder) interface{} {
	switch method {
	case http.MethodGet:
		return models.GetGames(decoder)
	case http.MethodPost:
		return models.MakeGame(decoder)
	}
	return nil
}

func serveAPIGamesIDHTTP(game models.Board, method string, values url.Values, decoder *json.Decoder) interface{} {
	switch method {
	case http.MethodGet:
		return game.GetState(values)
	case http.MethodPost:
		return game.AddPlayer(decoder)
	case http.MethodPut:
		return game.PlayRound(decoder)
	}
	return nil
}

func serveAPIGamesIDStatesHTTP(game models.Board, method string, decoder *json.Decoder) interface{} {
	switch method {
	case http.MethodGet:
		return game.GetStates(decoder)
	}
	return nil
}

func serveAPIGamesIDInfoHTTP(game models.Board, method string, decoder *json.Decoder) interface{} {
	switch method {
	case http.MethodGet:
		return game.GetInfo(decoder)
	}
	return nil
}

// Handler neuralknight
type Handler struct{}

// ErrorMessage neuralknight
type ErrorMessage struct {
	Error string
	Extra interface{}
}

var routerV1 = regexp.MustCompile("^/api/v1.0/")
var routerV1GamesAny = regexp.MustCompile("^/api/v1.0/games")
var routerV1AgentsAny = regexp.MustCompile("^/api/v1.0/agents")

func (f Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	defer func() {
		switch err := recover().(type) {
		case error:
			w.WriteHeader(http.StatusInternalServerError)
			json.NewEncoder(w).Encode(ErrorMessage{err.Error(), err})
		case string:
			w.WriteHeader(http.StatusBadRequest)
			json.NewEncoder(w).Encode(ErrorMessage{err, nil})
		case nil:
			break
		default:
			w.WriteHeader(http.StatusInternalServerError)
			json.NewEncoder(w).Encode(ErrorMessage{"Unhandled error", err})
			log.Println("Unhandled error:", err)
			panic(err)
		}
	}()
	w.Header().Set("Content-Type", "text/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	buffer, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Panicln(err)
	}
	reader := bytes.NewReader(buffer)
	var message interface{}
	if routerV1.MatchString(r.URL.Path) {
		if routerV1GamesAny.MatchString(r.URL.Path) {
			message = serveAPIGamesHTTP(r.URL.Path, r.Method, r.URL.Query(), json.NewDecoder(reader))
		}
		if routerV1AgentsAny.MatchString(r.URL.Path) {
			message = serveAPIAgentsHTTP(r.URL.Path, r.Method, json.NewDecoder(reader))
		}
	}
	if message == nil {
		w.WriteHeader(http.StatusNotFound)
		message = ErrorMessage{"404 page not found", nil}
	} else {
		switch r.Method {
		case http.MethodPost:
			w.WriteHeader(http.StatusCreated)
		default:
			w.WriteHeader(http.StatusOK)
		}
	}
	err = json.NewEncoder(w).Encode(message)
	if err != nil {
		log.Println(err)
	}
}
