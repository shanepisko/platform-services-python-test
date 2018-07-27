from tornado.testing import AsyncTestCase, gen_test
from tornado.web import Application
from tornado.httpserver import HTTPRequest
from tornado.httpclient import AsyncHTTPClient
from unittest.mock import Mock
from user_handler import UserRewardsHandler

import json
import unittest
import urllib.parse

# This test uses an asynchronous style similar to most async
# application code.
class RewardsGetTestCase(AsyncTestCase):
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        client.fetch("http://localhost:7050/user-rewards/", self.handle_fetch)
        self.wait()

    def handle_fetch(self, response):
        # Test contents of response (failures and exceptions here
        # will cause self.wait() to throw an exception and end the
        # test).
        # Exceptions thrown here are magically propagated to
        # self.wait() in test_http_fetch() via stack_context.
        print(response.body)
        result = json.loads(response.body.decode('utf-8'))
        self.assertIsNotNone(result)
        self.stop()

class NewUserTestCase(AsyncTestCase):
    data = {'email': 'hondo@gmail.com', 'order_total': 103}

    def test_http_post(self):
        client = AsyncHTTPClient(self.io_loop)
        body = urllib.parse.urlencode(self.data) #Make it into a post request
        client.fetch("http://localhost:7050/user-rewards/", self.handle_fetch, method='POST', headers=None, body=body)
        self.wait()

    def handle_fetch(self, response):
        print(response.body)
        result = json.loads(response.body.decode('utf-8'))
        self.assertIsNotNone(result['inserted_id'])
        self.stop()


class UpdateUserTestCase(AsyncTestCase):

    data = {'email': 'hondo@gmail.com', 'order_total': 86}

    def test_http_post(self):
        client = AsyncHTTPClient(self.io_loop)
        body = urllib.parse.urlencode(self.data) #Make it into a post request
        client.fetch("http://localhost:7050/user-rewards/", self.handle_fetch, method='POST', headers=None, body=body)
        self.wait()

    def handle_fetch(self, response):
        print(response.body)
        result = json.loads(response.body.decode('utf-8'))
        print(result)
        self.stop()

class DeleteTestUserCase(AsyncTestCase):

        def delete_test_user(self):
            client = AsyncHTTPClient(self.io_loop)
            # body = urllib.parse.urlencode(data) #Make it into a post request
            client.fetch("http://localhost:7050/user-rewards/hondo@gmail.com", self.handle_fetch, method='DELETE', headers=None, body=None)
            self.wait()

        def handle_fetch(self, response):
            print(response.body)
            result = json.loads(response.body.decode('utf-8'))
            self.assertEqual(1, result['n'])
            self.stop()

if __name__ == '__main__':
    unittest.main()
