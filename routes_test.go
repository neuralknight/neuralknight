package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestServeHTTPBadURL(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodGet, "url", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	var w httptest.ResponseRecorder
	handler.ServeHTTP(&w, r)
	if w.Code != 404 {
		t.Fatal("Fake url response code:", w.Code)
	}
}

func TestServeHTTPNoModel(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodGet, "api/v1.0/", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	var w httptest.ResponseRecorder
	handler.ServeHTTP(&w, r)
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

func TestServeHTTPGetAgents(t *testing.T) {
	var handler Handler
	r, err := http.NewRequest(http.MethodGet, "api/v1.0/agents", bytes.NewReader([]byte{}))
	if err != nil {
		t.Fatal(err)
	}
	var w httptest.ResponseRecorder
	handler.ServeHTTP(&w, r)
	if w.Code != 404 {
		t.Fatal("Agents model response code:", w.Code)
	}
}
