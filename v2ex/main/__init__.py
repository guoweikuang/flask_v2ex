# -*- coding: utf-8 -*-
from flask import Blueprint
from v2ex.utils import format_time

main = Blueprint('main', __name__)
main.add_app_template_filter(format_time, 'format_time')

from . import views 

