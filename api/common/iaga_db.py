#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-04-20 21:11:27
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import sys
import time
from base_conn import getConn

iaga_db = "IAGA_Release"
iaga_data = 'data'
iaga_header = 'files'
iaga_station = 'stations'


class IAGA_DB:
    def __init__(self):
        self.conn = getConn(iaga_db)

    def get_stations(self, start_longitude, end_longitude, start_latitude, end_latitude):
        stations = self.conn.get_collection(iaga_station).find({
            '$and': [
                {'Geodetic Latitude':
                    {'$gte': start_latitude, '$lte': end_latitude}},
                {'Geodetic Longitude':
                    {'$gte': start_longitude, '$lte': end_longitude}}
            ]
        }, {
            '_id': 0, 'Station Name': 1,
            'IAGA CODE': 1,
            'Geodetic Latitude': 1, 'Geodetic Longitude': 1
        }).sort("IAGA CODE", 1)
        return stations

    def get_IAGA_list(self, start_longitude, end_longitude, start_latitude, end_latitude):
        stations = self.conn.get_collection(iaga_station).distinct('IAGA CODE', {
            '$and': [
                {'Geodetic Latitude':
                    {'$gte': start_latitude, '$lte': end_latitude}},
                {'Geodetic Longitude':
                    {'$gte': start_longitude, '$lte': end_longitude}}
            ]
        })
        return stations

    def get_data_by_time_stations(self, start_time, end_time, stations, term, sample_rate, data_type):
        condition = {}
        for i in term.keys():
            condition[i] = {"$exists": 1}
        term['IAGA CODE'] = 1
        term['time_stamp'] = 1
        term["InterTpye"] = 1
        term['Type'] = 1
        term['_id'] = 0
        condition['Type'] = {'$in': data_type}
        condition['InterTpye'] = {'$in': sample_rate}
        condition['IAGA CODE'] = {'$in': stations}
        if start_time != None and end_time != None:
            condition['time_stamp'] = {'$gte': start_time, '$lte': end_time}

        t1 = time.time()
        data = self.conn.get_collection(iaga_data).find(condition, term).sort(
            [('time_stamp', 1)])
        t2 = time.time()
        # print "----------------------------"
        # print "generate cursor time:", t2 - t1
        # print "----------------------------"
        return data

    def get_reported_type_list(self, stations=None):
        if stations is None:
            reportde_types = self.conn.get_collection(
                iaga_header).distinct("Reported")
        else:
            reportde_types = self.conn.get_collection(iaga_header).distinct(
                "Reported", {'IAGA CODE': {'$in': stations}})
        return reportde_types
