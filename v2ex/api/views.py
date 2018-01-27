# -*- coding: utf-8 -*-
from flask import jsonify, g, request, current_app, url_for
from flask_restful import Resource, Api, reqparse

from .. import db
from ..models import User, Topic, Node, Notify
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
        topics = Topic.query.order_by(Topic.create_time.desc()).limit(per_page+offset)
        topics = topics[offset:offset+per_page]
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
    def get(self, id):
        topic = Topic.query.filter_by(id=id).first()
        if topic is None:
            return jsonify({"error": "no topic"})
        return jsonify(topic.to_json())


restful_api.add_resource(TopicApi, '/topics')
restful_api.add_resource(TopicIdApi, "/topic/<int:id>")