import os
from pyramid.config import Configurator

testapp = None


def main(global_config, **settings):
    """
    Return a Pyramid WSGI application.
    """
    if os.environ.get('DATABASE_URL', ''):
        settings['sqlalchemy.url'] = os.environ['DATABASE_URL']
    else:
        settings['sqlalchemy.url'] = 'postgres://localhost:5432/neuralknight'
    if os.environ.get('PORT', ''):
        settings['listen'] = '*:' + os.environ['PORT']
    else:
        settings['listen'] = 'localhost:54321'
    config = Configurator(settings=settings)
    config.include('cornice')
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    # config.include('.security')
    config.scan()
    return config.make_wsgi_app()
