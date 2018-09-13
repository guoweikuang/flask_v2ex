# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~
user auth and user info api.

@author guoweikuang
"""
from flask import jsonify
from flask_restful import Resource
from flask_restful import reqparse


from v2ex.models import User


class UserInfoAPI(Resource):
    """用户个人中心"""
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True,
                                 help='not username provided', location='args')
        super().__init__(*args, **kwargs)

    def get(self):
        args = self.parser.parse_args()
        user = User.query.filter_by(username=args['username']).first()
        if user is None:
            return jsonify({"error": 'no user'})
        return jsonify(user.to_viewdict())




