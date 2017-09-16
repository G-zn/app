#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-04-22 20:44:06
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from flask import g
from flask import jsonify
from flask import request
from . import main
import time
from manage import cache


@main.route("/iaga/stations", methods=['GET'])
def get_iaga_stations():
    db = getattr(g, 'IAGA_DB', None)
    if db == None:
        return jsonify({"error": "can't connect to background database service."}), 503

    try:
        start_longitude = float(request.args.get("start_longitude", 0))
    except ValueError:
        return jsonify({"error": "can not convert start_longitude:%s to float." % request.args.get("start_longitude")}), 400
    if start_longitude < 0 or start_longitude > 360:
        return jsonify({"error": "start_longitude out of range(0,360)."}), 400

    try:
        start_latitude = float(request.args.get("start_latitude", -90))
    except ValueError:
        return jsonify({"error": "can not convert start_latitude:%s to float." % request.args.get("start_latitude")}), 400
    if start_latitude < -90 or start_latitude > 90:
        return jsonify({"error": "start_latitude out of range(-90,90)."}), 400

    try:
        end_longitude = float(request.args.get("end_longitude", 360))
    except ValueError:
        return jsonify({"error": "can not convert end_longitude:%s to float." % request.args.get("end_longitude")}), 400
    if end_longitude < 0 or end_longitude > 360:
        return jsonify({"error": "end_longitude out of range(0,360)."}), 400

    try:
        end_latitude = float(request.args.get("end_latitude", 90))
    except ValueError:
        return jsonify({"error": "can not convert end_latitude:%s to float." % request.args.get("end_latitude")}), 400
    if end_latitude < -90 or end_latitude > 90:
        return jsonify({"error": "end_latitude out of range(-90,90)."}), 400

    if start_longitude > end_longitude or start_latitude > end_latitude:
        return jsonify({"error": "the range of location is invalid."}), 400

    stations = list(db.get_stations(
        start_longitude, end_longitude, start_latitude, end_latitude))

    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"error": "can not convert offset:%s to int." % request.args.get("offset")}), 400
    if offset < 0:
        return jsonify({"error": "offset:%d isn't a nonnegative number." % offset}), 400

    number = request.args.get('number', None)
    if number == None:
        return jsonify({
            "stations": stations[offset:],
            "count": len(stations[offset:])
        })
    else:
        try:
            number = int(number)
        except ValueError:
            return jsonify({"error": "can not convert number:%s to int." % number}), 400
        if number <= 0:
            return jsonify({"error": "number:%d isn't a positive number." % number}), 400
        return jsonify({
            "stations": stations[offset:offset + number],
            "count": len(stations[offset:offset + number])
        })


@main.route("/iaga/reported_type", methods=['GET'])
@cache.cached(timeout=50)
def get_iaga_reported_types():
    db = getattr(g, 'IAGA_DB', None)
    if db == None:
        return jsonify({"error": "can't connect to background database service."}), 503

    reported_types = db.get_reported_type_list()
    return jsonify({"Reported": reported_types})


@main.route("/iaga/data", methods=['GET'])
def get_iaga_data():
    db = getattr(g, 'IAGA_DB', None)
    if db == None:
        return jsonify({"error": "can't connect to background database service."}), 503

    if not (("start_time" in request.args) ^ ("end_time" in request.args)):
        start_time = request.args.get("start_time", None)
        end_time = request.args.get("end_time", None)
        if start_time != None and end_time != None:
            try:
                start_time = time.mktime(time.strptime(
                    start_time, "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                return jsonify({"error": "start_time:" + start_time + " doesn't match '%Y-%m-%d %H:%M:%S'."}), 400
            try:
                end_time = time.mktime(time.strptime(
                    end_time, "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                return jsonify({"error": "end_time:" + end_time + " doesn't match '%Y-%m-%d %H:%M:%S'."}), 400
            if start_time > end_time:
                return jsonify({"error": "please check time range, start_time can't over end_time."}), 400
    else:
        return jsonify({"error": "start_time and end_time must appeared together."}), 400

    try:
        start_longitude = float(request.args.get("start_longitude", 0))
    except ValueError:
        return jsonify({"error": "can not convert start_longitude:%s to float." % request.args.get("start_longitude")}), 400
    if start_longitude < 0 or start_longitude > 360:
        return jsonify({"error": "start_longitude out of range(0,360)."}), 400

    try:
        start_latitude = float(request.args.get("start_latitude", -90))
    except ValueError:
        return jsonify({"error": "can not convert start_latitude:%s to float." % request.args.get("start_latitude")}), 400
    if start_latitude < -90 or start_latitude > 90:
        return jsonify({"error": "start_latitude out of range(-90,90)."}), 400

    try:
        end_longitude = float(request.args.get("end_longitude", 360))
    except ValueError:
        return jsonify({"error": "can not convert end_longitude:%s to float." % request.args.get("end_longitude")}), 400
    if end_longitude < 0 or end_longitude > 360:
        return jsonify({"error": "end_longitude out of range(0,360)."}), 400

    try:
        end_latitude = float(request.args.get("end_latitude", 90))
    except ValueError:
        return jsonify({"error": "can not convert end_latitude:%s to float." % request.args.get("end_latitude")}), 400
    if end_latitude < -90 or end_latitude > 90:
        return jsonify({"error": "end_latitude out of range(-90,90)."}), 400

    if start_longitude > end_longitude or start_latitude > end_latitude:
        return jsonify({"error": "the range of location is invalid."}), 400

    stations = db.get_IAGA_list(
        start_longitude, end_longitude, start_latitude, end_latitude)
    station_list = request.args.get("stations", "all")
    if 'all' not in station_list:
        station_list = station_list.split(',')
        i = 0
        while i < len(station_list):
            station_list[i] = station_list[i].strip().upper()
            i += 1
        stations = list(set(stations) & set(station_list))
    if len(stations) == 0:
        return jsonify({"data": [], "count": 0, 'total_count': 0})

    # handle sample_rate
    sample_rate = list(
        set(request.args.get("sample_rate", "min").split(',')))
    for i in range(0, len(sample_rate)):
        sample_rate[i] = sample_rate[i].strip().lower()
        if sample_rate[i] not in ['min', 'sec']:
            return jsonify({"error": "please select sample_rate in [min, sec], default:min, you can select both, use ',' to split them."}), 400

    # handle data_type
    data_type = request.args.get("data_type", 'v').split(',')
    data_type = list(set(data_type))
    for i in range(0, len(data_type)):
        data_type[i] = data_type[i].strip().lower()
        if data_type[i] not in ['v', 'p', 'q', 'd']:
            return jsonify({"error": "please select data_type in [v, p, q, d], default:v, you can select more, use ',' to split them.",
                            'v': 'variation',
                            'p': 'provisional',
                            'q': 'quasi-definitive',
                            'd': 'definitive'
                            }), 400

    # handle term and reported
    term = {}
    reported_types = db.get_reported_type_list()
    i = 0
    reported_type = request.args.get("reported_type", 'XYZF')
    if reported_type in reported_types:
        mag_component = request.args.get("term", reported_type[0])
        if mag_component != '':
            mag_component = list(set(mag_component.split(',')))
            for i in range(0, len(mag_component)):
                mag_component[i] = mag_component[i].strip().upper()
                if mag_component[i] not in reported_type:
                    return jsonify({
                        "error": "the Geomagnetic component:" + mag_component[i] + " not in the data reported type:" + reported_type
                        + " that you selected or default:XYZF."
                    }), 400
                term[mag_component[i]] = 1
        else:
            return jsonify({"error": "term is invalid."}), 400
    else:
        return jsonify({"error": "please select reported_type in %s, default:XYZF." % reported_types}), 400

    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"error": "can not convert offset:%s to int." % request.args.get("offset")}), 400
    if offset < 0:
        return jsonify({"error": "offset:%d isn't a nonnegative number." % offset}), 400

    try:
        number = int(request.args.get('number', 1000))
    except ValueError:
        return jsonify({"error": "can not convert number:%s to int." % request.args.get('number')}), 400
    if number <= 0:
        return jsonify({"error": "number:%d isn't a positive number." % number}), 400
    elif number > 100000:
        return jsonify({"error": "the max number is 100000."}), 400

    data = db.get_data_by_time_stations(
        start_time, end_time, stations, term, sample_rate, data_type)
    t1 = time.time()
    data = list(data[offset: offset + number])
    t2 = time.time()
    # print "----------------------------"
    # print "list data time:", t2 - t1
    # print "----------------------------"
    return jsonify({
        'data': data,
        'count': len(data),
    })
