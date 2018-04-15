from os import environ
from pyramid.config import Configurator


def main(global_config, **settings):
    """
    Return a Pyramid WSGI application.
    """
    if 'DATABASE_URL' in environ:
        settings['sqlalchemy.url'] = environ['DATABASE_URL']
    config = Configurator(settings=settings)
    config.include('cornice')
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    # config.include('.security')
    config.scan()
    return config.make_wsgi_app()
