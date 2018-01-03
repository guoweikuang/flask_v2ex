# -*- coding: utf-8 -*-
import re
from datetime import datetime

from .models import User 
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

