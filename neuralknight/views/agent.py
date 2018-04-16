import requests
from pyramid.view import view_config
from uuid import uuid4
from ..models import agent
from pyramid.response import Response
import json
from pyramid.httpexceptions import HTTPBadRequest


agent_game_map = {}


@view_config(route_name='issue_agent', request_method='POST', renderer='json')
def issue_agent_view(request):
    try:
        game_id = request.POST['id']
    except KeyError:
        return HTTPBadRequest()

    agent_id = uuid4()
    agent_game_map[str(agent_id)] = game_id

    return Response(body=json.dumps({'agent_id': str(agent_id)}), status_code=200)


@view_config(route_name='agent', request_method='PUT', renderer='json')
def agent_view(request):
    agent_id = request.matchdict['agent_id']
    game_id = agent_game_map[agent_id]
    agent.play_round(game_id)

    return Response()
