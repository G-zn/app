#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-09-10 15:55:16
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import json
import time
import urllib
import unittest
from api import create_app
from pymongo import MongoClient

mongo = MongoClient()
db = mongo['CDF_Release']


def get_testcases():
    with open("./tests/testcase_istp.json") as fp:
        testcases = json.load(fp)
    return testcases


class test_istp(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing").test_client()
        self.testcases = get_testcases()
        self.flag = os.popen(
            "ps -aux|grep mongod|grep -v grep|awk '{print $1}'").readlines()

    def tearDown(self):
        if len(self.flag) == 0:
            print "can't connect to database,whether the information that system\
            returned correspond to this situation testing module have done."

    def test_sources(self):
        for value in self.testcases["sources"]["values"]:
            geturl = self.testcases["sources"]["URL"]
            if len(self.flag) == 0:
                result = "can't connect to background database service."
            else:
                condition = {}
                if "instrument_type" in value:
                    condition["Instrument_type"] = value["instrument_type"]
                result = db.get_collection("attrs").distinct(
                    "Source_name", condition)
            parameters = urllib.urlencode(value)
            if parameters != "":
                geturl = geturl + "?" + parameters
            response = self.app.get(geturl)
            if response.status_code == 200:
                res = json.loads(response.data)
                tmp = []
                for i in res["sources"]:
                    if i["Source_name"] not in result:
                        self.assertTrue(False)
                if len(result) != len(res["sources"]):
                    self.assertTrue(False)
            else:
                res = json.loads(response.data)
                if res["error"] != result:
                    self.assertTrue(False)

    def test_instrument_types(self):
        for value in self.testcases["instrument_types"]["values"]:
            geturl = self.testcases["instrument_types"]["URL"]
            if len(self.flag) == 0:
                result = "can't connect to background database service."
            else:
                condition = {}
                if "source_name" in value:
                    condition["Source_name"] = value["source_name"]
                result = db.get_collection("attrs").distinct(
                    "Instrument_type", condition)
            parameters = urllib.urlencode(value)
            if parameters != "":
                geturl = geturl + "?" + parameters
            response = self.app.get(geturl)
            if response.status_code == 200:
                res = json.loads(response.data)
                if res["instrument_types"] != result:
                    self.assertTrue(False)
            else:
                res = json.loads(response.data)
                if res["error"] != result:
                    self.assertTrue(False)

    def test_instruments(self):
        for value in self.testcases["instruments"]["values"]:
            geturl = self.testcases["instruments"]["URL"]
            if len(self.flag) == 0:
                result = "can't connect to background database service."
            else:
                condition = {}
                if "instrument_type" in value:
                    condition["Instrument_type"] = value["instrument_type"]
                if "source_name" in value:
                    condition["Source_name"] = value["source_name"]
                result = db.get_collection("attrs").distinct(
                    "Descriptor", condition)
            parameters = urllib.urlencode(value)
            if parameters != "":
                geturl = geturl + "?" + parameters
            response = self.app.get(geturl)
            if response.status_code == 200:
                res = json.loads(response.data)
                tmp = []
                for i in res["instruments"]:
                    if i["Descriptor"] not in result:
                        self.assertTrue(False)
                if len(result) != len(res["instruments"]):
                    self.assertTrue(False)
            else:
                res = json.loads(response.data)
                if res["error"] != result:
                    self.assertTrue(False)

    def test_data_sets(self):
        for value in self.testcases["data_sets"]["values"]:
            geturl = self.testcases["data_sets"]["URL"]
            if len(self.flag) == 0:
                result = "can't connect to background database service."
            else:
                condition = {}
                if "instrument_type" in value:
                    condition["Instrument_type"] = value["instrument_type"]
                if "source_name" in value:
                    condition["Source_name"] = value["source_name"]
                if "instrument" in value:
                    condition["Descriptor"] = value["instrument"]
                result = list(db.get_collection(
                    "attrs").find(condition, {"_id": 1, "Data_type": 1, "full_Data_type": 1}))
            parameters = urllib.urlencode(value)
            if parameters != "":
                geturl = geturl + "?" + parameters
            response = self.app.get(geturl)
            if response.status_code == 200:
                res = json.loads(response.data)
                for data_set in result:
                    if data_set not in res["data_sets"]:
                        self.assertTrue(False)
                if len(result) != len(res["data_sets"]):
                    self.assertTrue(False)
            else:
                res = json.loads(response.data)
                if res["error"] != result:
                    self.assertTrue(False)

    def test_variables(self):
        for value in self.testcases["variables"]["values"]:
            geturl = self.testcases["variables"]["URL"]
            if len(self.flag) == 0:
                result = "can't connect to background database service."
            else:
                result = []
                data_set = value["data_set"]
                attr = db.get_collection("attrs").find_one({"_id": data_set})
                if attr != None:
                    for key in attr.keys():
                        if isinstance(attr[key], dict):
                            if "VAR_TYPE" in attr[key] and attr[key]["VAR_TYPE"] == 'data':
                                result.append(key)
            geturl += value["data_set"] + "/variables"
            response = self.app.get(geturl)
            if response.status_code == 200:
                res = json.loads(response.data)
                for variable in result:
                    if variable not in res["variables"]:
                        self.assertTrue(False)
                if len(result) != len(res["variables"]):
                    self.assertTrue(False)
            else:
                res = json.loads(response.data)
                if res["error"] != result:
                    self.assertTrue(False)

    def test_data(self):
        for value in self.testcases["data"]["values"]:
            geturl = self.testcases["data"]["URL"]
            if len(self.flag) == 0:
                result = "can't connect to background database service."
            else:
                data_set = value["data_set"]
                attr = db.get_collection("attrs").find_one({"_id": data_set})
                tmp = []
                if "variables" in value:
                    if attr != None:
                        var = value["variables"]
                        if var in attr:
                            if "VAR_TYPE" in attr[var] and attr[var]["VAR_TYPE"] == 'data':
                                tmp.append(var)
                                for val in attr[var].values():
                                    if val in attr:
                                        tmp.append[val]
                            else:
                                attr = {"error": "variables"}
                        else:
                            attr = {"error": "variables"}
                    else:
                        attr = {"error": "variables"}
                else:
                    attr = {"error": "variables"}
                if "error" in attr:
                    data = []
                else:
                    data = tmp
            geturl += value["data_set"] + "/data"
            response = self.app.get(geturl)
            if response.status_code == 200:
                res = json.loads(response.data)
                attributes = tes["attributes"]
                if len(data) == len(attributes.keys()):
                    for key in data:
                        if key not in attributes.keys():
                            self.assertTrue(False)
                else:
                    self.assertTrue(False)
            else:
                res = json.loads(response.data)
                if res["error"] != attr["error"]:
                    self.assertTrue(False)
