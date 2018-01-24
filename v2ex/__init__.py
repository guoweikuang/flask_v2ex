# -*- coding: utf-8 -*-
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail 
from flask_pagedown import PageDown
from flask_msearch import Search
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_moment import Moment
from flask_babelex import Babel 
from config import config 


db = SQLAlchemy()
search1 = Search(db=db)
bootstrap = Bootstrap()
login_manager = LoginManager()
mail = Mail()
pagedown = PageDown()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
admin = Admin(name="后台管理")
moment = Moment()
babel = Babel()


from .models import User, Topic, TopicAppend, Node, Notify, Comment
from .utils import UserView, TopicView, TopicAppendView, CommentView, NodeView, NotifyView


def add_view_to_admin(model_name):
    pass

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)
    search1.init_app(app)
    admin.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # admin.add_view(AdminModelView(User, db.session, name="管理员"))
    admin.add_view(UserView(User, db.session, name="用户"))
    admin.add_view(TopicView(Topic, db.session, name="话题"))
    admin.add_view(TopicAppendView(TopicAppend, db.session, name="话题追加"))
    admin.add_view(NodeView(Node, db.session, name="节点"))
    admin.add_view(NotifyView(Notify, db.session, name="提醒"))
    admin.add_view(CommentView(Comment, db.session, name="评论"))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api/v1.0")
    
    return app 


