# -*- coding: utf-8 -*-
"""
Flask-V2ex Config
~~~~~~~~~~~~~~~~~~~

projects config model

@author guoweikuang
@date 2017-11-7

"""
import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """基本配置文件，其它配置类从该类继承"""

    # sqlalchemy相关配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or "%^&453969388@#$%^%"
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True 

    # 管理员邮箱相关配置
    FLASK_ADMIN = '673411814@qq.com'
    FLASK_MAIL_SUBJECT_PREFIX = '[Guoweikuang]'
    FLASK_MAIL_SENDER = '郭伟匡<156022005343@163.com>'

    # 邮箱相关配置
    MAIL_DEFAULT_SENDER = '15602200534@163.com'
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True 
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '15602200534@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your password'
    
    # 国际化与本地化
    BABEL_DEFAULT_LOCALE = 'zh_CN'
    BABEL_DEFAULT_TIMEZONE = 'CST'

    UPLOAD_FOLDER = os.path.join(basedir, 'v2ex/static/uploads')
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

    # 搜索
    WHOOSH_BASE = "whoosh_index"
    WHOOSH_ENABLE = True

    PER_PAGE = 20

    ONLINE_LAST_MINUTES = 5

    @staticmethod
    def init_app(app):
        pass 


class DevelopmentConfig(Config):
    """开发模式配置"""

    DEBUG = True 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
            'sqlite:////' + os.path.join(basedir, 'data-dev.sqlite')


class ProductionConfig(Config):
    """生产者模式配置"""

    DEBUG = False 
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRO_DATABASE_URL') or \
            'sqlite:////' + os.path.join(basedir, 'data.sqlite')


class TestingConfig(Config):
    """测试模式配置"""
    TESTING = True
    DEBUG = True 
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATEBASE_URL') or \
            'sqlite:////' + os.path.join(basedir, 'date-test.sqlite')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}

