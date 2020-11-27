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
    """We test the params passing."""
    # everything which pydantic can cast to a string
    setup.Setup(
        role_arn=44.44,  # we have to introduce more rules
        role_session_name='',
        client='',
        secret='',
        refresh_token='',
        endpoint='',
        region='',
        app_name=''
    )
