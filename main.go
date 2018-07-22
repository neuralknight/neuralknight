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
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	"github.com/jinzhu/gorm"
	// _ "github.com/jinzhu/gorm/dialects/postgres"
	_ "github.com/jinzhu/gorm/dialects/sqlite"
)

const connStr = "postgres://pqgotest:password@localhost/pqgotest?sslmode=verify-full"

func shutdown(srv *http.Server, sigint <-chan os.Signal, idleConnsClosed chan<- struct{}) {
	<-sigint

	// We received an interrupt signal, shut down.
	if err := srv.Shutdown(context.Background()); err != nil {
		// Error from closing listeners, or context timeout:
		log.Printf("HTTP server Shutdown: %v", err)
	}
}

// Main interruptable process.
func Main(sigint <-chan os.Signal, idleConnsClosed chan<- struct{}) {
	defer close(idleConnsClosed)

	var srv http.Server

	go shutdown(&srv, sigint, idleConnsClosed)

	db, err := gorm.Open("sqlite3", "chess.db")
	if err != nil {
		log.Panicln("failed to connect database", err, connStr)
	}

	db.DB().SetMaxIdleConns(10)
	db.DB().SetMaxOpenConns(100)
	db.DB().SetConnMaxLifetime(time.Hour)

	srv.Handler = Handler{}

	if err := srv.ListenAndServe(); err != http.ErrServerClosed {
		// Error starting or closing listener:
		log.Printf("HTTP server ListenAndServe: %v", err)
	}
}

func main() {
	sigint := make(chan os.Signal, 1)
	idleConnsClosed := make(chan struct{})
	signal.Notify(sigint, os.Interrupt)
	go Main(sigint, idleConnsClosed)
	<-idleConnsClosed
}
