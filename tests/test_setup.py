import pytest
from pydantic import ValidationError
from spapi import setup


def test_invalid_params():
    """Pydantic should find required params somewhere."""
    with pytest.raises(ValidationError):
        setup.Setup(
            endpoint='https://sellingpartnerapi-eu.amazon.com',
            region=None)


def test_required_params():
    """Validation and completeness of params without model."""
    setup.AccesTokenRequest(params={
        'grant_type': 'refresh_token',
        'refresh_token': 'example',
        'client_id': 'example',
        'client_secret': 'example'
    })


def test_required_params_bymodel(setup_data_model):
    """We use a model in conftest.py for testing."""
    model = setup_data_model(client='overwrite_client_from_model')
    setupapi = setup.Setup(**model.dict())
    setupapi.client == 'overwrite_client_from_model'


def test_setter_access_token(setup_data_model):
    """Simple API call to exchange refresh token."""
    model = setup_data_model()
    setupapi = setup.Setup(**model.dict())
    prepared_request = setupapi.setter_access_token(test=True)
    assert not set(prepared_request.data) - {'grant_type', 'refresh_token', 'client_id', 'client_secret'}
