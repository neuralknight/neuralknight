import json

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config

from ..models import Agent
from ..models import UserAgent


@view_config(route_name='issue_agent', request_method='POST', renderer='json')
def issue_agent_view(request):
    try:
        game_id = request.json['id']
    except KeyError:
        return HTTPBadRequest()
    player = request.json.get('player', 1)
    if 'user' in request.json:
        return Response(body=json.dumps({'agent_id': UserAgent(game_id, player).agent_id}))
    return Response(body=json.dumps({'agent_id': Agent(game_id, player).agent_id}))


@view_config(route_name='agent', request_method=('PUT', 'GET'), renderer='json')
def agent_view(request):
    agent_id = request.matchdict['agent_id']
    agent = Agent.AGENT_POOL[agent_id]

    if request.method == 'GET':
        assert isinstance(agent, UserAgent)
    else:
        if isinstance(agent, UserAgent):
            agent.play_round(request.matchdict['move'])
        else:
            agent.play_round()

    return Response(body=json.dumps({}))
