package views_test

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"github.com/neuralknight/neuralknight/models"
	"github.com/neuralknight/neuralknight/views"
	"github.com/satori/go.uuid"
	log "github.com/sirupsen/logrus"
	. "gopkg.in/check.v1"
)

func (s *RoutesSuite) logError(res *http.Response) {
	defer func() {
		if err := recover(); err != nil {
			log.Println(err)
		}
	}()
	buffer, err := ioutil.ReadAll(res.Body)
	if err != nil {
		log.Panicln("logError read all:", err)
	}
	var message views.ErrorMessage
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

func (s RoutesSuite) makeURLString(input string) string {
	srvURL, err := url.Parse(s.srv.URL)
	if err != nil {
		log.Panicln(err)
	}
	uriURL, err := url.Parse(input)
	if err != nil {
		log.Panicln(err)
	}
	uriURL = srvURL.ResolveReference(uriURL)
	return uriURL.String()
}

func (s *RoutesSuite) generateGame(c *C) uuid.UUID {
	res, err := s.client.Post(s.makeURLString("api/v1.0/games"), "text/json; charset=utf-8", nil)
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 201)
	c.Assert(res.Header.Get("Content-Type"), Equals, "text/json; charset=utf-8")
	buffer, err := ioutil.ReadAll(res.Body)
	c.Assert(err, Not(NotNil))
	var message models.BoardCreatedMessage
	err = json.Unmarshal(buffer, &message)
	c.Assert(err, Not(NotNil))
	c.Assert(len(message.ID.Bytes()), Not(Equals), 0)
	c.Assert(message.ID.Version(), Equals, uuid.V5)
	return message.ID
}

func (s *RoutesSuite) addAgent(c *C, gameID uuid.UUID) uuid.UUID {
	res, err := s.client.Post(s.makeURLString("api/v1.0/agents"), "text/json; charset=utf-8", nil)
	c.Assert(err, Not(NotNil))
	c.Assert(res.StatusCode, Equals, 400)
	var message models.AgentCreatedMessage
	return message.ID
}

func (s *RoutesSuite) TestServeHTTPBadURL(c *C) {
	res, err := s.client.Get(s.makeURLString("foo"))
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPIndex(c *C) {
	res, err := s.client.Get(s.endpoint)
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPNoModel(c *C) {
	res, err := s.client.Get(s.makeURLString("api/v1.0/"))
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPGetGames(c *C) {
	res, err := s.client.Get(s.makeURLString("api/v1.0/games"))
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 200)
	c.Assert(res.Header.Get("Content-Type"), Equals, "text/json; charset=utf-8")
	buffer, err := ioutil.ReadAll(res.Body)
	c.Assert(err, Not(NotNil))
	var message models.BoardStatesMessage
	err = json.Unmarshal(buffer, &message)
	c.Assert(err, Not(NotNil))
	c.Assert(len(message.Games), Equals, 0)
}

func (s *RoutesSuite) TestServeHTTPPostGames(c *C) {
	ID := s.generateGame(c)
	res, err := s.client.Get(s.makeURLString("api/v1.0/games/" + ID.String()))
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 200)
	c.Assert(res.Header.Get("Content-Type"), Equals, "text/json; charset=utf-8")
	buffer, err := ioutil.ReadAll(res.Body)
	c.Assert(err, Not(NotNil))
	var response models.BoardStateMessage
	err = json.Unmarshal(buffer, &response)
	c.Assert(err, Not(NotNil))
	log.Println(response)
}

func (s *RoutesSuite) TestServeHTTPPutGames(c *C) {
	req, err := http.NewRequest(http.MethodPut, s.makeURLString("api/v1.0/games"), nil)
	c.Assert(err, Not(NotNil))
	res, err := s.client.Do(req)
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPDeleteGames(c *C) {
	req, err := http.NewRequest(http.MethodDelete, s.makeURLString("api/v1.0/games"), nil)
	c.Assert(err, Not(NotNil))
	res, err := s.client.Do(req)
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPGetAgents(c *C) {
	res, err := s.client.Get(s.makeURLString("api/v1.0/agents"))
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPPostAgents(c *C) {
	message := models.AgentCreateMessage{}
	message.User = true
	gameID := s.generateGame(c)
	gameURL, err := url.Parse(s.makeURLString("api/v1.0/games/" + gameID.String()))
	c.Assert(err, Not(NotNil))
	message.GameURL = *gameURL
	buffer, err := json.Marshal(message)
	c.Assert(err, Not(NotNil))
	res, err := s.client.Post(s.makeURLString("api/v1.0/agents"), "text/json; charset=utf-8", bytes.NewReader(buffer))
	c.Assert(err, Not(NotNil))
	s.logError(res)
	c.Assert(res.StatusCode, Equals, 201)
}

func (s *RoutesSuite) TestServeHTTPPutAgents(c *C) {
	req, err := http.NewRequest(http.MethodPut, s.makeURLString("api/v1.0/agents"), nil)
	c.Assert(err, Not(NotNil))
	res, err := s.client.Do(req)
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPDeleteAgents(c *C) {
	req, err := http.NewRequest(http.MethodDelete, s.makeURLString("api/v1.0/agents"), nil)
	c.Assert(err, Not(NotNil))
	res, err := s.client.Do(req)
	c.Assert(err, Not(NotNil))
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func Test(t *testing.T) { TestingT(t) }

type RoutesSuite struct {
	srv      *httptest.Server
	client   *http.Client
	endpoint string
}

var _ = Suite(&RoutesSuite{})

func (s *RoutesSuite) SetUpSuite(c *C) {
	s.srv = httptest.NewServer(views.Handler{})
	s.client = s.srv.Client()
	s.endpoint = s.srv.URL
}

func (s *RoutesSuite) SetUpTest(c *C) {}

func (s *RoutesSuite) TearDownTest(c *C) {
	db, _ := gorm.Open("sqlite3", "chess.db")
	db = db.Begin()
	defer db.Commit()
	db.DropTableIfExists("game_models", "agent_models")
}

func (s *RoutesSuite) TearDownSuite(c *C) {
	s.srv.Close()
}
