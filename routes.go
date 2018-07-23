package main

import (
	"log"
	"net/http"
	"regexp"

	"github.com/neuralknight/neuralknight/views"
)

// Handler neuralknight
type Handler struct{}

var routerV1 = regexp.MustCompile("^api/v1.0/")
var routerV1Games = regexp.MustCompile("^api/v1.0/games")
var routerV1Agents = regexp.MustCompile("^api/v1.0/agents")

func (f Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	defer func() {
		if err := recover(); err != nil {
			switch err := err.(type) {
			case error:
				http.Error(w, err.Error(), http.StatusInternalServerError)
			case string:
				http.Error(w, err, http.StatusInternalServerError)
			default:
				http.Error(w, "Unhandled error", http.StatusInternalServerError)
				log.Println("Unhandled error:", err)
			}
		}
	}()
	if routerV1.MatchString(r.URL.Path) {
		if routerV1Games.MatchString(r.URL.Path) {
			views.ServeAPIGamesHTTP(w, r)
			w.Header().Set("Content-Type", "text/json; charset=utf-8")
			w.WriteHeader(200)
			return
		}
		if routerV1Agents.MatchString(r.URL.Path) {
			views.ServeAPIAgentsHTTP(w, r)
			w.Header().Set("Content-Type", "text/json; charset=utf-8")
			w.WriteHeader(200)
			return
		}
	}
	http.NotFound(w, r)
}
