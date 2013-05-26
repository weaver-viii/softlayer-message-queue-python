""" See COPYING for license information """
try:
    import unittest2 as unittest
except:
    import unittest  # NOQA
from softlayer_messaging import get_client
from softlayer_messaging.client import QueueClient
from softlayer_messaging.compat import json
from mock import patch, Mock
import requests


class TestCore(unittest.TestCase):
    @patch('softlayer_messaging.QueueClient')
    def test_get_client(self, qc):
        account = 'account'
        client = get_client(account)
        self.assertEquals(client, qc())

    @patch('softlayer_messaging.QueueClient')
    def test_get_client_with_endpoint(self, qc):
        account = 'account'
        endpoint = 'endpoint'
        client = get_client(account, endpoint=endpoint)
        self.assertEquals(client, qc())


class TestClient(unittest.TestCase):
    def setUp(self):
        self.endpoint = 'http://softlayer.com'
        self.account = 'account'
        self.base_href = "%s/v1/%s" % (self.endpoint, self.account)
        self.client = QueueClient(self.endpoint, self.account)

    def test_client_init(self):
        self.assertEquals(self.client.url, self.base_href)
        self.assertEquals(self.client.account, self.account)

    @patch('requests.post')
    def test_authenticate(self, res):
        self.client.authenticate('username', 'password')
        res.assert_called_with('http://softlayer.com/v1/account/auth', headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'})

    @patch('requests.get')
    def test_ping_good(self, res):
        res.return_value.error = None
        res.return_value.status_code = 200
        self.assertTrue(self.client.ping())

    @patch('requests.get')
    def test_ping_status(self, res):
        res.return_value.error = None
        res.return_value.status_code = 500
        self.assertFalse(self.client.ping())

    @patch('requests.get')
    def test_ping_bad(self, res):
        res.side_effect = requests.RequestException('Fail')
        self.assertFalse(self.client.ping())

    @patch('requests.request')
    def test_request(self, res):
        header_resp = Mock()
        res.return_value.status_code = 200
        res.return_value.content = '{"some": "json"}'
        res.return_value.headers = header_resp
        result = self.client.request('GET', 'queues')
        self.assertEqual(result.json, {'some': 'json'})
        self.assertEqual(result.headers, header_resp)
        res.assert_called_with(
            'GET', '%s/queues' % (self.base_href,),
            headers=self.client.headers, auth=None)

    @patch('softlayer_messaging.queue.Queue')
    def test_queue(self, res):
        name = Mock()
        q = self.client.queue(name)
        res.assert_called_with(self.client.url, name, self.client.auth)
        self.assertEqual(q, res())

    @patch('softlayer_messaging.topic.Topic')
    def test_topic(self, res):
        name = Mock()
        q = self.client.topic(name)
        res.assert_called_with(self.client.url, name, self.client.auth)
        self.assertEqual(q, res())

    @patch('softlayer_messaging.client.QueueClient.request')
    def test_queues(self, res):
        tags = ['tag1', 'tag2']
        result = self.client.queues(tags=tags)
        res.assert_called_with('GET', 'queues', params={'tags': "tag1,tag2"})
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.client.QueueClient.request')
    def test_topics(self, res):
        tags = ['tag1', 'tag2']
        result = self.client.topics(tags=tags)
        res.assert_called_with('GET', 'topics', params={'tags': "tag1,tag2"})
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.client.QueueClient.request')
    def test_create_queue(self, res):
        name = 'name'
        kwargs = {'arg1': 'arg1', 'arg2': 'arg2'}
        result = self.client.create_queue(name, **kwargs)
        res.assert_called_with(
            'PUT', 'queues/name',
            data=json.dumps(kwargs))
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.client.QueueClient.request')
    def test_create_topic(self, res):
        name = 'name'
        kwargs = {'arg1': 'arg1', 'arg2': 'arg2'}
        result = self.client.create_topic(name, **kwargs)
        res.assert_called_with(
            'PUT', 'topics/name',
            data=json.dumps(kwargs))
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.client.QueueClient.request')
    def test_stats(self, res):
        result = self.client.stats()
        res.assert_called_with('GET', 'stats/hour')
        self.assertEqual(result, res().json)

    def test_repr(self):
        self.client.url = "URL"
        value = repr(self.client)
        self.assertEqual(value, "<QueueClient [URL]>")


if __name__ == '__main__':
    unittest.main()
