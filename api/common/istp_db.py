#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-09-06 10:55:00
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from base_conn import getConn

cdf_db = "CDF_Release"
cdf_attrs = 'attrs'
cdf_data = 'data'


class ISTP_DB:
    def __init__(self):
        self.conn = getConn(cdf_db)

    def get_element_list(self, element, condition=None):
        return self.conn.get_collection(cdf_attrs).distinct(element, condition)

    def get_element_and_full_list(self, element, condition=None):
        e_list = ["Project", "Source_name", "Descriptor", "Data_type"]
        if element not in e_list:
            return self.get_element_list(element, condition)
        res = []
        elem_list = self.conn.get_collection(
            cdf_attrs).distinct(element, condition)
        for elem in elem_list:
            temp = {}
            temp[element] = elem
            temp["full_" + element] = self.conn.get_collection(cdf_attrs).distinct(
                "full_" + element, {"full_" + element: {"$nin": ['', ' ', None]}, element: elem})[0]
            res.append(temp)
        return res

    def get_data_sets(self, condition):
        term = {}
        term["Data_type"] = 1
        term["full_Data_type"] = 1
        data_sets = list(self.conn.get_collection(
            "attrs").find(condition, term))
        return data_sets

    def get_variables(self, logical_source, var_type=None):
        condition = {}
        condition["_id"] = logical_source
        attrs = self.conn.get_collection("attrs").find_one(condition)
        variables = []
        if attrs != None:
            for key in attrs.keys():
                if isinstance(attrs[key], dict):
                    if var_type != None:
                        if "VAR_TYPE" in attrs[key].keys() and attrs[key]["VAR_TYPE"] == var_type:
                            variables.append(key)
                    else:
                        variables.append(key)
        return sorted(variables)

    def get_attribute(self, logical_source, variables):
        term = {}
        term["_id"] = 0
        term[variables] = 1
        attr = self.conn.get_collection("attrs").find_one(
            {"_id": logical_source}, term)
        if attr == None:
            return {"error": "data_set"}
        elif attr == {}:
            return {"error": "vaiables"}
        var_list = self.get_variables(logical_source)
        for variable in attr.keys():
            for key in attr[variable].values():
                if key in var_list:
                    term[key] = 1
        attr = self.conn.get_collection("attrs").find_one(
            {"_id": logical_source}, term)
        return attr

    def get_data(self, logical_source, variables, start_time=None, end_time=None):
        attr = self.get_attribute(logical_source, variables)
        if "error" in attr:
            return []
        term = {}
        term["_id"] = 0
        term[variables] = 1
        term["time_stamp"] = 1
        condition = {}
        condition["Logical_source"] = logical_source
        if start_time != None and end_time != None:
            condition["time_stamp"] = {"$gte": start_time, "$lte": end_time}
        condition[variables] = {"$exists": 1}
        data = self.conn.get_collection("data").find(condition, term)
        return data
