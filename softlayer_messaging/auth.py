""" See COPYING for license information """
import requests.auth
from softlayer_messaging.errors import Unauthenticated


class QueueAuth(requests.auth.AuthBase):
    """Attaches User Authentication to the given request object"""
    def __init__(self, endpoint, username, api_key, auth_token=None):
        self.endpoint = endpoint
        self.username = username
        self.api_key = api_key
        self.auth_token = auth_token

    def auth(self):
        headers = {
            'X-Auth-User': self.username,
            'X-Auth-Key': self.api_key
        }
        resp = requests.post(self.endpoint, headers=headers)
        if resp.ok:
            self.auth_token = resp.headers['X-Auth-Token']
        else:
            raise Unauthenticated("Error while authenticating", resp)

    def handle_error(self, resp, **kwargs):
        resp.request.deregister_hook('response', self.handle_error)
        if resp.status_code == 503:
            resp.connection.send(resp.request)
        elif resp.status_code == 401:
            self.auth()
            resp.request.headers['X-Auth-Token'] = self.auth_token
            resp.connection.send(resp.request)

    def __call__(self, r):
        if not self.auth_token:
            self.auth()
        r.register_hook('response', self.handle_error)
        r.headers['X-Auth-Token'] = self.auth_token
        return r


class NonAuth(requests.auth.AuthBase):
    """Does not actually auth"""
    pass
