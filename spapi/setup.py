"""Structured setup to get all your tokens."""
import boto3
from pydantic import BaseModel, BaseSettings
import requests


class AccessTokenParams(BaseSettings):
    """Your credentials are best put into ~/.sellerpartnerapi.env."""
    grant_type = 'refresh_token'
    refresh_token: str
    client_id: str
    client_secret: str

    class Config:
        """
        Alternative locations for your configs.
        See in docs: https://pydantic-docs.helpmanual.io/usage/settings/
        """
        env_file = '~/.sellerpartnerapi.env'
        underscore_attrs_are_private = True


class AccesTokenRequest(BaseModel):
    """Model for data we need to request access token."""
    url = 'https://api.amazon.com/auth/o2/token'
    params: dict = AccessTokenParams().dict()

    def get_access_token(self) -> dict:
        """Exchange your refresh token into an access token."""
        return requests.post(self.url, data=self.params).json()

    def prepare_access_token(self) -> dict:
        """For testing we return a request and you can do req.prepared()."""
        req = requests.Request(method='PUT', url=self.url, data=self.params)
        return req


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

    # AccesTokenRequest
    access_token_request: AccesTokenRequest = AccesTokenRequest()

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
