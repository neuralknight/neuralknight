package nknight_test

import (
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"

	"github.com/neuralknight/neuralknight/views"
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

func (s *NKnightSuite) TestMainEntry(c *C) {
	defer func() {
		switch err := recover().(type) {
		case error:
			log.Println(err.Error())
		default:
			break
		}
	}()
	apiURL, err := url.Parse(s.endpoint)
	c.Assert(err, Not(NotNil))
	nknight.MakeCLIAgent(apiURL).CmdLoop()
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
