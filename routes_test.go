package main

import (
	"bytes"
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
	var w httptest.ResponseRecorder
	handler.ServeHTTP(&w, r)
	if w.Code != 404 {
		t.Fatal("No model response code:", w.Code)
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
		t.Fatal("No model response code:", w.Code)
	}
}
