""" See COPYING for license information """
try:
    import unittest2 as unittest
except:
    import unittest  # NOQA
from softlayer_messaging.resource import Resource, Response
from softlayer_messaging.errors import ResponseError
from mock import patch, Mock


class TestResource(unittest.TestCase):
    def test_init(self):
        r = Resource('http://softlayer.com')
        self.assertEqual(r.url, 'http://softlayer.com')

    def test_init_strip_base_url(self):
        r = Resource('http://softlayer.com/')
        self.assertEqual(r.url, 'http://softlayer.com')

    def test_get_item(self):
        r = Resource('http://softlayer.com')
        sub_r = r['path/to/file']
        self.assertEqual(sub_r.url, 'http://softlayer.com/path/to/file')

    def test_child_path(self):
        r = Resource('http://softlayer.com')
        child_path = r.child_path('path/to/file')
        self.assertEqual(child_path, 'http://softlayer.com/path/to/file')

    def test_get(self):
        r = Resource('http://softlayer.com')
        r.request = Mock()
        args = (Mock, )
        kwargs = {'test': Mock()}
        r.get(*args, **kwargs)
        r.request.assert_called_with('GET', *args, **kwargs)

    def test_put(self):
        r = Resource('http://softlayer.com')
        r.request = Mock()
        args = (Mock, )
        kwargs = {'test': Mock()}
        r.put(*args, **kwargs)
        r.request.assert_called_with('PUT', *args, **kwargs)

    def test_post(self):
        r = Resource('http://softlayer.com')
        r.request = Mock()
        args = (Mock, )
        kwargs = {'test': Mock()}
        r.post(*args, **kwargs)
        r.request.assert_called_with('POST', *args, **kwargs)

    def test_delete(self):
        r = Resource('http://softlayer.com')
        r.request = Mock()
        args = (Mock, )
        kwargs = {'test': Mock()}
        r.delete(*args, **kwargs)
        r.request.assert_called_with('DELETE', *args, **kwargs)

    def test_head(self):
        r = Resource('http://softlayer.com')
        r.request = Mock()
        args = (Mock, )
        kwargs = {'test': Mock()}
        r.head(*args, **kwargs)
        r.request.assert_called_with('HEAD', *args, **kwargs)

    @patch('requests.request')
    def test_request(self, mocked):
        r = Resource('http://softlayer.com')
        method = Mock()
        r.headers = {}
        kwargs = {'test': Mock()}
        result = r.request(method, 'path/to/file', **kwargs)
        kwargs['headers'] = r.headers
        mocked.assert_called_with(
            method, 'http://softlayer.com/path/to/file', **kwargs)
        self.assertIsInstance(result, Response)

    @patch('requests.request')
    def test_request_with_headers(self, mocked):
        r = Resource('http://softlayer.com')
        method = Mock()
        r.headers = {'default_header': 'value'}
        custom_headers = {'header1': Mock()}
        result = r.request(method, 'path/to/file', headers=custom_headers)
        custom_headers.update(r.headers)
        mocked.assert_called_with(
            method, 'http://softlayer.com/path/to/file',
            headers=custom_headers)
        self.assertIsInstance(result, Response)

    def test_repr(self):
        r = Resource('http://softlayer.com')
        r.url = "URL"
        value = repr(r)
        self.assertEqual(value, "<Resource [URL]>")


class TestResponse(unittest.TestCase):
    def test_response_init(self):
        original_response = Mock()
        response = Response(original_response)
        self.assertEqual(response.resp, original_response)
        self.assertEqual(response.status_code, original_response.status_code)
        self.assertEqual(response.url, original_response.url)
        self.assertEqual(response.headers, original_response.headers)
        self.assertEqual(response.request, original_response.request)
        self.assertEqual(response.content, original_response.content)
        self.assertEqual(response.text, original_response.text)

    def test_response_repr(self):
        original_response = Mock()
        response = Response(original_response)
        response.status_code = 200
        value = repr(response)
        self.assertEqual(value, "<Response [200]>")

    def test_response_raise_for_status_with_exception(self):
        original_response = Mock()
        original_response.error.return_value = Exception
        response = Response(original_response)
        self.assertRaises(Exception, response.raise_for_status)

    def test_response_raise_for_status(self):
        original_response = Mock()
        original_response.error = None
        original_response.status_code = 500
        original_response.content = '{"message": "error"}'
        response = Response(original_response)
        try:
            response.raise_for_status()
        except ResponseError as e:
            self.assertEqual(str(e), "500: error")
        else:
            self.fail("Did not raise a Response Error")

    def test_response_raise_for_status_with_error(self):
        original_response = Mock()
        original_response.error = None
        original_response.status_code = 500
        original_response.content = '''{
            "message": "Error",
            "errors": ["Error 1", "Error 2"]
        }'''
        response = Response(original_response)
        try:
            response.raise_for_status()
        except ResponseError as e:
            self.assertEqual(str(e), "500: Error -> [Error 1, Error 2]")
        else:
            self.fail("Did not raise a Response Error")

if __name__ == '__main__':
    unittest.main()
