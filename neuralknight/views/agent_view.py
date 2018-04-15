import requests
from pyramid.view import view_config
from ../models/board_evaluation import evaluate_boards

@view_config(route_name="agent")
def agent_view(request):

    return {}
