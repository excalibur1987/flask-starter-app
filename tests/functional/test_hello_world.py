"""
This file (test_hello_world.py) contains the functional tests for the `hello_world` blueprint.

These tests use GETs and POSTs to different URLs to check for the proper behavior
of the `hello_world` blueprint.
"""


def test_hello_world(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/hello-world' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get("/hello-world")
    assert response.status_code == 200
