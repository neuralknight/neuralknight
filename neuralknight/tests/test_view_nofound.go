def test_default_behavior_of_home_view(dummy_request):
    from ..views.home import home_view

    response = home_view(dummy_request)
    assert dummy_request.response.status_code == 200
    assert isinstance(response, dict)
    assert response == {}


def test_not_found_behavior(dummy_request):
    from ..views.notfound import notfound_view

    response = notfound_view(dummy_request)
    assert dummy_request.response.status_code == 404
    assert isinstance(response, dict)
    assert response == {}
