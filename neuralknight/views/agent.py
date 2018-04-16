import requests
from pyramid.view import view_config
from uuid import uuid
from ..models import agent

agent_game_map = {}

@view_config(route_name='issue_agent')
def issue_agent_view(request):
    if request.method == 'POST':
        game_id = request.POST['id']
        agent_id = uuid()
        agent_game_map[agent_id] = game_id

        return {'agent_id': agent_id}

@view_config(route_name='agent')
def agent_view(request):
    if request.method == 'PUT':
        agent_id = request.matchdict['agent_id']
        game_id = agent_game_map[agent_id]
        agent.play_round(game_id)

        return {}
