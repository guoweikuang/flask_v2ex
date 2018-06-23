# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    """登录表单"""
    email = StringField('邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class RegisterForm(FlaskForm):
    """注册表单"""
    email = StringField('邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField(
        '用户名',
        validators=[
            Required(),
            Length(1, 64),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, "用户名必须是字母，数字，小数点或下划线")
        ])
    password = PasswordField(
        '密码', validators=[Required(),
                          EqualTo(u'password2', message='密码必须一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        """验证邮箱地址是否存在于数据库"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册!')

    def validate_username(self, field):
        """验证用户名是否存在"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用!')


class ResetPasswordForm(FlaskForm):
    """重置密码表单"""
    email = StringField('邮箱', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('修改密码')


class ResetPasswordRequestForm(FlaskForm):
    """忘记密码表单(修改密码)"""
    email = StringField('邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(
        '密码', validators=[Required(),
                          EqualTo('password2', message='密码必须一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('修改密码')


class ChangePasswordForm(FlaskForm):
    """知道原密码下的修改密码"""
    old_password = PasswordField('原密码', validators=[Required()])
    new_password = PasswordField(
        '新密码',
        validators=[Required(),
                    EqualTo('new_password2', message='密码必须一致')])
    new_password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('修改密码')


class UploadForm(FlaskForm):
    """上传头像"""
    pass


class UserInfoForm(FlaskForm):
    """用户个人信息"""
