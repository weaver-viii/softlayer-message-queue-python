""" See COPYING for license information """
try:
    import unittest2 as unittest
except:
    import unittest
from softlayer_messaging.queue import Queue, Message
from softlayer_messaging.compat import json
from mock import patch, Mock


class TestQueue(unittest.TestCase):
    def setUp(self):
        self.endpoint = 'http://softlayer.com/v1/account'
        self.queue_name = 'queue_name'
        self.base_href = "%s/queues/%s" % (self.endpoint, self.queue_name)
        self.auth = Mock()
        self.queue = Queue(self.endpoint, self.queue_name, self.auth)

    def test_client_init(self):
        self.assertEquals(self.queue.url, self.base_href)
        self.assertEquals(self.queue.name, self.queue_name)
        self.assertEquals(self.queue.auth, self.auth)

    @patch('requests.request')
    def test_request(self, res):
        json_resp = Mock()
        header_resp = Mock()
        res.return_value.error = None
        res.return_value.status_code = 200
        res.return_value.json = json_resp
        res.return_value.headers = header_resp
        self.queue.headers = {'test': Mock()}
        result = self.queue.request('GET', 'messages')
        self.assertEqual(result.json, json_resp)
        self.assertEqual(result.headers, header_resp)

        res.assert_called_with('GET', '%s/messages' % (self.base_href,),
            headers=self.queue.headers, auth=self.auth)

    @patch('softlayer_messaging.queue.Queue.request')
    def test_detail(self, res):
        result = self.queue.detail()
        res.assert_called_with('GET')
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.queue.Queue.request')
    def test_modify_queue(self, res):
        kwargs = {'arg1': 'arg1', 'arg2': 'arg2'}
        result = self.queue.modify(**kwargs)
        res.assert_called_with('PUT', data=json.dumps(kwargs))
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.queue.Queue.request')
    def test_delete_queue(self, res):
        result = self.queue.delete()
        res.assert_called_with('DELETE')
        self.assertEqual(result, True)

    @patch('softlayer_messaging.queue.Queue.request')
    def test_delete_queue(self, res):
        result = self.queue.delete(force=True)
        res.assert_called_with('DELETE', params={'force': 1})
        self.assertEqual(result, True)

    @patch('softlayer_messaging.queue.Queue.request')
    def test_push(self, res):
        message_body = "body"
        message_options = {'option_a': 'a', 'option_b': 'b'}
        result = self.queue.push(message_body, **message_options)
        json_doc = {'body': 'body', 'option_a': 'a', 'option_b': 'b'}
        res.assert_called_with('POST', 'messages',
            data=json.dumps(json_doc))
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.queue.Queue.request')
    def test_pop(self, res):
        count = Mock()
        result = self.queue.pop(count)
        res.assert_called_with('GET', 'messages', params={'batch': count})
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.queue.Message')
    def test_message(self, res):
        msg_id = Mock()
        q = self.queue.message(msg_id)
        res.assert_called_with(self.queue.url, self.queue.name, msg_id, self.queue.auth)
        self.assertEqual(q, res())

    def test_repr(self):
        self.queue.url = "URL"
        value = repr(self.queue)
        self.assertEqual(value, "<Queue [URL]>")


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.endpoint = 'http://softlayer.com/v1/account/queues/queue_name'
        self.queue_name = 'queue_name'
        self.message_id = 'message_id'
        self.base_href = "%s/messages/%s" % (self.endpoint, self.message_id)
        self.auth = Mock()
        self.message = Message(self.endpoint, self.queue_name, self.message_id, self.auth)

    @patch('requests.request')
    def test_request(self, res):
        json_resp = Mock()
        header_resp = Mock()
        res.return_value.error = None
        res.return_value.status_code = 200
        res.return_value.json = json_resp
        res.return_value.headers = header_resp
        self.message.headers = {'test': Mock()}
        result = self.message.request('DELETE')
        self.assertEqual(result.json, json_resp)
        self.assertEqual(result.headers, header_resp)

        res.assert_called_with('DELETE', self.base_href,
            headers=self.message.headers, auth=self.auth)

    def test_client_init(self):
        self.assertEquals(self.message.url, self.base_href)
        self.assertEquals(self.message.queue_name, self.queue_name)
        self.assertEquals(self.message.id, self.message_id)
        self.assertEquals(self.message.auth, self.auth)

    @patch('softlayer_messaging.queue.Message.request')
    def test_delete_message(self, res):
        result = self.message.delete()
        res.assert_called_with('DELETE')
        self.assertEqual(result, True)

    def test_repr(self):
        self.message.url = "URL"
        value = repr(self.message)
        self.assertEqual(value, "<Message [URL]>")

if __name__ == '__main__':
    unittest.main()
