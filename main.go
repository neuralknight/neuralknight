// name="neuralknight",
// version="1.0.0",
// description="A Chess-playing AI",
// author="David Snowberger <david.snowberger@fartherout.org>, Shannon Tully, and Adam Grandquist <grandquista@gmail.com>",
// author_email="grandquista@gmail.com",
// url="https://www.github.com/neuralknight/neuralknight",
// license="MIT",
//     "Development Status :: 3 - Alpha",
//     "Intended Audience :: Developers",
//     "Topic :: Games/Entertainment :: Board Games",
//     "Operating System :: OS Independent",
//     "Natural Language :: English",
//     "License :: Freely Distributable",
// keywords="chess entertainment game ai",

package main

import (
	"context"
	"flag"
	"net/http"
	"os"
	"os/signal"

	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"github.com/neuralknight/backend-views"
	log "github.com/sirupsen/logrus"
)

func shutdown(srv *http.Server, sigint <-chan os.Signal, idleConnsClosed chan<- struct{}) {
	defer close(idleConnsClosed)

	<-sigint

	if err := srv.Shutdown(context.Background()); err != nil {
		log.Println("HTTP server Shutdown:", err)
	}
}

func listenAndServe(addr string, sigint <-chan os.Signal, idleConnsClosed chan<- struct{}) {
	var srv http.Server
	go shutdown(&srv, sigint, idleConnsClosed)

	srv.Addr = addr
	srv.Handler = views.Handler{}

	if err := srv.ListenAndServe(); err != http.ErrServerClosed {
		log.Println("HTTP server ListenAndServe:", err)
	}
}

func main() {
	sigint := make(chan os.Signal, 1)
	signal.Notify(sigint, os.Interrupt)
	flag.Parse()
	idleConnsClosed := make(chan struct{})
	go listenAndServe(":8080", sigint, idleConnsClosed)
	<-idleConnsClosed
}
