package main

import (
	"flag"
	"net/url"

	log "github.com/sirupsen/logrus"

	"github.com/neuralknight/neuralknight/nkight/nkight"
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
	apiURLFlag := flag.String("api_url", "http://localhost:8080", "api_url")
	flag.Parse()
	if apiURLFlag == nil {
		log.Panicln("Failed to parse flags")
	}
	apiURL, err := url.Parse(*apiURLFlag)
	if err != nil {
		log.Panicln(err)
	}
	nkight.MakeCLIAgent(apiURL).CmdLoop()
}
