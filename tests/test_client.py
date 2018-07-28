# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~
v2ex test case

"""
import unittest

from v2ex import db
from v2ex import create_app
from v2ex.models import User


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('V2EX' in response.get_data(as_text=True))

    def test_register_and_login(self):
        response = self.client.post('/auth/register', data={
            'username': 'kubernetes',
            'email': 'hello@qq.com',
            'password': '2014081029',
            'password2': '2014081029'
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/auth/login', data={
            'email': 'hello@qq.com',
            'password': '2014081029'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(u'kubernetes' in response.get_data(as_text=True))

        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(u"登录" in response.get_data(as_text=True))
