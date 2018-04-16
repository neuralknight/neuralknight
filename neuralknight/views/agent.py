import requests
from pyramid.view import view_config
from uuid import uuid4
from ..models import agent
from pyramid.response import Response
import json
from pyramid.httpexceptions import HTTPBadRequest
from ..models import Agent
from ..models import AGENT_POOL


@view_config(route_name='issue_agent', request_method='POST', renderer='json')
def issue_agent_view(request):
    try:
        game_id = request.POST['id']
    except KeyError:
        return HTTPBadRequest()

    agent = Agent(game_id)
    AGENT_POOL[agent.agent_id] = agent

    return Response(body=json.dumps({'agent_id': agent.agent_id}), status_code=200)


@view_config(route_name='agent', request_method='PUT', renderer='json')
def agent_view(request):
    agent_id = request.matchdict['agent_id']
    AGENT_POOL[agent_id].play_round()

    return Response()
