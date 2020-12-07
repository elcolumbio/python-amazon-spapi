import pytest
from pydantic import ValidationError
from spapi import setup


def test_invalid_params():
    """Validation of params."""
    with pytest.raises(ValidationError):
        setup.AccessTokenRequest(params={
            'grant_type': 'refresh_token',
            'refresh_token': 'example1',
            'client_id': 'example2',
            'client_secret': None
        })


def test_required_params():
    """Validation and completeness of params with overwriting."""
    # not recommended to do in production
    setup.AccessTokenRequest(params={
        'grant_type': 'refresh_token',
        'refresh_token': 'example1',
        'client_id': 'example2',
        'client_secret': 'example3'
    })


def test_required_params_bymodel():
    """Validation and completeness of params with model."""
    # grant_type has an default value and is optional
    params = setup.AccessTokenParams(
        refresh_token='example1',
        client_id='example2',
        client_secret='example3')
    setup.AccessTokenRequest(params=params)


def test_request_access_token():
    """Simple API call to exchange refresh token."""
    expected = (
        'refresh_token=example1'
        '&client_id=example2'
        '&client_secret=example3&'
        'grant_type=refresh_token')
    params = setup.AccessTokenParams(
        refresh_token='example1',
        client_id='example2',
        client_secret='example3')
    setupapi = setup.AccessTokenRequest(params=params)
    token_request = setupapi.prepare_access_token_request()
    prepared_request = token_request.prepare()  # requests prepare() function
    assert prepared_request.body == expected
