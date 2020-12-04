import pytest
from pydantic import BaseModel


@pytest.fixture
def setup_data_model():
    class SetupData(BaseModel):
        role_arn: str = 'arn:aws:iam::123xxx'
        role_session_name: str = '123xxx'
        client: str = 'amzn1.application-oa2-client.123xxx'
        secret: str = '123xxx'
        refresh_token: str = 'Atzr|'
        endpoint: str = 'https://sellingpartnerapi-eu.amazon.com'
        region: str = 'eu-west-1'
        app_name: str = (
            'python sellerpartnerapi'
            '(Language=Python/3.8; Platform=Ubuntu/20.4)')
    return SetupData
