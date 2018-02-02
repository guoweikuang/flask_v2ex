# -*- coding: utf-8 -*-
"""
Test for v2ex
"""
import unittest
from flask import current_app
from v2ex.models import User 
from v2ex import db, create_app


class BasicTestCase(unittest.TestCase):
    """测试用例"""
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        print(current_app.config["TESTING"])
        self.assertTrue(current_app.config["TESTING"])


if __name__ == '__main__':
    unittest.main()

