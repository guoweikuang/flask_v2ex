# -*- coding: utf-8 -*-
"""
认证模块视图
"""
import os
from PIL import Image

from flask import render_template, url_for, flash, request, redirect, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug import secure_filename

from .. import db
from . import auth
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegisterForm, ResetPasswordForm, \
    ResetPasswordRequestForm, ChangePasswordForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """登录视图"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('用户登录成功')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid password or username!')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """登出视图"""
    logout_user()
    flash('你已经登出')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """注册视图"""
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """重置密码"""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                '重置密码',
                'auth/email/new_email',
                user=user,
                token=token,
                next=request.args.get('next'))
        flash('一封邮件已经发送到你邮箱中，请确认重置密码')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset_password_request/<token>', methods=['GET', 'POST'])
def reset_password_request(token):
    """修改密码确认"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('密码已经修改成功')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """在知道原密码情况下修改密码"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('你的密码已经更新')
            return redirect(url_for('auth.login'))
        else:
            flash('原密码无效!')
    return render_template('auth/change_password.html', form=form)


def allow_file(filename, allowed_file):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in allowed_file


@auth.route('/setting/avatar', methods=['GET', 'POST'])
@login_required
def setting_avatar():
    if request.method == 'GET':
        return render_template('auth/setting_avatar.html', form=None)
    if request.method == 'POST':
        _file = request.files['file']
        allowed_file = current_app.config['ALLOWED_EXTENSIONS']
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if _file and allow_file(_file.filename, allowed_file):
            size = (80, 80)
            im = Image.open(_file)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save('%s/%s.png' % (upload_folder, current_user.id), 'PNG')

            image_path = os.path.join(upload_folder,
                                      '%d.png' % current_user.id)
            unique_mark = os.stat(image_path).st_mtime
            current_user.avatar_url = url_for(
                'static',
                filename='uploads/%s.png' % current_user.id,
                t=unique_mark)
            db.session.commit()
            return render_template('auth/setting_avatar.html')
        else:
            return render_template('auth/setting_avatar.html')


@auth.route('/setting/info', methods=['GET', 'POST'])
@login_required
def setting_info():
    email = current_user.email
    username = current_user.username
    join_time = current_user.join_time
    username_url = current_user.username_url
    return render_template(
        'auth/setting_info.html',
        email=email,
        username=username,
        join_time=join_time,
        username_url=username_url)
