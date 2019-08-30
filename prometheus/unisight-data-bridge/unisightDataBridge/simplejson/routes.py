#!/usr/bin/env python

# Copyright 2008-2019 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from calendar import timegm
from datetime import datetime
import _strptime # https://bugs.python.org/issue7980
from flask import Flask, request, jsonify, json, abort
import pandas as pd
from pandas import Timestamp

from . import flask_metrics

methods = ('GET', 'POST')

def convert_to_time_ms(timestamp):
	return 1000 * timegm(datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())

def create_app(graphql_host, graphql_port, graphql_auth):
    app = Flask(__name__) 

    @app.route('/', methods=methods)
    def ok():
        print(request.headers, request.get_json())
        return 'This datasource is healthy.'


    @app.route('/search', methods=methods)
    def search():

        print('/search')
        print(request.headers, request.get_json())

        #return jsonify(['job_number','slots','group','owner','project','department','usage.ru_wallclock','usage.cpu','usage.mem','usage.io','usage.iow','usage.iow'])
        return jsonify(['Jobs_Table','Historical_Jobs_Table','Historical_Job_Timeseries_Slots'])


    @app.route('/query', methods=['POST'])
    def query():

        req = request.get_json()

        target = req['targets'][0]['target']
        req_type = req['targets'][0]['type']

        ts_range = {'$gt': pd.Timestamp(req['range']['from']).to_pydatetime(),
                    '$lte': pd.Timestamp(req['range']['to']).to_pydatetime()}

        # Metrics by Target
        if target == 'Jobs_Table':
           df = flask_metrics.all_jobs_metric(graphql_host, graphql_port, graphql_auth)
        if target == 'Historical_Jobs_Table':
           df = flask_metrics.all_historical_job_metric(graphql_host, graphql_port, graphql_auth)
   
        # Serialize based on req_type 
        if req_type == 'table':
               data = flask_metrics.dataframe_to_json_table(target,df)
        else:
               data = flask_metrics.dataframe_to_json_timeserie(target,df)

        return jsonify(data)


    @app.route('/annotations', methods=['POST'])
    def annotations():

        print('/anotations')
        print(request.headers, request.get_json())

        req = request.get_json()
        data = [
            {
                "annotation": 'This is the annotation',
                "time": (convert_to_time_ms(req['range']['from']) +
                         convert_to_time_ms(req['range']['to'])) / 2,
                "title": 'Deployment notes',
                "tags": ['tag1', 'tag2'],
                "text": 'Hm, something went wrong...'
            }
        ]
    
        return jsonify(data)


    @app.route('/tag-keys', methods=['POST'])
    def tag_keys():
        data = [
            {"type": "string", "text": "City"},
            {"type": "string", "text": "Country"}
        ]
        return jsonify(data)


    @app.route('/tag-values', methods=['POST'])
    def tag_values():
        req = request.get_json()
        if req['key'] == 'City':
            return jsonify([
                {'text': 'Tokyo'},
                {'text': 'So Paulo'},
                {'text': 'Jakarta'}
            ])
        elif req['key'] == 'Country':
            return jsonify([
                {'text': 'China'},
                {'text': 'India'},
                {'text': 'United States'}
            ])
    return app
