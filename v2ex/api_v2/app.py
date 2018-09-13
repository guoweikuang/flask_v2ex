# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~
flask_v2ex api moudle.

@author guoweikuang
"""

from flask_restful import Api
from . import api_v2


from .resource.main import TopicApi
from .resource.main import TopicAppendAPI
from .resource.main import TopicIdApi
from .resource.main import TopicEditAPI
from .resource.main import HotTopicAPI
from .resource.auth import UserInfoAPI

rest_api = Api(api_v2)


# 话题相关
rest_api.add_resource(TopicApi, '/topics')
rest_api.add_resource(TopicIdApi, "/topic/<int:id>")
rest_api.add_resource(TopicAppendAPI, "/topic/append/<int:id>")
rest_api.add_resource(TopicEditAPI, "/topic/edit/<int:id>")
rest_api.add_resource(HotTopicAPI, "/topic/hot")

# 用户相关
rest_api.add_resource(UserInfoAPI, '/user')
