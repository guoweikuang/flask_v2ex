# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~
index page module.

@author guoweikuang
"""
from flask import current_app
from flask import request
from flask import jsonify
from flask import g

from flask_restful import Resource
from flask_restful import reqparse

from ... import db
from ...models import TopicAppend
from ...models import Topic
from ...models import Comment
from ...utils import add_notify_in_content
from ..common.authentication import auth


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
    pass
