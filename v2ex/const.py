# -*- coding: utf-8 -*-
import redis 

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


V2EX_NODES_TOP_KEY = "v2ex:nodes:top:key"
V2EX_NODES_TOP_VALUE = "v2ex:nodes:top:value"

V2EX_TOPIC_TOP_KEY = "v2ex:topic:top:key"
V2EX_TOPIC_TOP_VALUE = "v2ex:topic:top:value"

V2EX_COMMON_TOP_KEY = "v2ex:%s:top:key"
V2EX_COMMON_TOP_VALUE = "v2ex:%s:top:value"

V2EX_PEOPLE_NUMS = "v2ex:people:nums"

V2EX_TOPIC_NUMS = "v2ex:topic:nums"

V2EX_COMMENT_NUMS = "v2ex:comment:nums"

V2EX_BROWSE_NUMS = "v2ex:browse:nums"

ONLINE_LAST_MINUTES = 5
        
