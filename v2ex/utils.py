# -*- coding: utf-8 -*-
import re
import redis
import time 
from datetime import datetime

from .const import V2EX_COMMON_TOP_KEY
from .const import V2EX_COMMON_TOP_VALUE
from .const import V2EX_PEOPLE_NUMS
from .const import V2EX_TOPIC_NUMS
from .const import V2EX_BROWSE_NUMS
from .const import V2EX_COMMENT_NUMS
from .const import ONLINE_LAST_MINUTES
from .models import User, Notify, Topic, Node, Comment
from . import db 
from flask import url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView
from flask_login import current_user


r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def format_time(create_time):
    return create_time.strftime("%Y-%m-%d %H:%M:%S")


def add_user_links_in_content(content_html):
    """ add the @user with the link of user 
    
    :param content_html: markdown格式内容
    """    
    for name in re.findall(r"@(.*?)(?:\s|</\w+)", content_html):
        receiver = User.query.filter_by(username=name).first()
        if not receiver:
            continue
        
        content_html = re.sub(
            "@%s" % name,
            '@<a href="%s" class="mention">%s</a>' % (url_for('auth.info', uid=receiver.id), name),
            content_html)
    return content_html


def add_notify_in_content(content, sender_id, topic_id, comment_id=None, append_id=None):
    """ 生成评论消息提醒 
    """
    receivers = []
    for name in re.findall(r"@(.*?)(?:\s|$)", content):
        receiver = User.query.filter_by(username=name).first()
        if receiver:
            receivers.append(receiver)
    
    receivers = set(receivers)
    all_notify = []
    for u in receivers:
        all_notify.append(Notify(sender_id=sender_id, receiver_id=u.id, 
                                topic_id=topic_id, comment_id=comment_id, append_id=append_id))
    
    for new in all_notify:
        db.session.add(new)
    db.session.commit()


class AdminModelView(BaseView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_administator:
            return True 
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))

    def __init__(self, model, session, **kwargs):
        super(AdminModelView, self).__init__(User, session, **kwargs)


class UserView(ModelView):
    column_searchable_list = ["username", "email", "id"]
    column_filters = ["username", "email"]
    column_labels = {
        "id": "序号", 
        "username": "用户名",
        "email": "邮箱",
        "avatar_url": "头像链接",
        "join_time": "加入时间",
        "last_seen": "上次登录时间",
        "username_url": "个人链接"
    }
    column_list = ("id", "username", "email", "join_time", "avatar_url", "last_seen", "username_url")

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_administator:
            return True 
        return False

    def __init__(self, model, session, **kwargs):
        super(UserView, self).__init__(model, session, **kwargs)


class TopicView(ModelView):
    column_searchable_list = ["title", "user_id", "id", "node_id"]
    column_filters = ["title", "user_id", "node_id"]
    column_labels = {
        "id": "序号",
        "title": "标题",
        "content": "内容",
        "create_time": "创建时间",
        "click_num": "点击数",
        "reply_num": "回复数",
        "user_id": "用户ID",
        "node_id": "节点ID"
    }
    column_list = ("id", "title", "content", "create_time", "click_num", "reply_num", "user_id", "node_id")
    def __init__(self, model, session, **kwargs):
        super(TopicView, self).__init__(model, session, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_administator:
            return True 
        return False


class TopicAppendView(ModelView):
    column_searchable_list = ["topic_id", "id"]
    column_filters = ["topic_id"]
    column_labels = {
        "id": "序号",
        "content": "追加内容",
        "create_time": "追加时间",
        "topic_id": "话题ID"
    }
    column_list = ("id", "content", "create_time", "topic_id")

    def __init__(self, model, session, **kwargs):
        super(TopicAppendView, self).__init__(model, session, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_administator:
            return True 
        return False


class NodeView(ModelView):
    column_searchable_list = ["title", "id"]
    column_filters = ["title"]
    column_labels = {
        "id": "序号",
        "title": "节点名称",
        "description": "节点描述" 
    }
    column_list = ("id", "title", "description")
    def __init__(self, model, session, **kwargs):
        super(NodeView, self).__init__(model, session, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_administator:
            return True 
        return False


class CommentView(ModelView):
    column_searchable_list = ["user_id", "id", "topic_id"]
    column_filters = ["topic_id", "user_id"]
    column_labels = {
        "id": "序号",
        "content": "评论内容", 
        "create_time": "评论时间",
        "user_id": "用户ID",
        "topic_id": "话题ID"
    }
    column_list = ("id", "content", "create_time", "user_id", "topic_id")
    def __init__(self, model, session, **kwargs):
        super(CommentView, self).__init__(model, session, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_administator:
            return True 
        return False


class NotifyView(ModelView):
    column_searchable_list = ["topic_id", "id", "read_flag"]
    column_filters = ["topic_id", "read_flag"]
    column_list = ("id", "create_time", "read_flag", "topic_id")
    def __init__(self, model, session, **kwargs):
        super(NotifyView, self).__init__(model, session, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_administator:
            return True 
        return False


def get_content_from_redis(key_name, key_type):
    """取top数据"""
    key = V2EX_COMMON_TOP_KEY % key_name
    value = V2EX_COMMON_TOP_VALUE % key_name
    content = r.llen(key)
    if not content:
        if key_type == 'Node':
            nodes = Node.query.limit(10)
            for node in nodes:
                r.lpush(key, node.id)
                r.lpush(value, node.title)
            r.expire(key, 60 * 60)
            r.expire(key, 60 * 60)
        elif key_type == 'Topic':
            topics = Topic.query.order_by(Topic.reply_num).limit(10)
            for topic in topics:
                r.lpush(key, topic.id)
                r.lpush(value, topic.title)
        r.expire(key, 60 * 30)
        r.expire(value, 60 * 30)
    keys = r.lrange(key, 0, 10)
    values = r.lrange(value, 0, 10)
    contents = [(tid, title) for tid, title in zip(keys, values)]
    return contents
            

def get_v2ex_people_num():
    key = r.exists(V2EX_PEOPLE_NUMS)
    if not key:
        peoples = User.query.count()
        r.set(V2EX_PEOPLE_NUMS, peoples)
        r.expire(V2EX_PEOPLE_NUMS, 60 * 3)
    else:
        peoples = r.get(V2EX_PEOPLE_NUMS)
    return peoples 


def get_v2ex_topic_num():
    key = r.exists(V2EX_TOPIC_NUMS)
    if not key:
        topic_num = Topic.query.count()
        r.set(V2EX_TOPIC_NUMS, topic_num)
        r.expire(V2EX_TOPIC_NUMS, 60 * 2)
    else:
        topic_num = r.get(V2EX_TOPIC_NUMS)
    return topic_num

    
def get_v2ex_comment_num():
    key = r.exists(V2EX_COMMENT_NUMS)
    if not key:
        comment_num = Comment.query.count()
        print(comment_num)
        r.set(V2EX_COMMENT_NUMS, comment_num)
        r.expire(V2EX_COMMENT_NUMS, 60)
        return comment_num
    else:
        comment_num = r.get(V2EX_COMMENT_NUMS)
    return comment_num


def get_v2ex_browse_num():
    key = r.exists(V2EX_BROWSE_NUMS)
    if not key:
        r.set(V2EX_BROWSE_NUMS, 1)
        return r.get(V2EX_BROWSE_NUMS)
    else:
        r.incr(V2EX_BROWSE_NUMS)
        return r.get(V2EX_BROWSE_NUMS)
        

def get_top_hot_node():
    nodes = Node.query.all()
    top = {}
    for node in nodes:
        top[node.id] = (node.title, node.topics.count())
    top = sorted(top.items(), key=lambda a: a[1][1], reverse=True)
    return top[:10]


def mark_online(user_id):
    now = int(time.time())
    expires = now + (ONLINE_LAST_MINUTES * 60) + 10
    all_user_key = 'v2ex:online:users:%d' % (now // 60)
    user_key = 'v2ex:online:activitys:%s' % user_id

    p = r.pipeline()
    p.sadd(all_user_key, user_id)
    p.set(user_key, now)
    p.expireat(all_user_key, expires)
    p.expireat(user_key, expires)
    p.execute()


def get_user_last_activity(user_id):
    last_active = r.get('v2ex:online:activitys:%s' % user_id)
    if last_active is None:
        return None
    return datetime.utcfromtimestamp(int(last_active))


def get_online_users():
    current = int(time.time()) // 60
    minutes = range(ONLINE_LAST_MINUTES)
    return r.sunion(["v2ex:online:users:%d" % (current - x) for x in minutes])

