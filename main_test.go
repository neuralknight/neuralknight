package main

import (
	"os"
	"testing"
)

func TestInteruptMain(t *testing.T) {
	sigint := make(chan os.Signal, 1)
	idleConnsClosed := make(chan struct{})
	go Main(sigint, idleConnsClosed)
	sigint <- os.Interrupt
	close(sigint)
	<-idleConnsClosed
}

func TestMain(t *testing.T) {
	go main()
}
