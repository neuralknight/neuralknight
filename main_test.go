package main

import (
	"net/http"
	"os"
	"testing"
	"time"
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

func TestInteruptMain(t *testing.T) {
	sigint := make(chan os.Signal, 1)
	idleConnsClosed := make(chan struct{})
	go Main(sigint, idleConnsClosed)
	sigint <- os.Interrupt
	<-idleConnsClosed
	close(sigint)
}

func TestMainEntry(t *testing.T) {
	go main()
	time.Sleep(time.Microsecond * 10)
}
