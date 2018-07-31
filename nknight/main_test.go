package main_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	nknight "github.com/neuralknight/neuralknight/nknight"
	"github.com/neuralknight/neuralknight/views"
	. "gopkg.in/check.v1"
)

func Test(t *testing.T) { TestingT(t) }

type NKnightSuite struct {
	srv      *httptest.Server
	client   *http.Client
	endpoint string
}

var _ = Suite(&NKnightSuite{})

func (s *NKnightSuite) TestMainEntry(c *C) {
	nknight.MakeCLIAgent(nil).CmdLoop()
}

func (s *NKnightSuite) SetUpSuite(c *C) {
	s.srv = httptest.NewServer(views.Handler{})
	s.client = s.srv.Client()
	s.endpoint = s.srv.URL
}

func (s *NKnightSuite) SetUpTest(c *C) {}

func (s *NKnightSuite) TearDownTest(c *C) {}

func (s *NKnightSuite) TearDownSuite(c *C) {
	s.srv.Close()
}
