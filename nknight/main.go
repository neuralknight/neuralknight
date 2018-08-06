package main

import (
	"flag"
	"net/url"

	"github.com/neuralknight/neuralknight/nknight/nknight"
	log "github.com/sirupsen/logrus"
)

func main() {
	defer func() {
		switch err := recover().(type) {
		case error:
			log.Println(err.Error())
		default:
			break
		}
	}()
	Main()
}

// Main entry.
func Main() {
	apiURLFlag := flag.String("api_url", "http://localhost:8080", "api_url")
	flag.Parse()
	if apiURLFlag == nil {
		log.Panicln("Failed to parse flags")
	}
	CmdLoop(*apiURLFlag)
}

// CmdLoop entry.
func CmdLoop(apiURLFlag string) {
	apiURL, err := url.Parse(apiURLFlag)
	if err != nil {
		log.Panicln(err)
	}
	nknight.MakeCLIAgent(*apiURL).CmdLoop()
}
