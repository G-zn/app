#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-06-25 16:23:35
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from flask import Flask
from config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
