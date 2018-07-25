package main

import (
	"encoding/json"
	"log"
	"net/http"
	"regexp"

	"github.com/neuralknight/neuralknight/views"
)

// Handler neuralknight
type Handler struct{}

// ErrorMessage neuralknight
type ErrorMessage struct {
	Error string
	Extra interface{}
}

var routerV1 = regexp.MustCompile("^api/v1.0/")
var routerV1Games = regexp.MustCompile("^api/v1.0/games")
var routerV1Agents = regexp.MustCompile("^api/v1.0/agents")

func (f Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	defer func() {
		if err := recover(); err != nil {
			http.Error(w, "", http.StatusInternalServerError)
			encoder := json.NewEncoder(w)
			switch err := err.(type) {
			case error:
				encoder.Encode(ErrorMessage{err.Error(), err})
			case string:
				encoder.Encode(ErrorMessage{err, nil})
			default:
				encoder.Encode(ErrorMessage{"Unhandled error", err})
				log.Println("Unhandled error:", err)
			}
		}
	}()
	if routerV1.MatchString(r.URL.Path) {
		if routerV1Games.MatchString(r.URL.Path) {
			w.Header().Set("Content-Type", "text/json; charset=utf-8")
			views.ServeAPIGamesHTTP(w, r)
			return
		}
		if routerV1Agents.MatchString(r.URL.Path) {
			w.Header().Set("Content-Type", "text/json; charset=utf-8")
			views.ServeAPIAgentsHTTP(w, r)
			return
		}
	}
	http.NotFound(w, r)
}
