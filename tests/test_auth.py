""" See COPYING for license information """
try:
    import unittest2 as unittest
except:
    import unittest  # NOQA
from softlayer_messaging.auth import QueueAuth
from softlayer_messaging.errors import Unauthenticated
from mock import patch, Mock


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.endpoint = Mock()
        self.username = Mock()
        self.api_key = Mock()
        self.auth_token = Mock()
        self.auth = QueueAuth(
            self.endpoint, self.username, self.api_key,
            auth_token=self.auth_token)

    def test_init(self):
        self.auth.endpoint = self.endpoint
        self.auth.username = self.username
        self.auth.api_key = self.api_key
        self.auth.auth_token = self.auth_token

    @patch('requests.post')
    def test_auth(self, res):
        self.auth.auth()
        res.assert_called_once_with(
            self.endpoint,
            headers={'X-Auth-User': self.username, 'X-Auth-Key': self.api_key})
        self.assertNotEqual(
            self.auth_token, self.auth.auth_token, 'auth token was set')

    @patch('requests.post')
    def test_auth_raises_error(self, res):
        response = Mock()
        response.ok = False
        res.return_value = response
        self.assertRaises(Unauthenticated, self.auth.auth)

    def test_auth_handle_error_resend_on_503(self):
        m = Mock()
        m.status_code = 503
        self.auth.handle_error(m)
        m.connection.send.assert_called_once_with(m.request)

    def test_auth_handle_error_reauth_on_401(self):
        self.auth.auth = Mock()
        m = Mock()
        m.status_code = 401
        m.request.headers = {}
        self.auth.handle_error(m)
        self.auth.auth.assert_called_once()
        m.connection.send.assert_called_once_with(m.request)

    def test_call(self):
        request = Mock()
        request.headers = {}
        self.auth(request)
        self.assertEqual(request.headers, {'X-Auth-Token': self.auth_token})

    def test_call_unauthed(self):
        self.auth.auth = Mock()
        request = Mock()
        request.headers = {}
        self.auth.auth_token = None
        self.auth(request)
        self.auth.auth.assert_called_once_with()
        self.assertEqual(request.headers, {'X-Auth-Token': None})


if __name__ == '__main__':
    unittest.main()
