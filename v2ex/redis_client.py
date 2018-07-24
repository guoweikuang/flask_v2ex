# -*- coding: utf-8 -*-
import redis


class RedisPool(object):
    def __init__(self, redis_config):
        self.redis_config = redis_config
        if not hasattr(RedisPool, 'pool'):
            RedisPool.get_redis_conn()
        self.conn = redis.Redis(connection_pool=RedisPool.pool)


    @staticmethod
    def get_redis_conn(redis_config):
        RedisPool.pool = redis.ConnectionPool(host=redis_config['host'],
                                              password=redis_config['password'],
                                              port=redis_config['port'],
                                              db=redis_config['db'])

