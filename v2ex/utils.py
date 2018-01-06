# -*- coding: utf-8 -*-
import re
from datetime import datetime

from .models import User, Notify
from . import db 
from flask import url_for

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

