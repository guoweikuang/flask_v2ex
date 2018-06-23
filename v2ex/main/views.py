# -*- coding: utf-8 -*-
from flask import request, url_for, redirect, render_template, current_app, flash,\
        abort
from flask_login import login_required, current_user
from flask_paginate import Pagination
from ..models import db, User, Topic, Node, TopicAppend, Comment, AnonymousUser
from . import main
from .. import search1
from .forms import TopicForm, PostForm, AppendForm, AppendPostForm, CommentForm

from ..utils import add_user_links_in_content, add_notify_in_content, get_content_from_redis, \
                    get_v2ex_people_num, get_v2ex_topic_num, get_v2ex_comment_num, \
                    get_v2ex_browse_num, get_top_hot_node, mark_online, get_online_users, \
                    get_top_topic, get_tag


# import redis
# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@main.context_processor
def get_online_count():
    """ get online people number.

    :return:
    """
    return dict(online_user=get_online_users())


@main.before_request
def mark_current_user_online():
    mark_online(request.remote_addr)


@main.route('/', methods=['GET', 'POST'])
def index():
    """ index page view.

    :return:
    """
    per_page = current_app.config['PER_PAGE']
    page = int(request.args.get('page', 1, type=int))
    offset = (page - 1) * per_page
    topics = Topic.query.order_by(Topic.create_time.desc()).limit(per_page+offset)
    topics = topics[offset:offset+per_page]
    if page == 1:
        topics = get_top_topic(topics)
    pagination = Pagination(page=page, total=Topic.query.count(),
                        per_page=per_page,
                        record_name='topics',
                        CSS_FRAMEWORK='bootstrap',
                        bs_version=4)

    top = get_content_from_redis(key_name="topic", key_type="Topic")
    nodes = Node.query.all()
    nodes = get_content_from_redis(key_name="nodes", key_type="Node")
    nodes = get_tag()

    people_num = get_v2ex_people_num()
    topic_num = get_v2ex_topic_num()
    comment_num = get_v2ex_comment_num()
    browse_num = get_v2ex_browse_num()
    top_nodes = get_top_hot_node()
    online_users = get_online_users()

    return render_template('main/index.html',
                            pagination=pagination,
                            topics=topics, nodes=nodes, top=top,
                            people_num=people_num, topic_num=topic_num,
                            browse_num=browse_num, comment_num=comment_num,
                            top_nodes=top_nodes, online=online_users)


@main.route('/topic/hot', methods=['GET', 'POST'])
def hot():
    """ hot topic view.

    :return:
    """
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
    top = get_content_from_redis(key_name="topic", key_type="Topic")
    nodes = get_content_from_redis(key_name="nodes", key_type="Node")
    people_num = get_v2ex_people_num()
    topic_num = get_v2ex_topic_num()
    comment_num = get_v2ex_comment_num()
    browse_num = get_v2ex_browse_num()
    top_nodes = get_top_hot_node()
    online_users = get_online_users()

    return render_template('main/index.html',
                            pagination=pagination,
                            topics=topics, nodes=nodes, top=top,
                            topic_num=topic_num, people_num=people_num,
                            browse_num=browse_num, comment_num=comment_num,
                            top_nodes=top_nodes, online=online_users)


@main.route('/topic/create', methods=['GET', 'POST'])
@login_required
def create_topic():
    """ create topic from register user.

    :return:
    """
    nodes = Node.query.all()
    form = TopicForm(nodes)
    if form.validate_on_submit():
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
    """ topic detail content.

    :param tid: topic id
    :return:
    """
    per_page = current_app.config['PER_PAGE']
    page = int(request.args.get('page', 1, type=int))
    offset = (page - 1) * per_page

    topic = Topic.query.filter_by(id=tid).first_or_404()
    comments = topic.comments.order_by(Comment.create_time.desc()).limit(per_page+offset)
    # comments = Comment.query.order_by(Comment.create_time.desc()).limit(per_page+offset)
    comments = comments[offset: offset+per_page]
    pagination = Pagination(page=page, total=topic.comments.count(),
                            per_page=per_page,
                            record_name="comments",
                            CSS_FRAMEWORK="bootstrap",
                            bs_version=3)

    form = CommentForm()
    if not current_user.is_anonymous:
        if form.validate_on_submit():
            content = add_user_links_in_content(form.content.data)
            comment = Comment(content=content,
                              user=current_user._get_current_object(),
                              topic=topic)
            topic.reply_num += 1
            db.session.add(comment)
            db.session.commit()
            add_notify_in_content(form.content.data, current_user.id, tid, comment.id)
            return redirect(url_for('main.topic_view', tid=tid))
        topic.click_num += 1
        db.session.commit()
    else:
        flash("请先登录后评论")
    return render_template('main/topic.html', topic=topic, pagination=pagination,
                            comments=comments, form=form)


@main.route('/topic/append/<int:tid>', methods=['GET', 'POST'])
@login_required
def topic_append(tid):
    """ topic append view.

    :param tid: topic id
    :return:
    """
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
    """ topic edit view.

    :param tid: topic id
    :return:
    """
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


@main.route('/nodes')
def nodes():
    """ all node view.

    :return:
    """
    nodes = Node.query.all()
    return render_template('main/nodes.html', nodes=nodes)


@main.route('/node/<int:nid>')
def node_view(nid):
    """ node view.

    :param nid: node id
    :return:
    """
    node = Node.query.filter_by(id=nid).first_or_404()
    node_title = node.title
    per_page = current_app.config['PER_PAGE']
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    topics = Topic.query.filter_by(node_id=nid).order_by(
        Topic.create_time.desc()).limit(per_page+offset)
    topics = topics[offset:offset+per_page]
    pagination = Pagination(page=page,
                        total=Topic.query.filter_by(node_id=nid).count(),
                        per_page=per_page,
                        record_name="comments",
                        CSS_FRAMEWORK="bootstrap",
                        bs_version=3)
    return render_template('main/node_view.html',
                            topics=topics,
                            node_title=node_title,
                            pagination=pagination, node=node)


@main.route('/search/<keywords>')
def search(keywords):
    """ search view .

    :param keywords:
    :return:
    """
    results = search1.whoosh_search(Topic, query=keywords, fields=["title"], limit=20)
    results = Topic.query.msearch(keywords, fields=["title"], limit=20)

    per_page = current_app.config["PER_PAGE"]
    page = int(request.args.get("page", 1))
    offset = (page-1) * per_page
    topics = results[offset:offset+per_page]
    pagination = Pagination(page=page,
                    total=results.count(),
                    per_page=per_page,
                    record_name="comments",
                    CSS_FRAMEWORK="bootstrap",
                    bs_version=3)
    return render_template("main/index.html", topics=topics, pagination=pagination)


@main.route('/topic/test', methods=['GET', 'POST'])
def test():
    return render_template('main/test.html')
