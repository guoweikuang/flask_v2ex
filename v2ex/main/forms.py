# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm 
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required, Length, Email 
from ..models import Topic, Node 
from v2ex import db 


class TopicForm(FlaskForm):
    """新建话题表单"""
    # nodes_id = [(node.id, node.content) for node in db.session.query(Node).all()]
    title = StringField('标题', validators=[Required(), Length(1, 64)])
    content = PageDownField('内容', validators=[Required()])
    node = SelectField('节点', coerce=int)
    submit = SubmitField('发布')

    def __init__(self, nodes, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        self.node.choices = [(node.id, node.title) for node in nodes]

    
class PostForm(FlaskForm):
    """新建话题表单"""
    # nodes_id = [(node.id, node.content) for node in db.session.query(Node).all()]
    title = StringField('标题', validators=[Required(), Length(1, 64)])
    content = TextAreaField('内容', validators=[Required()])
    node = SelectField('节点', coerce=int)
    submit = SubmitField('发布')

    def __init__(self, nodes, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.node.choices = [(node.id, node.title) for node in nodes]


class AppendForm(FlaskForm):
    """追加话题内容表单"""
    content = TextAreaField('内容', validators=[Required()])
    submit = SubmitField('追加内容')


class AppendPostForm(FlaskForm):
    """编辑话题表单"""
    content = TextAreaField('内容', validators=[Required()])
    submit = SubmitField('更新')


class CommentForm(FlaskForm):
    """评论表单"""
    content = TextAreaField('评论', validators=[Required()])
    submit = SubmitField('评论')
