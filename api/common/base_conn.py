#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-04-20 20:50:10
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import sys
from pymongo import MongoClient

mongodb_url = "mongodb://127.0.0.1:27017/"


def getConn(database_name):
    client = MongoClient(mongodb_url)
    db = client[database_name]
    return db


def getCollection(collection_name):
    db = getConn("IAGA_Release")
    collection = db[collection_name]
    return collection
