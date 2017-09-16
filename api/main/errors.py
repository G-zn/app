#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-04-08 20:03:18
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import sys
from flask import request, jsonify
from . import main
from flask import g


@main.app_errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found  ' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


@main.app_errorhandler(500)
def internal_server_error():
    message = {
        'status': 500,
        'message': 'internal server error'
    }
    resp = jsonify(message)
    resp.status_code = 500
    return resp
