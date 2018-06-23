# -*- coding: utf-8 -*-
from flask import jsonify


def page_not_found():
    return jsonify({"error": "page not found"})


def bad_request(message):
    """404 error request"""
    response = jsonify({"error": "bad request", "message": message})
    return response


def internal_server_error():
    """500 internal server error"""
    response = jsonify({"error": "internal server error"})
    return response