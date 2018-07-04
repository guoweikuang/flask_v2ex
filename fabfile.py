# -*- coding: utf-8 -*-
from __future__ import with_statement
from fabric.api import *


env.user = 'ubuntu'
env.hosts = ['119.29.172.148']
env.key_filename = "/home/guoweikuang/project/my/daocloud"


def prepare_deploy():
    local('git add . && git commit -m "add fabric" ')
    local('git push origin develop')


def deploy():
    """ deploy project to remote.

    :return:
    """
    project_dir = '/home/guoweikuang/github'
    with settings(warn_only=True):
        if run('test -d %s' % project_dir).failed:
            run("git clone https://github.com/guoweikuang/flask_v2ex.git")
    with cd(project_dir):
        run("git clone https://github.com/guoweikuang/flask_v2ex.git")
        run('git pull')

