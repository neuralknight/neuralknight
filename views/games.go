package views

import (
	"log"
	"net/http"
	"regexp"
	"strings"

	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
)

func viewID(r *http.Request, re *regexp.Regexp, suffix string) uuid.UUID {
	ID, err := uuid.FromString(strings.Trim(strings.TrimSuffix(strings.Trim(re.FindString(r.URL.Path), "/"), suffix), "/"))
	if err != nil {
		log.Panicln(err)
	}
	return ID
}

var routerV1Games = regexp.MustCompile("^api/v1.0/games/?$")
var routerV1GamesID = regexp.MustCompile("^api/v1.0/games/[\\w-]+/?$")
var extractV1GamesID = regexp.MustCompile("(?:/)[\\w-]+(?:/?)$")
var routerV1GamesIDStates = regexp.MustCompile("^api/v1.0/games/[\\w-]+/states/?$")
var extractV1GamesIDStates = regexp.MustCompile("(?:/)[\\w-]+(?:/states/?)$")
var routerV1GamesIDInfo = regexp.MustCompile("^api/v1.0/games/[\\w-]+/info/?$")
var extractV1GamesIDInfo = regexp.MustCompile("(?:/)[\\w-]+(?:/info/?)$")

// ServeAPIGamesHTTP views.
func ServeAPIGamesHTTP(r *http.Request) interface{} {
	if routerV1Games.MatchString(r.URL.Path) {
		return serveAPIGamesListHTTP(r)
	}
	if routerV1GamesID.MatchString(r.URL.Path) {
		return serveAPIGamesIDHTTP(r)
	}
	if routerV1GamesIDStates.MatchString(r.URL.Path) {
		return serveAPIGamesIDStatesHTTP(r)
	}
	if routerV1GamesIDInfo.MatchString(r.URL.Path) {
		return serveAPIGamesIDInfoHTTP(r)
	}
	return nil
}

func serveAPIGamesListHTTP(r *http.Request) interface{} {
	switch r.Method {
	case http.MethodGet:
		return models.GetGames(r)
	case http.MethodPost:
		return models.MakeGame(r)
	}
	return nil
}

func serveAPIGamesIDHTTP(r *http.Request) interface{} {
	game := models.GetGame(viewID(r, extractV1GamesID, ""))
	switch r.Method {
	case http.MethodGet:
		return game.GetState(r)
	case http.MethodPost:
		return game.AddPlayer(r)
	case http.MethodPut:
		return game.PlayRound(r)
	}
	return nil
}

func serveAPIGamesIDStatesHTTP(r *http.Request) interface{} {
	game := models.GetGame(viewID(r, extractV1GamesIDStates, "states"))
	switch r.Method {
	case http.MethodGet:
		return game.GetStates(r)
	}
	return nil
}

func serveAPIGamesIDInfoHTTP(r *http.Request) interface{} {
	game := models.GetGame(viewID(r, extractV1GamesIDInfo, "info"))
	switch r.Method {
	case http.MethodGet:
		return game.GetInfo(r)
	}
	return nil
}
