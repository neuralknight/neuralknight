import requests
from pyramid.view import view_config

@view_config(route_name='agent')
def agent_view(request):
    return {}
