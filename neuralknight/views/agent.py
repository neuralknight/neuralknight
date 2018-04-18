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


@view_config(route_name='agent', request_method=('PUT', 'GET'), renderer='json')
def agent_view(request):
    agent_id = request.matchdict['agent_id']
    agent = Agent.AGENT_POOL[agent_id]

    if request.method == 'GET':
        return {'state': agent.get_state()}
    else:
        if isinstance(agent, UserAgent):
            agent.play_round(request.json['move'])
        else:
            agent.play_round()
    return {}
