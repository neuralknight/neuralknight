package views

import (
	"encoding/json"
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
func ServeAPIGamesHTTP(w http.ResponseWriter, r *http.Request) {
	if routerV1Games.MatchString(r.URL.Path) {
		serveAPIGamesListHTTP(w, r)
		return
	}
	if routerV1GamesID.MatchString(r.URL.Path) {
		serveAPIGamesIDHTTP(w, r)
		return
	}
	if routerV1GamesIDStates.MatchString(r.URL.Path) {
		serveAPIGamesIDStatesHTTP(w, r)
		return
	}
	if routerV1GamesIDInfo.MatchString(r.URL.Path) {
		serveAPIGamesIDInfoHTTP(w, r)
		return
	}
	http.NotFound(w, r)
}

func serveAPIGamesListHTTP(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		message := models.GetGames(r)
		w.WriteHeader(http.StatusOK)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	case http.MethodPost:
		message := models.MakeGame(r)
		w.WriteHeader(http.StatusCreated)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	default:
		http.NotFound(w, r)
	}
}

func serveAPIGamesIDHTTP(w http.ResponseWriter, r *http.Request) {
	gameID := viewID(r, extractV1GamesID, "")
	game := models.GetGame(gameID)
	switch r.Method {
	case http.MethodGet:
		message := game.GetState(r)
		w.WriteHeader(http.StatusOK)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	case http.MethodPost:
		message := game.AddPlayer(r)
		w.WriteHeader(http.StatusCreated)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	case http.MethodPut:
		message := game.PlayRound(r)
		w.WriteHeader(http.StatusOK)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	default:
		http.NotFound(w, r)
	}
}

func serveAPIGamesIDStatesHTTP(w http.ResponseWriter, r *http.Request) {
	gameID := viewID(r, extractV1GamesIDStates, "states")
	game := models.GetGame(gameID)
	switch r.Method {
	case http.MethodGet:
		message := game.GetStates(r)
		w.WriteHeader(http.StatusOK)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	default:
		http.NotFound(w, r)
	}
}

func serveAPIGamesIDInfoHTTP(w http.ResponseWriter, r *http.Request) {
	gameID := viewID(r, extractV1GamesIDInfo, "info")
	game := models.GetGame(gameID)
	switch r.Method {
	case http.MethodGet:
		message := game.GetInfo(r)
		w.WriteHeader(http.StatusOK)
		err := json.NewEncoder(w).Encode(message)
		if err != nil {
			log.Println(err)
		}
	default:
		http.NotFound(w, r)
	}
}
