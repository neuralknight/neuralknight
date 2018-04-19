from pyramid.httpexceptions import HTTPBadRequest
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
        return {'agent_id': UserAgent(game_id, player).agent_id}
    return {'agent_id': Agent(game_id, player).agent_id}


@view_config(route_name='issue_agent_lookahead', request_method='POST', renderer='json')
def issue_agent_lookahead_view(request):
    try:
        game_id = request.json['id']
        lookahead = request.json['lookahead']
    except KeyError:
        return HTTPBadRequest()
    player = request.json.get('player', 1)
    if 'user' in request.json:
        return {'agent_id': UserAgent(game_id, player).agent_id}
    return {'agent_id': Agent(game_id, player, lookahead).agent_id}


@view_config(route_name='agent', request_method=('PUT', 'GET'), renderer='json')
def agent_view(request):
    agent_id = request.matchdict['agent_id']
    try:
        agent = Agent.get_agent(agent_id)
    except KeyError:
        if request.method == 'GET':
            return {'state': {'end': True}}
        return {}

    if request.method == 'GET':
        return {'state': agent.get_state()}
    if request.json.get('end', False):
        return agent.close()
    if isinstance(agent, UserAgent):
        return agent.play_round(request.json.get('move', None))
    return agent.play_round()
