""" See COPYING for license information """
try:
    import unittest2 as unittest
except:
    import unittest  # NOQA
from softlayer_messaging.topic import Topic, Subscription
from softlayer_messaging.compat import json
from mock import patch, Mock


class TestTopic(unittest.TestCase):

    def setUp(self):
        self.endpoint = 'http://softlayer.com/v1/account'
        self.topic_name = 'topic_name'
        self.base_href = "%s/topics/%s" % (self.endpoint, self.topic_name)
        self.auth = Mock()
        self.topic = Topic(self.endpoint, self.topic_name, self.auth)

    def test_client_init(self):
        self.assertEquals(self.topic.url, self.base_href)
        self.assertEquals(self.topic.name, self.topic_name)
        self.assertEquals(self.topic.auth, self.auth)

    @patch('requests.request')
    def test_request(self, res):
        header_resp = Mock()
        res.return_value.error = None
        res.return_value.status_code = 200
        res.return_value.content = '{"some": "json"}'
        res.return_value.headers = header_resp
        self.topic.headers = {'test': Mock()}
        result = self.topic.request('GET', 'messages')
        self.assertEqual(result.json, {'some': 'json'})
        self.assertEqual(result.headers, header_resp)

        res.assert_called_with(
            'GET', '%s/messages' % (self.base_href,),
            headers=self.topic.headers, auth=self.auth)

    @patch('softlayer_messaging.topic.Topic.request')
    def test_detail(self, res):
        result = self.topic.detail()
        res.assert_called_with('GET')
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.topic.Topic.request')
    def test_modify_queue(self, res):
        kwargs = {'arg1': 'arg1', 'arg2': 'arg2'}
        result = self.topic.modify(**kwargs)
        res.assert_called_with('PUT', data=json.dumps(kwargs))
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.topic.Topic.request')
    def test_delete_topic(self, res):
        result = self.topic.delete()
        res.assert_called_with('DELETE', params={})
        self.assertEqual(result, True)

    @patch('softlayer_messaging.topic.Topic.request')
    def test_delete_topic_force(self, res):
        result = self.topic.delete(force=True)
        res.assert_called_with('DELETE', params={'force': 1})
        self.assertEqual(result, True)

    @patch('softlayer_messaging.topic.Topic.request')
    def test_push(self, res):
        message_body = "body"
        message_options = {'option_a': 'a', 'option_b': 'b'}
        result = self.topic.push(message_body, **message_options)
        json_doc = {'body': 'body', 'option_a': 'a', 'option_b': 'b'}
        res.assert_called_with(
            'POST', 'messages',
            data=json.dumps(json_doc))
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.topic.Topic.request')
    def test_subscriptions(self, res):
        result = self.topic.subscriptions()
        res.assert_called_with('GET', 'subscriptions')
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.topic.Topic.request')
    def test_create_subscription(self, res):
        type_ = 'http'
        options = {'arg1': 'arg1', 'arg2': 'arg2'}
        result = self.topic.create_subscription(type_, **options)
        subscription = {"endpoint_type": type_, "endpoint": options}
        res.assert_called_with(
            'POST', 'subscriptions',
            data=json.dumps(subscription))
        self.assertEqual(result, res().json)

    @patch('softlayer_messaging.topic.Subscription')
    def test_subscription(self, res):
        _id = Mock()
        q = self.topic.subscription(_id)
        res.assert_called_with(self.topic.url, _id, self.topic.auth)
        self.assertEqual(q, res())

    def test_repr(self):
        self.topic.url = "URL"
        value = repr(self.topic)
        self.assertEqual(value, "<Topic [URL]>")


class TestSubscription(unittest.TestCase):
    def setUp(self):
        self.endpoint = 'http://softlayer.com/v1/account/topics/topic'
        self.sub_id = 'sub_id'
        self.base_href = "%s/subscriptions/%s" % (self.endpoint, self.sub_id)
        self.auth = Mock()
        self.sub = Subscription(self.endpoint, self.sub_id, self.auth)

    def test_client_init(self):
        self.assertEquals(self.sub.url, self.base_href)
        self.assertEquals(self.sub.id, self.sub_id)
        self.assertEquals(self.sub.auth, self.auth)

    @patch('requests.request')
    def test_request(self, res):
        header_resp = Mock()
        res.return_value.error = None
        res.return_value.status_code = 200
        res.return_value.content = '{"some": "json"}'
        res.return_value.headers = header_resp
        self.sub.headers = {'test': Mock()}
        result = self.sub.request('GET', 'path')
        self.assertEqual(result.json, {'some': 'json'})
        self.assertEqual(result.headers, header_resp)
        res.assert_called_with(
            'GET', '%s/path' % (self.base_href,),
            headers=self.sub.headers, auth=self.auth)

    @patch('softlayer_messaging.topic.Subscription.request')
    def test_delete_subscription(self, res):
        result = self.sub.delete()
        res.assert_called_with('DELETE')
        self.assertEqual(result, True)

    def test_repr(self):
        self.sub.url = "URL"
        value = repr(self.sub)
        self.assertEqual(value, "<Subscription [URL]>")


if __name__ == '__main__':
    unittest.main()
