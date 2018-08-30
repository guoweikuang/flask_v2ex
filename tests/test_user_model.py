# -*- coding: utf-8 -*-
import unittest

from v2ex import db, create_app
from v2ex.models import User
from v2ex.models import Follow


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

    def test_follow(self):
        user1 = User(email="user1@qq.com", password='user1')
        user2 = User(email="user2@qq.com", password='user2')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user1.is_followed_by(user2))

        user1.follow(user2)
        db.session.add(user1)
        db.session.commit()

        self.assertTrue(user1.is_following(user2))
        self.assertFalse(user1.is_followed_by(user2))
        self.assertTrue(user2.is_followed_by(user1))
        self.assertTrue(user1.followed.count() == 1)
        self.assertTrue(user2.followers.count() == 1)

        f = user1.followed.all()[-1]
        self.assertTrue(f.followed == user2)

        f = user2.followers.all()[-1]
        self.assertTrue(f.follower == user1)

        user1.unfollow(user2)
        db.session.add(user1)
        db.session.commit()

        self.assertTrue(user1.followed.count() == 0)
        self.assertTrue(user2.followers.count() == 0)
        self.assertTrue(Follow.query.count() == 0)

    def test_to_json(self):
        user = User(email='user@qq.com', password='user')
        db.session.add(user)
        db.session.commit()

        with self.app.test_request_context('/'):
            user_json = user.to_json()

        expected_keys = ['id', 'username', 'email', 'avatar_url', 'join_time', 'username_url']
        self.assertEqual(sorted(user_json.keys()), sorted(expected_keys))