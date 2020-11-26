import hashlib
import hmac
import datetime
from pydantic import BaseModel, Field
import requests


class CredentialSetup(BaseModel):
    """Interface Model with all credentials set."""
    access_token: str = Field(
        description='Can be set with setupapi.setter_access_token()')
    access_key: str = Field(
        description='Can be set with setupapi.setter_sts_creds()')
    secret_key: str = Field(
        description='Can be set with setupapi.setter_sts_creds()')
    session_token: str = Field(
        description='Can be set with setupapi.setter_sts_creds()')

    endpoint: str
    region: str


class SPAPI():
    def __init__(
        self, setup, path, http_verb='GET', querystring='', payload=''
    ):
        validate = CredentialSetup
        validate(**setup.dict())

        self.setup = setup
        self.path: str = path  # todo fix naming

        self.set_datestrings()

        # api
        self.http_verb: str = http_verb
        self.host: str = setup.endpoint.split('https://')[-1]
        self.payload = payload

        self.canonical_headers = f'host:{self.host}\nx-amz-date:{self.amzdate}\n'
        self.canonical_request = None
        self.canonical_querystring: str = querystring

        self.service = 'execute-api'
        self.signed_headers = 'host;x-amz-date'
        self.algorithm = 'AWS4-HMAC-SHA256'
        self.credential_scope = (f'{self.datestamp}/{self.setup.region}'
                                 f'/{self.service}/aws4_request')

    def set_datestrings(self):
        """Create a date for headers and the credential string."""
        t = datetime.datetime.utcnow()
        self.amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        self.datestamp = t.strftime('%Y%m%d')

    def sign(self, key, msg):
        """Link how to sign requests: http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python ."""

        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(self):
        kDate = self.sign((
            'AWS4' + self.setup.secret_key).encode('utf-8'), self.datestamp)
        kRegion = self.sign(kDate, self.setup.region)
        kService = self.sign(kRegion, self.service)
        kSigning = self.sign(kService, 'aws4_request')
        return kSigning

    def hash_payload(self) -> str:
        """For GET requests it is an empty string."""
        return hashlib.sha256((self.payload).encode('utf-8')).hexdigest()

    def create_canonical_request(self):
        # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
        # https://cloud.google.com/storage/docs/authentication/canonical-requests

        canonical_request_components = [
            self.http_verb,
            self.path,
            self.canonical_querystring,
            self.canonical_headers,
            self.signed_headers,
            self.hash_payload()
        ]
        self.canonical_request = '\n'.join(canonical_request_components)

    def create_string_to_sign(self):
        hashed_request = hashlib.sha256(self.canonical_request.encode(
            'utf-8')).hexdigest()
        string_to_sign_components = [
            self.algorithm,
            self.amzdate,
            self.credential_scope,
            hashed_request
        ]
        self.string_to_sign = '\n'.join(string_to_sign_components)

        signing_key = self.getSignatureKey()

        # Sign the string_to_sign using the signing_key
        signature = hmac.new(signing_key, (
            self.string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def add_signing_to_request(self):
        # The signing information can be either in a query string value or in
        # a header named Authorization. This code shows how to use a header.
        # Create authorization header and add to request headers
        signature = self.create_string_to_sign()
        authorization_header = (
            f'{self.algorithm} '
            f'Credential={self.setup.access_key}/{self.credential_scope}'
            f', SignedHeaders={self.signed_headers} Signature={signature}')

        headers = {'x-amz-date': self.amzdate,
                   'Authorization': authorization_header,
                   'x-amz-access-token': self.setup.access_token,
                   'x-amz-security-token': self.setup.session_token}
        return headers

    def get_request(self):
        headers = self.add_signing_to_request()
        request_url = (
            self.setup.endpoint + self.path + self.canonical_querystring)

        print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
        print('Request URL = ' + request_url)
        r = requests.get(request_url, headers=headers)

        print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
        print('Response code: %d\n' % r.status_code)
        print(r.text)
        return r

    def main(self):
        """Main entry for queries."""

        self.create_canonical_request()
        self.create_string_to_sign()
        self.add_signing_to_request()
        response = self.get_request()
        return response
