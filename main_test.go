package main

import (
	"net/http"
	"os"
	"testing"
)

func TestShutdown(t *testing.T) {
	sigint := make(chan os.Signal, 1)
	idleConnsClosed := make(chan struct{})
	var srv http.Server
	go shutdown(&srv, sigint, idleConnsClosed)
	sigint <- os.Interrupt
	<-idleConnsClosed
	close(sigint)
}

func TestSetupDB(t *testing.T) {
	db := setupDB("sqlite3", "chess.db")
	if db == nil {
		t.Fatal("nil database connection")
	}
	errors := db.DropTableIfExists("test").GetErrors()
	if len(errors) != 0 {
		t.Fatal(errors)
	}
}

func TestInteruptMain(t *testing.T) {
	sigint := make(chan os.Signal, 1)
	idleConnsClosed := make(chan struct{})
	go Main(sigint, idleConnsClosed)
	sigint <- os.Interrupt
	<-idleConnsClosed
	close(sigint)
}

func TestMain(t *testing.T) {
	go main()
}
