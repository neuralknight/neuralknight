import pytest
from pyramid.httpexceptions import HTTPBadRequest
from neuralknight.views.agent import issue_agent_view, agent_view

def test_issue_agent_bad_request(dummy_post_request):
    '''Test request without proper query string'''
    assert isinstance(issue_agent_view(dummy_post_request), HTTPBadRequest)

#def test_issue_agent_
