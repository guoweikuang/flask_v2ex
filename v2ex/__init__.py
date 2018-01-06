# -*- coding: utf-8 -*-
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail 
from flask_pagedown import PageDown
from flask_msearch import Search
from config import config 


db = SQLAlchemy()
search1 = Search(db=db)
bootstrap = Bootstrap()
login_manager = LoginManager()
mail = Mail()
pagedown = PageDown()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


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

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app 


