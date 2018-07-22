# -*- coding: utf-8 -*-
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

V2EX_NODES_TOP = "v2ex:nodes:top"
V2EX_NODES_TOP_KEY = "v2ex:nodes:top:key"
V2EX_NODES_TOP_VALUE = "v2ex:nodes:top:value"

V2EX_TOPIC_TOP = "v2ex:topic:top"
V2EX_TOPIC_TOP_KEY = "v2ex:topic:top:key"
V2EX_TOPIC_TOP_VALUE = "v2ex:topic:top:value"

V2EX_COMMON_TOP_KEY = "v2ex:%s:top:key"
V2EX_COMMON_TOP_VALUE = "v2ex:%s:top:value"

V2EX_PEOPLE_NUMS = "v2ex:people:nums"

V2EX_TOPIC_NUMS = "v2ex:topic:nums"

V2EX_COMMENT_NUMS = "v2ex:comment:nums"

V2EX_BROWSE_NUMS = "v2ex:browse:nums"

V2EX_MAX_ONLINE_NUMS = "v2ex:online:users:max"

V2EX_ARTICLE_LIKE_NUM = "v2ex:article:%s:like"

V2EX_ARTICLE_UNLIKE_NUM = "v2ex:article:%s:unlike"

V2EX_ARTICLE_USER_LIKE = "article:%s:user:%s:like"

V2EX_ARTICLE_USER_UNLIKE = "article:%s:user:%s:unlike"

V2EX_ARTICLE_LIKE = "v2ex:article:like"

V2EX_ARTICLE_UNLIKE = "v2ex:article:unlike"

ONLINE_LAST_MINUTES = 5
