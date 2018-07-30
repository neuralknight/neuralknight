package views

import (
	"encoding/json"
	"net/http"
	"regexp"
	"strings"

	log "github.com/sirupsen/logrus"

	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
)

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
func ServeAPIGamesHTTP(path string, method string, decoder *json.Decoder) interface{} {
	if routerV1Games.MatchString(path) {
		return serveAPIGamesListHTTP(method, decoder)
	}
	if routerV1GamesID.MatchString(path) {
		return serveAPIGamesIDHTTP(models.GetGame(viewID(path, extractV1GamesID, "")), method, decoder)
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

func serveAPIGamesIDHTTP(game models.Board, method string, decoder *json.Decoder) interface{} {
	switch method {
	case http.MethodGet:
		return game.GetState(decoder)
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
