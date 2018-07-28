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

// NotFoundMessage neuralknight
type NotFoundMessage struct{}

// ErrorMessage neuralknight
type ErrorMessage struct {
	Error string
	Extra interface{}
}

var routerV1 = regexp.MustCompile("^api/v1.0/")
var routerV1Games = regexp.MustCompile("^api/v1.0/games")
var routerV1Agents = regexp.MustCompile("^api/v1.0/agents")

func (f Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	encoder := json.NewEncoder(w)
	defer func() {
		if err := recover(); err != nil {
			switch err := err.(type) {
			case error:
				w.WriteHeader(http.StatusInternalServerError)
				encoder.Encode(ErrorMessage{err.Error(), err})
			case string:
				w.WriteHeader(http.StatusBadRequest)
				encoder.Encode(ErrorMessage{err, nil})
			default:
				w.WriteHeader(http.StatusInternalServerError)
				encoder.Encode(ErrorMessage{"Unhandled error", err})
				log.Println("Unhandled error:", err)
			}
		}
	}()
	var message interface{}
	if routerV1.MatchString(r.URL.Path) {
		if routerV1Games.MatchString(r.URL.Path) {
			message = views.ServeAPIGamesHTTP(r)
		}
		if routerV1Agents.MatchString(r.URL.Path) {
			message = views.ServeAPIAgentsHTTP(r)
		}
	}
	if message == nil {
		w.WriteHeader(http.StatusNotFound)
		message = NotFoundMessage{}
	} else {
		switch r.Method {
		case http.MethodPost:
			w.WriteHeader(http.StatusCreated)
		default:
			w.WriteHeader(http.StatusOK)
		}
	}
	err := encoder.Encode(message)
	if err != nil {
		log.Println(err)
	}
}
