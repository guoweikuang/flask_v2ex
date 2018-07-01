# -*- coding: utf-8 -*-
from __future__ import with_statement
from fabric.api import local
from fabric.api import run
from fabric.api import settings
from fabric.api import cd


def prepare_deploy():
    local('git add . && git commit -m "add fabric" ')
    local('git push origin develop')


def deploy(project_link):
    """ deploy project to remote.

    :return:
    """
    project_dir = '/home/guoweikuang/github'
    with settings(warn_only=True):
        if run('test -d %s' % project_dir).failed:
            run("git clone https://github.com/guoweikuang/flask_v2ex.git")
    with cd(project_dir):
        run('git pull')

