import pytest
from ..views import agent
from pyramid.httpexceptions import HTTPBadRequest


test_issue_agent_bad_request(dummy_post_request):
    '''Test request without proper query string'''
    assert isinstance(issue_agent_view(dummy_post_request), HTTPBadRequest)
