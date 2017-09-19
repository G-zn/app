#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-04-03 15:00:25
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from flask import Blueprint
from flask import g, current_app


main = Blueprint('main', __name__)

from . import iaga, istp, errors
from ..common.iaga_db import IAGA_DB
from ..common.istp_db import ISTP_DB


@main.before_request
def get_db():
    # print "-" * 50
    flag = os.popen(
        "ps -aux|grep mongod|grep -v grep|awk '{print $1}'").readlines()
    if len(flag) > 0:
        g.IAGA_DB = IAGA_DB()
        g.ISTP_DB = ISTP_DB()
