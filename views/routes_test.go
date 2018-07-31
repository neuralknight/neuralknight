package views_test

import (
	"bytes"
	"encoding/json"
	"io"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"

	. "gopkg.in/check.v1"

	"github.com/neuralknight/neuralknight/models"
	"github.com/neuralknight/neuralknight/views"
	"github.com/satori/go.uuid"
	log "github.com/sirupsen/logrus"
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

func (s *RoutesSuite) generateGame(c *C) uuid.UUID {
	res, err := s.client.Post(s.endpoint+"/api/v1.0/games", "text/json; charset=utf-8", nil)
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 201)
	c.Assert(res.Header.Get("Content-Type"), Equals, "text/json; charset=utf-8")
	buffer, err := ioutil.ReadAll(res.Body)
	c.Assert(err, NotNil)
	var message models.BoardCreatedMessage
	err = json.Unmarshal(buffer, &message)
	c.Assert(err, NotNil)
	c.Assert(len(message.ID.Bytes()), Not(Equals), 0)
	c.Assert(message.ID.Version(), Equals, uuid.V5)
	return message.ID
}

func (s *RoutesSuite) addAgent(c *C, gameID uuid.UUID) uuid.UUID {
	res, err := s.client.Post(s.endpoint+"/api/v1.0/agents/", "text/json; charset=utf-8", nil)
	c.Assert(err, NotNil)
	c.Assert(res.StatusCode, Equals, 400)
	var message models.AgentCreatedMessage
	return message.ID
}

func (s *RoutesSuite) TestServeHTTPBadURL(c *C) {
	res, err := s.client.Get(s.endpoint + "/foo")
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPIndex(c *C) {
	res, err := s.client.Get(s.endpoint)
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPNoModel(c *C) {
	res, err := s.client.Get(s.endpoint + "/api/v1.0/")
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPGetGames(c *C) {
	res, err := s.client.Get(s.endpoint + "/api/v1.0/games")
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 200)
	c.Assert(res.Header.Get("Content-Type"), Equals, "text/json; charset=utf-8")
	buffer, err := ioutil.ReadAll(res.Body)
	c.Assert(err, NotNil)
	var message models.BoardStatesMessage
	err = json.Unmarshal(buffer, &message)
	c.Assert(err, NotNil)
}

func (s *RoutesSuite) TestServeHTTPPostGames(c *C) {
	ID := s.generateGame(c)
	res, err := s.client.Get(s.endpoint + "/api/v1.0/games/" + ID.String())
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 200)
	c.Assert(res.Header.Get("Content-Type"), Equals, "text/json; charset=utf-8")
	buffer, err := ioutil.ReadAll(res.Body)
	c.Assert(err, NotNil)
	var response models.BoardStateMessage
	err = json.Unmarshal(buffer, &response)
	c.Assert(err, NotNil)
	log.Println(response)
}

func (s *RoutesSuite) TestServeHTTPPutGames(c *C) {
	req, err := http.NewRequest(http.MethodPut, s.endpoint+"/api/v1.0/games/", nil)
	c.Assert(err, NotNil)
	res, err := s.client.Do(req)
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPDeleteGames(c *C) {
	req, err := http.NewRequest(http.MethodDelete, s.endpoint+"/api/v1.0/games/", nil)
	c.Assert(err, NotNil)
	res, err := s.client.Do(req)
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPGetAgents(c *C) {
	res, err := s.client.Get(s.endpoint + "/api/v1.0/agents/")
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPPostAgents(c *C) {
	message := models.AgentCreateMessage{}
	message.User = true
	gameID := s.generateGame(c)
	gameURL, err := url.Parse(s.endpoint + "/api/v1.0/games/" + gameID.String())
	c.Assert(err, NotNil)
	message.GameURL = *gameURL
	buffer, err := json.Marshal(message)
	c.Assert(err, NotNil)
	res, err := s.client.Post(s.endpoint+"/api/v1.0/agents/", "text/json; charset=utf-8", bytes.NewReader(buffer))
	c.Assert(err, NotNil)
	s.logError(res)
	c.Assert(res.StatusCode, Equals, 201)
}

func (s *RoutesSuite) TestServeHTTPPutAgents(c *C) {
	req, err := http.NewRequest(http.MethodPut, s.endpoint+"/api/v1.0/agents/", nil)
	c.Assert(err, NotNil)
	res, err := s.client.Do(req)
	c.Assert(err, NotNil)
	defer res.Body.Close()
	c.Assert(res.StatusCode, Equals, 404)
}

func (s *RoutesSuite) TestServeHTTPDeleteAgents(c *C) {
	req, err := http.NewRequest(http.MethodDelete, s.endpoint+"/api/v1.0/agents/", nil)
	c.Assert(err, NotNil)
	res, err := s.client.Do(req)
	c.Assert(err, NotNil)
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

func (s *RoutesSuite) TearDownTest(c *C) {}

func (s *RoutesSuite) TearDownSuite(c *C) {
	s.srv.Close()
}

func (s *RoutesSuite) TestHelloWorld(c *C) {
	c.Assert(42, Equals, "42")
	c.Assert(io.ErrClosedPipe, ErrorMatches, "io: .*on closed pipe")
	c.Check(42, Equals, 42)
}
