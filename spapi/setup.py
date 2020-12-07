"""Structured setup to get all your tokens."""
import boto3
from pydantic import BaseModel, BaseSettings, ValidationError
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


class AccessTokenRequest(BaseModel):
    """Model for data we need to request access token."""
    url = 'https://api.amazon.com/auth/o2/token'
    try:  # if you change local files you have to reimport
        params: AccessTokenParams = AccessTokenParams()
    except ValidationError:
        params: AccessTokenParams

    def 

    def get_access_token(self) -> dict:
        """Exchange your refresh token into an access token."""
        return requests.post(self.url, data=self.params.dict()).json()

    def prepare_access_token_request(self) -> dict:
        """For testing we return a request and you can do req.prepared()."""
        req = requests.Request(
            method='PUT', url=self.url, data=self.params.dict())
        return req

    def set_access_token(self) -> None:
        """Easy object interface for main."""
        self.access_token = self.get_access_token()['access_token']


class StsTokenRequest(BaseSettings):
    """IAM Authentification with Amazon STS."""
    role_arn: str
    role_session_name: str

    class Config:
        """
        Alternative locations for your configs.
        See in docs: https://pydantic-docs.helpmanual.io/usage/settings/
        """
        env_file = '~/.sellerpartnerapi.env'
        underscore_attrs_are_private = True

    def get_sts_creds(self) -> dict:
        """Temporal sts creds from your iam role."""
        # boto does the signing for us
        client = boto3.client('sts')
        sts_creds = client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.role_session_name)
        return sts_creds

    def set_sts_creds(self) -> None:
        sts_creds = self.get_sts_creds()
        self.access_key = sts_creds['Credentials']['AccessKeyId']
        self.secret_key = sts_creds['Credentials']['SecretAccessKey']
        self.session_token = sts_creds['Credentials']['SessionToken']
