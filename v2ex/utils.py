# -*- coding: utf-8 -*-
import re
import redis
from datetime import datetime

from .const import V2EX_COMMON_TOP_KEY
from .const import V2EX_COMMON_TOP_VALUE
from .models import User, Notify, Topic, Node
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
    print(content)
    for name in re.findall(r"@(.*?)(?:\s|$)", content):
        print(name)
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
            
        
