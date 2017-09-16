#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-04-09 12:57:35
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from flask import Flask
from flask_script import Manager
from api import create_app
from flask_cache import Cache


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@manager.command
def test():
    """Run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
