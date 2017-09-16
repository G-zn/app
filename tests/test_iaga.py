#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-04-09 12:54:35
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import json
import urllib
import time
import unittest
from api import create_app
from pymongo import MongoClient

mongo = MongoClient()
db = mongo['IAGA_Release']


def get_source():
    with open("./tests/testcase_iaga.json") as json_file:
        source = json.load(json_file)
    return source


class test(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing').test_client()
        self.source = get_source()
        self.flag = os.popen(
            "ps -aux|grep mongod|grep -v grep|awk '{print $1}'").readlines()

    def tearDown(self):
        if len(self.flag) == 0:
            print "\n--> can't connect to database,whether the information that system returned correspond to this situation testing module have done."

    def test_app_exists(self):
        self.assertFalse(self.app is None)
        self.flag = [1]

    def test_stations(self):
        for values in self.source["stations"]["values"]:
            geturl = self.source["stations"]["URL"]
            if len(self.flag) == 0:
                result = "can't connect to background database service."
            elif "result" in values:
                result = values["result"]
                del values["result"]
            else:
                condition = {}
                if "start_longitude" in values or "end_longitude" in values:
                    condition['Geodetic Longitude'] = {}
                    if "start_longitude" in values:
                        start_longitude = values['start_longitude']
                        condition['Geodetic Longitude'][
                            '$gte'] = start_longitude
                    if "end_longitude" in values:
                        end_longitude = values['end_longitude']
                        condition['Geodetic Longitude']['$lte'] = end_longitude
                if "start_latitude" in values or "end_latitude" in values:
                    condition['Geodetic Latitude'] = {}
                    if "start_latitude" in values:
                        start_latitude = values['start_latitude']
                        condition['Geodetic Latitude']['$gte'] = start_latitude
                    if "end_latitude" in values:
                        end_latitude = values['end_latitude']
                        condition['Geodetic Latitude']['$lte'] = end_latitude
                if len(self.flag) > 0:
                    result = db.get_collection(
                        'stations').find(condition).count()
                    if "offset" in values:
                        offset = values["offset"]
                    else:
                        offset = 0
                    if "number" in values:
                        number = values["number"]
                    else:
                        number = None

                    if result < offset:
                        result = 0
                    elif number == None:
                        result = result - offset
                    elif result > offset + number:
                        result = number
                    else:
                        result = result - offset
            data = urllib.urlencode(values)
            if data != "":
                geturl = geturl + '?' + data
            # print '\n', urllib.unquote(geturl)
            response = self.app.get(geturl)
            if response.status_code == 400:
                res = json.loads(response.data)
                # print res['error'], result
                if res['error'] != result:
                    self.assertTrue(False)
            elif response.status_code == 200:
                res = json.loads(response.data)
                # print res['count'], result
                if res["count"] != result:
                    self.assertTrue(False)
            elif response.status_code == 503:
                res = json.loads(response.data)
                # print res['error'], result
                if res['error'] != result:
                    self.assertTrue(False)

    def test_data(self):
        for values in self.source["data"]["values"]:
            geturl = self.source["data"]["URL"]
            if len(self.flag) == 0:
                result = "can't connect to background database service."
                return False
            elif "result" in values:
                result = values["result"]
                del values["result"]
            else:
                condition = {}
                if "start_longitude" in values or "end_longitude" in values:
                    condition['Geodetic Longitude'] = {}
                    if "start_longitude" in values:
                        start_longitude = values['start_longitude']
                        condition['Geodetic Longitude'][
                            '$gte'] = start_longitude
                    if "end_longitude" in values:
                        end_longitude = values['end_longitude']
                        condition['Geodetic Longitude'][
                            '$lte'] = end_longitude
                if "start_latitude" in values or "end_latitude" in values:
                    condition['Geodetic Latitude'] = {}
                    if "start_latitude" in values:
                        start_latitude = values['start_latitude']
                        condition['Geodetic Latitude'][
                            '$gte'] = start_latitude
                    if "end_latitude" in values:
                        end_latitude = values['end_latitude']
                        condition['Geodetic Latitude'][
                            '$lte'] = end_latitude
                if len(self.flag) > 0:
                    stations = db.get_collection(
                        'stations').distinct('IAGA CODE', condition)
                    station_list = []
                    if 'stations' in values:
                        station_list = values['stations'].split(',')
                    else:
                        station_list = 'all'
                    if 'all' not in station_list:
                        i = 0
                        while i < len(station_list):
                            station_list[i] = station_list[i].strip().upper()
                            i += 1
                        stations = list(set(stations) & set(station_list))

                    condition = {}
                    condition['IAGA CODE'] = {'$in': stations}

                    if "start_time" in values and "end_time" in values:
                        start_time = values["start_time"]
                        end_time = values["end_time"]
                        start_time = time.mktime(time.strptime(
                            start_time, "%Y-%m-%d %H:%M:%S"))
                        end_time = time.mktime(time.strptime(
                            end_time, "%Y-%m-%d %H:%M:%S"))
                        condition['time_stamp'] = {
                            '$gte': start_time, '$lte': end_time}

                    if "sample_rate" in values:
                        sample_rate = list(
                            set(values["sample_rate"].split(',')))
                        for i in range(0, len(sample_rate)):
                            sample_rate[i] = sample_rate[i].strip().lower()
                        condition['InterTpye'] = {'$in': sample_rate}
                    else:
                        condition['InterTpye'] = {'$in': ['min']}

                    if "data_type" in values:
                        data_type = list(set(values["data_type"].split(',')))
                        for i in range(0, len(data_type)):
                            data_type[i] = data_type[i].strip().lower()
                        condition['Type'] = {'$in': data_type}
                    else:
                        condition['Type'] = {'$in': ['v']}

                    if "term" in values:
                        mag_component = list(set(values["term"].split(',')))
                        for i in range(0, len(mag_component)):
                            mag_component[i] = mag_component[i].strip().upper()
                            condition[mag_component[i]] = {"$exists": 1}
                    else:
                        mag_component = ['X']

                    if 'offset' in values:
                        offset = values["offset"]
                    else:
                        offset = 0

                    if "number" in values:
                        number = values["number"]
                    else:
                        number = 1000

                    result = db.get_collection('data').find(condition).count()

                    if result <= offset:
                        result = 0
                    elif result <= (offset + number):
                        result = result - offset
                    else:
                        result = number
            data = urllib.urlencode(values)
            if data != "":
                geturl = geturl + '?' + data
            # print '\n', urllib.unquote(geturl)
            response = self.app.get(geturl)
            if response.status_code == 400:
                res = json.loads(response.data)
                if not result in res['error']:
                    # print "result:", result
                    # print "res:", res['error'], '\n'
                    self.assertTrue(False)
            elif response.status_code == 200:
                res = json.loads(response.data)
                if res["count"] != result:
                    # print urllib.unquote(geturl)
                    # print condition
                    # print res["count"]
                    # print result
                    self.assertTrue(False)
                if result > 0:
                    data = res["data"][0]
                    for i in mag_component:
                        if i not in data.keys():
                            self.assertTrue(False)
            elif response.status_code == 503:
                res = json.loads(response.data)
                # print res['error'], result
                if res['error'] != result:
                    self.assertTrue(False)
