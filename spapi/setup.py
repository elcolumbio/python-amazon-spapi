import boto3
from pydantic import BaseSettings
import requests


class Setup(BaseSettings):
    """Everything which is not part of the actual API request we put here."""
    # Objects we use in our main api calls.
    access_token: str = ''
    access_key: str = None
    secret_key: str = None
    session_token: str = None

    # the full json response
    _sts_creds: dict = dict()
    _access_token: dict = dict()

    # Settings Data
    # Fields we provide in e.g. .env files
    # IAM auth
    role_arn: str
    role_session_name: str

    # Sellerpartner API App
    # credentials for access token from seller central or oauth
    client: str
    secret: str
    refresh_token: str

    # data for api call
    endpoint: str
    region: str
    app_name: str  # 'my 0.1 (Language=Python/3.8; Platform=Ubuntu/20.4)'

    class Config:
        """
        Alternative locations for your configs.
        See in docs: https://pydantic-docs.helpmanual.io/usage/settings/
        """
        env_file = '~/.sellerpartnerapi.env'
        underscore_attrs_are_private = True

    def setter_access_token(self) -> str:
        """Token you pass to every api request, is valid for 1 hour."""
        # so far the only unsigned request
        lwa_login = 'https://api.amazon.com/auth/o2/token'
        params = {'grant_type': 'refresh_token',
                  'refresh_token': self.refresh_token,
                  'client_id': self.client, 'client_secret': self.secret}
        response = requests.post(lwa_login, data=params).json()
        access_token = response['access_token']
        self._access_token = response  # full json response
        self.access_token = access_token
        return access_token

    def setter_sts_creds(self) -> dict:
        """Temporal sts creds from your iam role."""
        # boto does the signing for us
        client = boto3.client('sts')
        sts_creds = client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.role_session_name)
        self._sts_creds = sts_creds  # full json response
        self.access_key = sts_creds['Credentials']['AccessKeyId']
        self.secret_key = sts_creds['Credentials']['SecretAccessKey']
        self.session_token = sts_creds['Credentials']['SessionToken']
        return sts_creds
