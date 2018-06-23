# -*- coding: utf-8 -*-
from flask_mail import Message
from flask import current_app, render_template
from . import mail


def send_email(to, subject, template_name, **kwargs):
    """发送邮件"""
    app = current_app._get_current_object()
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template_name + '.txt', **kwargs)
    msg.html = render_template(template_name + '.html', **kwargs)
    mail.send(msg)

