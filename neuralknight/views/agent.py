from cornice import Service
from pyramid.httpexceptions import HTTPBadRequest

from ..models import Agent
from ..models import UserAgent

agents = Service(
    name='issue_agent',
    path='/issue-agent',
    description='Create agent')
agent_states = Service(
    name='game_states',
    path='/agent/{agent_id}',
    description='Agent states')


@agents.post()
def issue_agent_view(request):
    try:
        json = dict(request.json)
        if json.pop('user', False):
            return {'agent_id': UserAgent(**json).agent_id}
        return {'agent_id': Agent(**json).agent_id}
    except Exception:
        pass
    raise HTTPBadRequest


@agent_states.get()
def get_agent_view(request):
    agent_id = request.matchdict['agent_id']
    try:
        agent = Agent.get_agent(agent_id)
    except KeyError:
        return {'end': True, 'state': {'end': True}}

    return {'state': agent.get_state()}


@agent_states.put()
def put_agent_view(request):
    agent_id = request.matchdict['agent_id']
    try:
        agent = Agent.get_agent(agent_id)
    except KeyError:
        return {'end': True, 'state': {'end': True}}

    if request.json.get('end', False):
        return agent.close()
    if isinstance(agent, UserAgent):
        return agent.play_round(request.json.get('move', None))
    return agent.play_round()
