import json

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config

from ..models import Agent
from ..models import UserAgent


@view_config(route_name='issue_agent', request_method='POST', renderer='json')
def issue_agent_view(request):
    try:
        game_id = request.POST['id']
    except KeyError:
        return HTTPBadRequest()
    if 'user' in request.POST:
        return Response(body=json.dumps({'agent_id': UserAgent(game_id).agent_id}), status_code=200)
    return Response(body=json.dumps({'agent_id': Agent(game_id).agent_id}), status_code=200)


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

    return Response()
