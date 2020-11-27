import boto3
from pydantic import BaseSettings
import requests


class Setup(BaseSettings):
    """Everything which is not part of the actual API request we put here."""
    # Output see in model CredentialSetup in main.py
    access_token: str = None
    access_key: str = None
    secret_key: str = None
    session_token: str = None

    # Settings Data, we have an example file .sellerpartnerapi.env
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
    app_name: str

    class Config:
        """
        Alternative locations for your configs.
        See in docs: https://pydantic-docs.helpmanual.io/usage/settings/
        """
        env_file = '~/.sellerpartnerapi.env'
        underscore_attrs_are_private = True

    def get_access_token(self, params) -> dict:
        lwa_login = 'https://api.amazon.com/auth/o2/token'
        return requests.post(lwa_login, data=params).json()

    def setter_access_token(self) -> dict:
        """Token you pass to every api request, is valid for 1 hour."""
        # so far the only unsigned request
        params = {'grant_type': 'refresh_token',
                  'refresh_token': self.refresh_token,
                  'client_id': self.client, 'client_secret': self.secret}
        response = self.get_access_token(params)
        self.access_token = response['access_token']
        return response

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
