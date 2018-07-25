package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/satori/go.uuid"
)

func TestServeHTTPBadURL(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodGet, "foo", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	handler.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Fake url response code:", w.Code)
	}
}

func TestServeHTTPIndex(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodGet, "", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	handler.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Index response code:", w.Code)
	}
}

func TestServeHTTPNoModel(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodGet, "api/v1.0/", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	handler.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("No model response code:", w.Code)
	}
}

func TestServeHTTPGetGames(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodGet, "api/v1.0/games", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, r)
	if w.Code != 200 {
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
	var handler Handler
	r, err := http.NewRequest(http.MethodPost, "api/v1.0/games", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, r)
	if w.Code != 201 {
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
	var message struct{ ID uuid.UUID }
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
}

func TestServeHTTPPutGames(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodPut, "api/v1.0/games", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	handler.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Games model response code:", w.Code)
	}
}

func TestServeHTTPDeleteGames(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodDelete, "api/v1.0/games", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	handler.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Games model response code:", w.Code)
	}
}

func TestServeHTTPGetAgents(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodGet, "api/v1.0/agents", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	handler.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Agents model response code:", w.Code)
	}
}

func TestServeHTTPPostAgents(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodPost, "api/v1.0/agents", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, r)
	if w.Code != 400 {
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
}

func TestServeHTTPPutAgents(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodPut, "api/v1.0/agents", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	handler.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Agents model response code:", w.Code)
	}
}

func TestServeHTTPDeleteAgents(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodDelete, "api/v1.0/agents", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	w := httptest.NewRecorder()
	defer w.Result().Body.Close()
	handler.ServeHTTP(w, r)
	if w.Code != 404 {
		t.Fatal("Agents model response code:", w.Code)
	}
}
