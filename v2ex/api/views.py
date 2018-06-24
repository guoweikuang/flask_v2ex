# -*- coding: utf-8 -*-
import arrow
from datetime import datetime, timedelta
from flask import jsonify, g, request, current_app
from flask_restful import Resource, Api, reqparse

from .. import db
from ..models import User
from ..models import Node
from ..models import Topic
from ..models import Comment
from ..models import TopicAppend
from ..email import send_email
from ..utils import add_notify_in_content
from . import api
from .errors import bad_request, internal_server_error, page_not_found
from .authentication import auth

restful_api = Api(api)


class TopicApi(Resource):
    """restful api to get topic
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', type=str, required=True,
                                 help='not title provided', location='json')
        self.parser.add_argument('content', type=str, required=True,
                                 help='not content provided', location='json')
        self.parser.add_argument('node_id', type=int, required=True,
                                 help='not node_id provided', location='json')
        super(TopicApi, self).__init__()

    def get(self):
        page = int(request.args.get('page', 1, type=int))
        per_page = current_app.config['PER_PAGE']
        offset = (page - 1) * per_page
        topics = Topic.query.order_by(Topic.create_time.desc()).limit(per_page + offset)
        topics = topics[offset:offset + per_page]
        if not topics:
            return jsonify({"error": "no topics"})
        return jsonify({'topic': [topic.to_json() for topic in topics]})

    @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        topic = Topic(title=args['title'],
                      content=args['content'],
                      node_id=args['node_id'],
                      user=g.current_user)
        db.session.add(topic)
        db.session.commit()
        return jsonify({'status': 200})


class TopicIdApi(Resource):
    """get topic by topic_id
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('content', type=str, required=True,
                                 help='not comment content provided', location='json')
        self.parser.add_argument('tid', type=int, required=True,
                                 help='not topic id provided', location='json')
        super(TopicIdApi, self).__init__()

    def get(self, id):
        topic = Topic.query.filter_by(id=id).first()
        if topic is None:
            return jsonify({"error": "no topic"})
        return jsonify(topic.to_json())

    @auth.login_required
    def post(self, id):
        args = self.parser.parse_args()
        topic = Topic.query.filter_by(id=id).first_or_404()
        comment = Comment(content=args['content'],
                          user=g.current_user,
                          topic=topic)
        topic.reply_num += 1
        db.session.add(comment)
        db.session.commit()
        add_notify_in_content(args['content'], g.current_user.id, id, comment.id)


class TopicAppendAPI(Resource):
    """ topic append api.
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('content', type=str, required=True,
                                 help='not append content provided', location='json')
        super(TopicAppendAPI, self).__init__()

    @auth.login_required
    def post(self, id):
        args = self.parser.parse_args()
        topic = Topic.query.filter_by(id=id).first_or_404()
        if g.current_user.id != topic.user.id:
            return jsonify({"error": "can't append topic"})
        append = TopicAppend(content=args['content'], topic_id=id)
        db.session.add(append)
        db.session.commit()
        return jsonify({"status": 200})


class TopicEditAPI(Resource):
    """ topic edit api.

    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('content', type=str, required=True,
                                 help='not append content provided', location='json')
        super(TopicEditAPI, self).__init__()

    @auth.login_required
    def post(self, id):
        args = self.parser.parse_args()
        topic = Topic.query.filter_by(id=id).first_or_404()
        if g.current_user.id != topic.user.id:
            return jsonify({"error": "can't edit topic"})
        topic.content = args['content']
        db.session.add(topic)
        db.session.commit()
        return jsonify({"status": 200})


class HotTopicAPI(Resource):
    """ top hot topic api.

    """
    def get(self):
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        topics = Topic.query.filter(Topic.create_time.between(yesterday, today))
        return jsonify({'topic': [topic.to_json() for topic in topics]})


class NodeAPI(Resource):
    """ node api.

    """

    def get(self):
        nodes = Node.query.all()
        if nodes is None:
            return jsonify({"error": 'no node'})
        return jsonify({'node': [node.to_json() for node in nodes]})


class NodeIdAPI(Resource):
    """ node id content api.

    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, required=False,
                                 help='not append content provided',
                                 location=['json', 'args', 'headers'],
                                 default=1)
        super(NodeIdAPI, self).__init__()

    def get(self, id):
        # node = Node.query.filter_by(id=id).first_or_404()
        # page = int(request.args.get('page', 1, type=int))
        args = self.parser.parse_args()
        page = args['page']
        print(page)
        per_page = current_app.config['PER_PAGE']
        offset = (page - 1) * per_page
        topics = Topic.query.filter_by(node_id=id).order_by(
            Topic.create_time.desc()).limit(per_page + offset)
        topics = topics[offset:offset + per_page]
        if not topics:
            return jsonify({"error": "no topics"})
        return jsonify({'topic': [topic.to_json() for topic in topics]})


class LoginAPI(Resource):
    """ login API.

    """

    def __init__(self):
        pass


class RegisterAPI(Resource):
    """ register api.

    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=str, required=True,
                                 help='not email provided', location='json')
        self.parser.add_argument('username', type=str, required=True,
                                 help='not username provided', location='json')
        self.parser.add_argument('password', type=str, required=True,
                                 help='not password provided', location='json')
        self.parser.add_argument('password2', type=str, required=True,
                                 help='not two password provided', location='json')
        super(RegisterAPI, self).__init__()

    def post(self):
        args = self.parser.parse_args()
        if User.query.filter_by(email=args['email']).first():
            return jsonify({"error": "邮箱已经被注册"})
        if User.query.filter_by(username=args['username']).first():
            return jsonify({"error": "用户名已经被使用"})
        user = User(email=args['email'],
                    username=args['username'],
                    password=args['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"status": 200})


class ResetPasswordAPI(Resource):
    """ reset password api.

    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=str, required=True,
                                 help='not email provided', location='json')
        super(ResetPasswordAPI, self).__init__()

    def post(self):
        args = self.parser.parse_args()
        user = User.query.filter_by(email=args['email']).first_or_404()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                '重置密码',
                'auth/email/new_email',
                user=user,
                token=token,
                next=request.args.get('next'))
            return jsonify({"message": "一封邮件已经发送到你邮箱中，请确认重置密码"})
        return jsonify({"error": "no user"})


class InfoAPI(Resource):
    """ user info api.

    """
    @auth.login_required
    def get(self):
        info = {}
        info['email'] = g.current_user.email
        info['username'] = g.current_user.username
        info['join_time'] = g.current_user.join_time
        info['username_url'] = g.current_user.username_url
        return jsonify(info)


class TimeLineAPI(Resource):
    """ user timeline api.

    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, required=False,
                                 help='not append content provided',
                                 location=['json', 'args', 'headers'],
                                 default=1)
        super(TimeLineAPI, self).__init__()

    @auth.login_required
    def get(self, id):
        args = self.parser.parse_args()
        user = User.query.filter_by(id=id).first_or_404()

        per_page = current_app.config['PER_PAGE']
        page = args['page']
        offset = (page - 1) * per_page

        topics = user.topics.order_by(Topic.create_time.desc()).limit(per_page + offset)
        topics = topics[offset: offset + per_page]

        if not topics:
            return jsonify({"error": "no topics"})
        return jsonify({'topic': [topic.to_json() for topic in topics]})


# 话题相关
restful_api.add_resource(TopicApi, '/topics')
restful_api.add_resource(TopicIdApi, "/topic/<int:id>")
restful_api.add_resource(TopicAppendAPI, "/topic/append/<int:id>")
restful_api.add_resource(TopicEditAPI, "/topic/edit/<int:id>")
restful_api.add_resource(HotTopicAPI, "/topic/hot")

# 节点相关
restful_api.add_resource(NodeAPI, "/nodes")
restful_api.add_resource(NodeIdAPI, "/node/<int:id>")

# 用户登录注册
restful_api.add_resource(RegisterAPI, "/register")
restful_api.add_resource(ResetPasswordAPI, "/reset_password")

# 用户中心
restful_api.add_resource(InfoAPI, "/info")

# 用户时间线
restful_api.add_resource(TimeLineAPI, "/user/<int:id>/timeline")