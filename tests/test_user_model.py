# -*- coding: utf-8 -*-
import unittest

from v2ex import db, create_app
from v2ex.models import User


class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        user = User(password="guoweikuang")
        self.assertTrue(user.password_hash is not None)

    def test_password_no_getter(self):
        user = User(password="guoweikuang")
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        user = User(password="guoweikuang")
        self.assertTrue(user.verify_password('guoweikuang'))
        self.assertFalse(user.verify_password('hello'))

    def test_password_salts_is_random(self):
        user1 = User(password="guoweikuang")
        user2 = User(password="guoweikuang")
        self.assertTrue(user1.password_hash != user2.password_hash)