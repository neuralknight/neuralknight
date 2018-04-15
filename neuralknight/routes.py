def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('games', '/games')
    config.add_route('game_states', '/games/{game}/states')
    config.add_route('issue_agent', '/issue-agent')
    config.add_route('agent', '/agent/{agent_id}')
