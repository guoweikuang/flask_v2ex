# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~
flask_v2ex api moudle.

@author guoweikuang
"""
from flask import Flask

from flask_restful import Api
from . import api


rest_api = Api(api)


# 话题相关
rest_api.add_resource(TopicApi, '/topics')
rest_api.add_resource(TopicIdApi, "/topic/<int:id>")
rest_api.add_resource(TopicAppendAPI, "/topic/append/<int:id>")
rest_api.add_resource(TopicEditAPI, "/topic/edit/<int:id>")
rest_api.add_resource(HotTopicAPI, "/topic/hot")

