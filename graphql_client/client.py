import graphql_client.utils
import requests
import tenacity
import logging
import collections
import os

logger = logging.getLogger(__name__)

exponential_retry = tenacity.retry(
    stop = tenacity.stop_after_attempt(4),
    wait = tenacity.wait_exponential(multiplier=0.2/2),
    before = tenacity.before_log(logger, logging.DEBUG),
    after = tenacity.after_log(logger, logging.DEBUG),
    before_sleep = tenacity.before_sleep_log(logger, logging.WARNING)
)

class Client:

    def __init__(
        self,
        uri=None,
        accessToken=None,
        token_uri=None,
        audience=None,
        client_id=None,
        client_secret=None,
        http_request_timeout=10
    ):
        if uri is None:
            uri = os.getenv('GRAPHQL_URI')
        if token_uri is None:
            token_uri = os.getenv('GRAPHQL_TOKEN_URI')
        if audience is None:
            audience = os.getenv('GRAPHQL_AUDIENCE')
        if client_id is None:
            client_id = os.getenv('GRAPHQL_CLIENT_ID')
        if client_secret is None:
            client_secret = os.getenv('GRAPHQL_CLIENT_SECRET')
        if uri is None:
            raise ValueError('GraphQL URI not specified and environment variable GRAPHQL_URI not set')
        if accessToken is None and token_uri is None:
            raise ValueError('No access token specified, GraphQL token URI not specified, and environment variable GRAPHQL_TOKEN_URI not set')
        if accessToken is None and audience is None:
            raise ValueError('No access token specified, GraphQL audience not specified, and environment variable GRAPHQL_AUDIENCE not set')
        if accessToken is None and client_id is None:
            raise ValueError('No access token specified, GraphQL client ID not specified, and environment variable GRAPHQL_CLIENT_ID not set')
        if accessToken is None and client_secret is None:
            raise ValueError('No access token specified, GraphQL client secret not specified, and environment variable GRAPHQL_CLIENT_SECRET not set')
        self.uri = uri
        self.accessToken = accessToken
        self.client_credentials = {
            'token_uri': token_uri,
            'audience': audience,
            'client_id': client_id,
            'client_secret': client_secret
        }
        self.headers = {'Content-Type': 'application/json'}
        if self.accessToken is None:
            try:
                auth_response = requests.post(
                    self.client_credentials["token_uri"],
                    {
                        "audience": self.client_credentials["audience"],
                        "grant_type": "client_credentials",
                        "client_id": self.client_credentials["client_id"],
                        "client_secret": self.client_credentials["client_secret"]
                    },
                    timeout=http_request_timeout
                )
                self.accessToken = auth_response.json().get('access_token')
            except Exception as err:
                raise Exception("Invalid client_credentials")
            if self.accessToken is None:
                raise Exception("Invalid client_credentials")
        self.headers["Authorization"] = f'bearer {self.accessToken}'

    @exponential_retry
    def execute(
        self,
        request_body_string,
        request_variables_dict=None,
        http_request_timeout=None
    ):
        if http_request_timeout is None:
            http_request_timeout = self.http_request_timeout
        payload = collections.OrderedDict({
            'query': request_body_string,
            'variables': request_variables_dict or {},
        })
        request = requests.post(
            self.uri,
            data=graphql_client.utils.graphql_json_dumps(payload),
            headers=self.headers,
            timeout=http_request_timeout
        )
        request.raise_for_status()
        result = request.json()
        if "errors" in result:
            return result.get("errors")
        return result.get("data")
