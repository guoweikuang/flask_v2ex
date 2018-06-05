# -*- coding: utf-8 -*-
from flask import Blueprint


api = Blueprint('api_v2', __name__)

from .resource import main, auth