import json

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config

from ..models import Agent


@view_config(route_name='issue_agent', request_method='POST', renderer='json')
def issue_agent_view(request):
    try:
        game_id = request.POST['id']
    except KeyError:
        return HTTPBadRequest()

    return Response(body=json.dumps({'agent_id': Agent(game_id).agent_id}), status_code=200)


@view_config(route_name='agent', request_method='PUT', renderer='json')
def agent_view(request):
    agent_id = request.matchdict['agent_id']
    Agent.AGENT_POOL[agent_id].play_round()

    return Response()
