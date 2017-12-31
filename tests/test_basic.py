# -*- coding: utf-8 -*-
"""
Test for v2ex
"""
import unittest
from v2ex.models import User 
from v2ex import db


class BasicTest(unittest.TestCase):
    """测试用例"""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_password_setter(self):
        user = User(username='guo', mail='15602200534@163.com', password='2014081029')
        self.assertTrue(user.password_hash is not None)


if __name__ == '__main__':
    unittest.main()

