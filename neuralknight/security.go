from os import environ

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated, Everyone
from pyramid.session import SignedCookieSessionFactory


class PyramidStocksRoot:
    def __init__(self, request):
        """
        Initialize for access control.
        """
        self.request = request

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'secret'),
    ]


def includeme(config):
    auth_secret = environ.get(
        'AUTH_SECRET',
        '\x85v\xaf\xf9:3I\x0c\x98\x80\xec\x9e\xe3\xd4\xee\xba\xdfst\xb5')
    authz_policy = ACLAuthorizationPolicy()
    authn_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg='sha512',
    )

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('view')
    config.set_root_factory(PyramidStocksRoot)

    session_secret = environ.get(
        'SESSION_SECRET',
        '\xc0\xa37\xc6\x15\xb4B7\x16\xe9\xaa[^<`\x7f;p\x18\x1f')
    session_factory = SignedCookieSessionFactory(session_secret)

    config.set_session_factory(session_factory)
    config.set_default_csrf_options(require_csrf=True)
