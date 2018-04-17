from neuralknight.views.agent import issue_agent_view
from pyramid.httpexceptions import HTTPBadRequest


def test_issue_agent_bad_request(dummy_post_request):
    '''Test request without proper query string'''
    assert isinstance(issue_agent_view(dummy_post_request), HTTPBadRequest)
