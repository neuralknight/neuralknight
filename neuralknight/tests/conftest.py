from os import environ
from pyramid.testing import DummyRequest, setUp, tearDown
from pytest import fixture

from ..models.board import Board
from ..models.meta import Base


@fixture
def configuration(request):
    """
    Create database models for testing purposes.
    """
    config = setUp(settings={
        'sqlalchemy.url': environ.get(
            'TEST_DATABASE_URL', 'postgres://localhost:5432/testing_neuralknight')
    })
    config.include('neuralknight.models')
    config.include('neuralknight.routes')
    yield config
    tearDown()


@fixture
def db_session(configuration, request):
    """
    Create a database session for interacting with the test database.
    """
    SessionFactory = configuration.registry['dbsession_factory']
    session = SessionFactory()
    engine = session.bind
    Base.metadata.create_all(engine)
    yield session
    session.transaction.rollback()
    Base.metadata.drop_all(engine)


@fixture
def dummy_request(db_session):
    """
    Create a dummy GET request with a dbsession.
    """
    return DummyRequest(dbsession=db_session)


@fixture
def dummy_post_request(db_session):
    """
    Create a dummy POST request with a dbsession.
    """
    return DummyRequest(dbsession=db_session, post={}, json={})


@fixture(scope="session")
def testapp(request):
    """
    Functional test for app to support mocking.
    """
    import neuralknight
    from webtest import TestApp

    app = neuralknight.main({}, **{
        'sqlalchemy.url': environ.get(
            'TEST_DATABASE_URL', 'postgres://localhost:5432/testing_neuralknight')
    })

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.create_all(bind=engine)
    neuralknight.testapp = TestApp(app)
    yield neuralknight.testapp
    Base.metadata.drop_all(bind=engine)


@fixture
def start_board():
    return Board()


@fixture
def pawn_capture_board():
    return Board(tuple(map(bytes, [
        [12, 6, 2, 10, 4, 2, 6, 12],
        [8, 8, 8, 0, 8, 0, 8, 8],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 8, 0, 8, 0, 0],
        [0, 0, 0, 0, 9, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [9, 9, 9, 9, 0, 9, 9, 9],
        [13, 7, 3, 11, 5, 3, 7, 13]])))


@fixture
def min_pawn_board():
    return Board(tuple(map(bytes, [
        [0, 0, 0, 0, 4, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 9, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 5, 0, 0, 0]])))


@fixture
def end_game_board():
    return Board(tuple(map(bytes, [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 4, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 11, 0],
        [0, 0, 0, 5, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]])))
