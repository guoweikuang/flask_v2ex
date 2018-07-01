# -*- coding: utf-8 -*-
from fabric.api import local


def prepare_deploy():
    local('git add . && git commit -m "add fabric" ')
    local('git push origin develop')