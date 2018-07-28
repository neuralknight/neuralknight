package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/jinzhu/gorm"
	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
)

func logError(w *httptest.ResponseRecorder) {
	defer func() {
		if err := recover(); err != nil {
		}
	}()
	defer w.Result().Body.Close()
	buffer, err := ioutil.ReadAll(w.Result().Body)
	if err != nil {
		log.Panicln("Agents read all:", err)
	}
	var message ErrorMessage
	err = json.Unmarshal(buffer, &message)
	if err != nil {
		log.Panicln("Agents unmarshal:", err)
	}
	log.Println(message.Error)
	switch extra := message.Extra.(type) {
	case error:
		log.Panicln("Error extra type error", extra.Error())
	case string:
		log.Panicln("Error extra type string", extra)
	case nil:
		log.Panicln("Error extra nil")
	default:
		log.Panicln("Error extra type unknown", extra)
	}
}

func generateGame(t *testing.T) uuid.UUID {
	r, err := http.NewRequest(http.MethodPost, "api/v1.0/games", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 201 {
		logError(w)
		t.Fatal("Games model response code:", w.Code)
	}
	if w.Header().Get("Content-Type") != "text/json; charset=utf-8" {
		t.Fatal("Games model Content-Type:", w.Header().Get("Content-Type"))
	}
	defer w.Result().Body.Close()
	buffer, err := ioutil.ReadAll(w.Result().Body)
	if err != nil {
		t.Fatal("Games read all:", err)
	}
	var message models.BoardCreatedMessage
	err = json.Unmarshal(buffer, &message)
	if err != nil {
		t.Fatal("Games unmarshal:", err)
	}
	if len(message.ID.Bytes()) == 0 {
		t.Fatal("Games uuid len: 0")
	}
	if message.ID.Version() != uuid.V5 {
		t.Fatal("Games uuid Version:", message.ID.Version())
	}
	return message.ID
}

func TestServeHTTPBadURL(t *testing.T) {
	r, err := http.NewRequest(http.MethodGet, "foo", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Fake url response code:", w.Code)
	}
}

func TestServeHTTPIndex(t *testing.T) {
	r, err := http.NewRequest(http.MethodGet, "", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Index response code:", w.Code)
	}
}

func TestServeHTTPNoModel(t *testing.T) {
	r, err := http.NewRequest(http.MethodGet, "api/v1.0/", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("No model response code:", w.Code)
	}
}

func TestServeHTTPGetGames(t *testing.T) {
	r, err := http.NewRequest(http.MethodGet, "api/v1.0/games", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 200 {
		logError(w)
		t.Fatal("Games model response code:", w.Code)
	}
	if w.Header().Get("Content-Type") != "text/json; charset=utf-8" {
		t.Fatal("Games model Content-Type:", w.Header().Get("Content-Type"))
	}
	defer w.Result().Body.Close()
	buffer, err := ioutil.ReadAll(w.Result().Body)
	if err != nil {
		t.Fatal("Games read all:", err)
	}
	var response []struct{}
	err = json.Unmarshal(buffer, &response)
	if err != nil {
		t.Fatal("Games unmarshal:", err)
	}
	if len(response) != 0 {
		t.Fatal("Games unmarshal:", response)
	}
}

func TestServeHTTPPostGames(t *testing.T) {
	ID := generateGame(t)
	r, err := http.NewRequest(http.MethodGet, "api/v1.0/games/"+ID.String(), bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 200 {
		logError(w)
		t.Fatal("Games model response code:", w.Code)
	}
	if w.Header().Get("Content-Type") != "text/json; charset=utf-8" {
		t.Fatal("Games model Content-Type:", w.Header().Get("Content-Type"))
	}
	defer w.Result().Body.Close()
	buffer, err := ioutil.ReadAll(w.Result().Body)
	if err != nil {
		t.Fatal("Games read all:", err)
	}
	var response models.BoardStateMessage
	err = json.Unmarshal(buffer, &response)
	if err != nil {
		t.Fatal("Games unmarshal:", err)
	}
	log.Println(response.State)
}

func TestServeHTTPPutGames(t *testing.T) {
	r, err := http.NewRequest(http.MethodPut, "api/v1.0/games", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Games model response code:", w.Code)
	}
}

func TestServeHTTPDeleteGames(t *testing.T) {
	r, err := http.NewRequest(http.MethodDelete, "api/v1.0/games", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Games model response code:", w.Code)
	}
}

func TestServeHTTPGetAgents(t *testing.T) {
	r, err := http.NewRequest(http.MethodGet, "api/v1.0/agents", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Agents model response code:", w.Code)
	}
}

func TestServeHTTPPostAgents(t *testing.T) {
	r, err := http.NewRequest(http.MethodPost, "api/v1.0/agents", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 400 {
		logError(w)
		t.Fatal("Agents model response code:", w.Code)
	}
	defer w.Result().Body.Close()
	buffer, err := ioutil.ReadAll(w.Result().Body)
	if err != nil {
		t.Fatal("Agents read all:", err)
	}
	var message ErrorMessage
	err = json.Unmarshal(buffer, &message)
	if err != nil {
		t.Fatal("Agents unmarshal:", err)
	}
	if len(message.Error) == 0 {
		t.Fatal("Agents error len: 0")
	}
	switch extra := message.Extra.(type) {
	case error:
		t.Fatal("Agents extra type error")
	case string:
		t.Fatal("Agents extra type string", extra)
	case nil:
		break
	default:
		t.Fatal("Agents extra type unknown", extra)
	}
}

func TestServeHTTPPutAgents(t *testing.T) {
	r, err := http.NewRequest(http.MethodPut, "api/v1.0/agents", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Agents model response code:", w.Code)
	}
}

func TestServeHTTPDeleteAgents(t *testing.T) {
	r, err := http.NewRequest(http.MethodDelete, "api/v1.0/agents", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	Handler{}.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Agents model response code:", w.Code)
	}
}

func TestMain(m *testing.M) {
	sigint := make(chan os.Signal, 1)
	idleConnsClosed := make(chan struct{})
	go listenAndServe(":3000", sigint, idleConnsClosed)
	code := m.Run()
	sigint <- os.Interrupt
	<-idleConnsClosed
	close(sigint)
	db, _ := gorm.Open("sqlite3", "chess.db")
	db.DropTableIfExists("agent_models", "board_models")
	if errors := db.GetErrors(); len(errors) != 0 {
		panic(errors)
	}
	os.Exit(code)
}
