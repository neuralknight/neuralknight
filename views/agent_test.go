package views_test

import (
	. "gopkg.in/check.v1"
)

type AgentSuite struct{}

var _ = Suite(&AgentSuite{})

func (s *AgentSuite) TestAgentView(c *C) {

}

// from pyramid.httpexceptions import HTTPBadRequest
//
// from ..views.agent import issue_agent_view
//
//
// def test_issue_agent_bad_request(dummy_post_request):
//     """Test request without proper query string"""
//     assert isinstance(issue_agent_view(dummy_post_request), HTTPBadRequest)
