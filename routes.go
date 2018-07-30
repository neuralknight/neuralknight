package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"regexp"

	log "github.com/sirupsen/logrus"

	"github.com/neuralknight/neuralknight/views"
)

// Handler neuralknight
type Handler struct{}

// ErrorMessage neuralknight
type ErrorMessage struct {
	Error string
	Extra interface{}
}

var routerV1 = regexp.MustCompile("^/api/v1.0/")
var routerV1Games = regexp.MustCompile("^/api/v1.0/games")
var routerV1Agents = regexp.MustCompile("^/api/v1.0/agents")

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
		log.Infoln(err)
	}
	log.Infoln("Request body: ", string(buffer))
	reader := bytes.NewReader(buffer)
	var message interface{}
	if routerV1.MatchString(r.URL.Path) {
		if routerV1Games.MatchString(r.URL.Path) {
			message = views.ServeAPIGamesHTTP(r.URL.Path, r.Method, json.NewDecoder(reader))
		}
		if routerV1Agents.MatchString(r.URL.Path) {
			message = views.ServeAPIAgentsHTTP(r.URL.Path, r.Method, json.NewDecoder(reader))
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
