import pytest
from pydantic import ValidationError
from spapi import setup


def test_invalid_params():
    """Pydantic should find required params somewhere."""
    with pytest.raises(ValidationError):
        setup.Setup(
            endpoint='https://sellingpartnerapi-eu.amazon.com',
            region=None)
