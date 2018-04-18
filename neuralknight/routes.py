def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('issue_agent', '/issue-agent')
    config.add_route('issue_agent_lookahead', '/issue-agent-lookahead')
    config.add_route('agent', '/agent/{agent_id}')
