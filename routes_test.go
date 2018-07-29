package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
)

var (
	client   *http.Client
	endpoint string
)

func logError(res *http.Response) {
	defer func() {
		if err := recover(); err != nil {
			log.Println(err)
		}
	}()
	buffer, err := ioutil.ReadAll(res.Body)
	if err != nil {
		log.Panicln("logError read all:", err)
	}
	var message ErrorMessage
	err = json.Unmarshal(buffer, &message)
	if err != nil {
		log.Panicln("logError unmarshal:", err)
	}
	log.Println(message.Error)
	switch extra := message.Extra.(type) {
	case error:
		log.Println("logError extra type error", extra.Error())
	case string:
		log.Println("logError extra type string", extra)
	case nil:
		log.Println("logError extra nil")
	default:
		log.Println("logError extra type unknown", extra)
	}
}

func generateGame(t *testing.T) uuid.UUID {
	res, err := client.Post(endpoint+"/api/v1.0/games", "text/json; charset=utf-8", nil)
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	if res.StatusCode != 201 {
		logError(res)
		t.Fatal("Games model response code:", res.StatusCode)
	}
	if res.Header.Get("Content-Type") != "text/json; charset=utf-8" {
		t.Fatal("Games model Content-Type:", res.Header.Get("Content-Type"))
	}
	buffer, err := ioutil.ReadAll(res.Body)
	if err != nil {
		t.Fatal("Games read all:", err)
	}
	var message models.BoardCreatedMessage
	err = json.Unmarshal(buffer, &message)
	if err != nil {
		t.Fatal("Games unmarshal:", err)
	}
	if len(message.ID.Bytes()) == 0 {
		t.Fatal("Games uuid len: 0")
	}
	if message.ID.Version() != uuid.V5 {
		t.Fatal("Games uuid Version:", message.ID.Version())
	}
	return message.ID
}

func TestServeHTTPBadURL(t *testing.T) {
	res, err := client.Get(endpoint + "/foo")
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	logError(res)
	if res.StatusCode != 404 {
		t.Fatal("Fake url response code:", res.StatusCode)
	}
}

func TestServeHTTPIndex(t *testing.T) {
	res, err := client.Get(endpoint + "")
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	logError(res)
	if res.StatusCode != 404 {
		t.Fatal("Index response code:", res.StatusCode)
	}
}

func TestServeHTTPNoModel(t *testing.T) {
	res, err := client.Get(endpoint + "/api/v1.0/")
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	logError(res)
	if res.StatusCode != 404 {
		t.Fatal("No model response code:", res.StatusCode)
	}
}

func TestServeHTTPGetGames(t *testing.T) {
	res, err := client.Get(endpoint + "/api/v1.0/games")
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		logError(res)
		t.Fatal("Games model response code:", res.StatusCode)
	}
	if res.Header.Get("Content-Type") != "text/json; charset=utf-8" {
		t.Fatal("Games model Content-Type:", res.Header.Get("Content-Type"))
	}
	buffer, err := ioutil.ReadAll(res.Body)
	if err != nil {
		t.Fatal("Games read all:", err)
	}
	var message models.BoardStatesMessage
	err = json.Unmarshal(buffer, &message)
	if err != nil {
		t.Fatal("Games unmarshal:", err)
	}
}

func TestServeHTTPPostGames(t *testing.T) {
	ID := generateGame(t)
	res, err := client.Get(endpoint + "/api/v1.0/games/" + ID.String())
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		logError(res)
		t.Fatal("Games model response code:", res.StatusCode)
	}
	if res.Header.Get("Content-Type") != "text/json; charset=utf-8" {
		t.Fatal("Games model Content-Type:", res.Header.Get("Content-Type"))
	}
	buffer, err := ioutil.ReadAll(res.Body)
	if err != nil {
		t.Fatal("Games read all:", err)
	}
	var response models.BoardStateMessage
	err = json.Unmarshal(buffer, &response)
	if err != nil {
		t.Fatal("Games unmarshal:", err)
	}
	log.Println(response)
}

func TestServeHTTPPutGames(t *testing.T) {
	req, err := http.NewRequest(http.MethodPut, endpoint+"/api/v1.0/games/", nil)
	if err != nil {
		t.Fatal(err)
	}
	res, err := client.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	logError(res)
	if res.StatusCode != 404 {
		t.Fatal("Games model response code:", res.StatusCode)
	}
}

func TestServeHTTPDeleteGames(t *testing.T) {
	req, err := http.NewRequest(http.MethodDelete, endpoint+"/api/v1.0/games/", nil)
	if err != nil {
		t.Fatal(err)
	}
	res, err := client.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	logError(res)
	if res.StatusCode != 404 {
		t.Fatal("Games model response code:", res.StatusCode)
	}
}

func TestServeHTTPGetAgents(t *testing.T) {
	res, err := client.Get(endpoint + "/api/v1.0/agents/")
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	logError(res)
	if res.StatusCode != 404 {
		t.Fatal("Agents model response code:", res.StatusCode)
	}
}

func TestServeHTTPPostAgents(t *testing.T) {
	res, err := client.Post(endpoint+"/api/v1.0/agents/", "text/json; charset=utf-8", nil)
	if err != nil {
		t.Fatal(err)
	}
	logError(res)
	if res.StatusCode != 400 {
		t.Fatal("Agents model response code:", res.StatusCode)
	}
}

func TestServeHTTPPutAgents(t *testing.T) {
	req, err := http.NewRequest(http.MethodPut, endpoint+"/api/v1.0/agents/", nil)
	if err != nil {
		t.Fatal(err)
	}
	res, err := client.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	logError(res)
	if res.StatusCode != 404 {
		t.Fatal("Agents model response code:", res.StatusCode)
	}
}

func TestServeHTTPDeleteAgents(t *testing.T) {
	req, err := http.NewRequest(http.MethodDelete, endpoint+"/api/v1.0/agents/", nil)
	if err != nil {
		t.Fatal(err)
	}
	res, err := client.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	logError(res)
	if res.StatusCode != 404 {
		t.Fatal("Agents model response code:", res.StatusCode)
	}
}

func TestMain(m *testing.M) {
	srv := httptest.NewTLSServer(Handler{})
	client = srv.Client()
	endpoint = srv.URL
	code := m.Run()
	srv.Close()
	os.Exit(code)
}
