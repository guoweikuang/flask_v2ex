# -*- coding: utf-8 -*-
from flask import request, url_for, redirect, render_template, current_app, flash,\
        abort
from flask_login import login_required, current_user 
from flask_paginate import Pagination
from ..models import db, User, Topic, Node, TopicAppend 
from . import main 
from .forms import TopicForm, PostForm, AppendForm, AppendPostForm


@main.route('/', methods=['GET', 'POST'])
def index():
    per_page = current_app.config['PER_PAGE']
    page = int(request.args.get('page', 1, type=int))
    offset = (page - 1) * per_page 
    topics = Topic.query.order_by(Topic.create_time.desc()).limit(per_page+offset)
    topics = topics[offset:offset+per_page]
    pagination = Pagination(page=page, total=Topic.query.count(),
                        per_page=per_page,
                        record_name='topics',
                        CSS_FRAMEWORK='bootstrap',
                        bs_version=3)
    return render_template('main/index.html', pagination=pagination, topics=topics)


@main.route('/topic/hot', methods=['GET', 'POST'])
def hot():
    per_page = current_app.config['PER_PAGE']
    page = int(request.args.get('page', 1, type=int))
    offset = (page-1) * per_page 

    topics = Topic.query.order_by(Topic.reply_num.desc()).limit(per_page+offset)
    topics = topics[offset: offset+per_page]
    pagination = Pagination(page=page, total=Topic.query.count(),
                            per_page=per_page,
                            record_name='topics',
                            CSS_FRAMEWORK='bootstrap',
                            bs_version=3)
    return render_template('main/index.html', pagination=pagination, topics=topics)

@main.route('/topic/create', methods=['GET', 'POST'])
@login_required 
def create_topic():
    nodes = Node.query.all()
    form = TopicForm(nodes)
    if form.validate_on_submit():
        print(form.node.data)
        print(current_user._get_current_object())
        topic = Topic(title=form.title.data,
                      content=form.content.data,
                      user=current_user._get_current_object(),
                      node_id=form.node.data)
        db.session.add(topic)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('main/create_topic.html', nodes=nodes, form=form)


@main.route('/topic/new', methods=['GET', 'POST'])
@login_required 
def new_topic():
    nodes = Node.query.all()
    form = PostForm(nodes)
    if form.validate_on_submit():
        topic = Topic(title=form.title.data,
                      content=form.content.data,
                      user=current_user._get_current_object(),
                      node_id=form.node.data)
        db.session.add(topic)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('main/new.html', nodes=nodes, form=form)


@main.route('/topic/<int:tid>', methods=['GET', 'POST'])
def topic_view(tid):
    per_page = current_app.config['PER_PAGE']
    page = int(request.args.get('page', 1, type=int))
    offset = (page - 1) * per_page 

    topic = Topic.query.filter_by(id=tid).first_or_404()
    
    topic.click_num += 1
    db.session.commit()
    return render_template('main/topic.html',topic=topic)


@main.route('/topic/append/<int:tid>', methods=['GET', 'POST'])
@login_required
def topic_append(tid):
    topic = Topic.query.filter_by(id=tid).first_or_404()

    if current_user.id != topic.user.id:
        abort(403)
    form = AppendForm()
    if form.validate_on_submit():
        append = TopicAppend(content=form.content.data,
                             topic_id=tid)
        db.session.add(append)
        db.session.commit()
        return redirect(url_for('main.topic_view', tid=tid))
    return render_template('main/append.html', topic=topic, form=form)
        

@main.route('/topic/edit/<int:tid>', methods=['GET', 'POST'])
@login_required 
def topic_edit(tid):
    topic = Topic.query.filter_by(id=tid).first_or_404()
    nodes = Node.query.all()
    if current_user.id != topic.user.id:
        abort(403)
    
    form = AppendPostForm()
    if form.validate_on_submit():
        topic.content = form.content.data 
        db.session.add(topic)
        db.session.commit()
        return redirect(url_for('main.topic_view', tid=tid))
    form.content.data = topic.content
    return render_template('main/topic_edit.html', topic=topic, form=form)



@main.route('/topic/test', methods=['GET', 'POST'])
def test():
    return render_template('main/test.html')
