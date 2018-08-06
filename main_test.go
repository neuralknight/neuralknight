package main

import (
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	_ "github.com/jinzhu/gorm/dialects/sqlite"
	log "github.com/sirupsen/logrus"
	. "gopkg.in/check.v1"
)

func Test(t *testing.T) { TestingT(t) }

type NKnightSuite struct {
	srv      *httptest.Server
	client   *http.Client
	endpoint string
}

var _ = Suite(&NKnightSuite{})

func (s *NKnightSuite) TestShutdown(c *C) {
	sigint := make(chan os.Signal, 1)
	idleConnsClosed := make(chan struct{})
	var srv http.Server
	go shutdown(&srv, sigint, idleConnsClosed)
	sigint <- os.Interrupt
	<-idleConnsClosed
	close(sigint)
}

func (s *NKnightSuite) TestListenAndServe(c *C) {
	sigint := make(chan os.Signal, 1)
	idleConnsClosed := make(chan struct{})
	go listenAndServe(":3000", sigint, idleConnsClosed)
	select {
	case res := <-idleConnsClosed:
		log.Panicln(res)
	case <-time.After(1 * time.Second):
		sigint <- os.Interrupt
		<-idleConnsClosed
	}
	close(sigint)
}

func (s *NKnightSuite) TestMainEntry(c *C) {
	go main()
	<-time.After(1 * time.Second)
}
