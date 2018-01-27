# -*- coding: utf-8 -*-
from flask import g
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    if email == '':
        g.current_user = AnonymousUser()
        return True

    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    g.current_user = user
    return user.verify_password(password)