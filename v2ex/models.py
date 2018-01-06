# -*- coding: utf-8 -*-
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from markdown import markdown
import bleach

from . import db
from . import login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar_url = db.Column(
        db.String(128),
        default="http://www.gravatar.com/avatar/")
    join_time = db.Column(db.DateTime(), default=datetime.utcnow())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow())
    is_superuser = db.Column(db.Boolean, default=False)
    username_url = db.Column(db.String(64), nullable=True)

    topics = db.relationship('Topic', backref="user", lazy='dynamic')
    comments = db.relationship("Comment", backref="user", lazy="dynamic")

   # unread_notify = db.relationship("Notify", backref="user", lazy="dynamic")

    @property
    def password(self):
        raise AttributeError('password not allow to reading!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        """生成确认令牌"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        """重置密码"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except BaseException:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def extract_read_notify(self):
        notifies = Notify.query.filter_by(id=self.id).filter_by(read_flag=True)
        if notifies:
            return notifies.count()
        else:
            return 0

    def extract_unread_notify(self):
        notifies = Notify.query.filter_by(id=self.id).filter_by(read_flag=False)
        if notifies:
            return notifies.count()
        else:
            return 0

    def __repr__(self):
        return '<User %s>' % self.username


class Topic(db.Model):
    __tablename__ = 'topics'
    __searchable__ = ["title", "content"]
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    content = db.Column(db.Text())
    content_html = db.Column(db.Text())
    create_time = db.Column(db.DateTime(), index=True, default=datetime.now)
    last_replied = db.Column(db.DateTime())
    click_num = db.Column(db.Integer, default=0)
    reply_num = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'))

    appends = db.relationship('TopicAppend', backref="topic", lazy='dynamic')
    comments = db.relationship('Comment', backref="topic", lazy="dynamic")

    def node(self):
        return Node.query.filter_by(id=self.node_id).first()

    def user(self):
        return User.query.filter_by(id=self.user_id).first()

    def extract_appends(self):
        if self.appends:
            all_appends = TopicAppend.query.filter_by(topic_id=self.id)
            return all_appends
        else:
            return []

    # markdown的处理
    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h4', 'h5', 'p']
        target.content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def __repr__(self):
        return '<Topic: %s>' % self.title


db.event.listen(Topic.content, 'set', Topic.on_change_body)


class Node(db.Model):
    """节点"""

    def __init__(self, title, description):
        self.title = title
        self.description = description

    __tablename__ = 'node'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.Text())
    topics = db.relationship('Topic', backref='node', lazy='dynamic')

    def __unicode__(self):
        return self.title


class TopicAppend(db.Model):
    """追加内容"""
    def __init__(self, content, topic_id):
        self.content = content 
        self.topic_id = topic_id 
        self.create_time = datetime.now()

    __tablename__ = 'append'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime(), default=datetime.utcnow)
    content = db.Column(db.Text())
    content_html = db.Column(db.Text())
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))

    # markdown的处理
    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h4', 'h5', 'p']
        target.content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(TopicAppend.content, 'set', TopicAppend.on_change_body)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Comment(db.Model):
    """评论"""
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text())
    content_html = db.Column(db.Text())
    create_time = db.Column(db.DateTime(), default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))

    # markdown的处理
    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h4', 'h5', 'p']
        target.content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def user(self):
        return User.query.filter_by(id=self.user_id).first()

db.event.listen(Comment.content, 'set', Comment.on_change_body)


class Notify(db.Model):
    """提醒"""
    __tablename__ = 'notify'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime(), default=datetime.utcnow)
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer, nullable=True)
    topic_id = db.Column(db.Integer, nullable=True)
    append_id = db.Column(db.Integer, nullable=True)
    read_flag = db.Column(db.Boolean, default=False)

    @property
    def topic(self):
        return Topic.query.filter_by(id=self.topic_id).first()

    @property
    def sender(self):
        return User.query.filter_by(id=self.sender_id).first()



