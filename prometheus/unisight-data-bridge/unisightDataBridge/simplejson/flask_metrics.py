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
from pprint import pprint
from pandas import Series
import pandas as pd
import json
import numpy as np
import os

from pandas.io.json import json_normalize
from datetime import datetime
from calendar import timegm
from datetime import datetime
from datetime import date

from graphqlclient import GraphQLClient

# Import my metrics
from . import graphql_queries

def dataframe_to_json_table(target, df):
    response = []
    if df.empty:
        return response

    if isinstance(df, pd.DataFrame):
        response.append({'type': 'table',
                         'columns': df.columns.map(lambda col: {"text": col}).tolist(),
                         'rows': df.where(pd.notnull(df), None).values.tolist()})
    else:
        abort(404, Exception('Received object is not a dataframe.'))

    return response


def dataframe_to_json_timeserie(target, df):
    dp = {"target": target, "datapoints": [] }
    output = []
    if df.empty:
        return output

    if isinstance(df, pd.DataFrame):
        list = df[[target,'time']].values.tolist()
        dp["datapoints"] = list
        output.append(dp)
    else:
        abort(404, Exception('Received object is not a dataframe.'))
    return output

# KEY FUNCTION TO GET GRAPHQL DATA. 
def all_jobs_metric(graphql_host, graphql_port, graphql_auth):
   
    # graphql connection

    graphql_url = 'http://' + graphql_host + ':' + str(graphql_port) + '/graphql'

    url = os.environ.get('GRAPHQL_URL',graphql_url)
    client = GraphQLClient(url)
    client.inject_token(os.environ.get('GRAPHQL_AUTH',graphql_auth))

    output_allJobsRunning = graphql_queries.query_AllJobs_Running(client)
    
    df = pd.DataFrame()
    # We triger a query got all Historical Jobs
    allJobs = json.loads(output_allJobsRunning).get('data',{}).get('allJobs',{})

    jobs = allJobs.get('Jobs',[])
    # Walk the result and append to dataframe
    for j in jobs:
      #print(j['jobid'])
      df_temp = pd.DataFrame(json_normalize(j))
      df_temp['submitEpoch'] = j['timeStamp']['submitEpoch']
      df_temp['time'] = j['timeStamp']['submitEpoch']
      df_temp['submission_time'] = j['timeStamp']['submit']
      df_temp['hosts'] =  j['queue'].split('@')[1]
      df = df.append(df_temp,sort=True)
      pd.to_datetime(df['time'].values, unit='ms', utc=True)

    df.set_index('submitEpoch',  append=False,inplace=True)
    return(df[['submission_time','jobid','taskid','slots','priority','department','project','shares','queue_name','hosts','usage.iow','usage.mem','usage.ioops','usage.cpu','usage.vmem','usage.wallclock','usage.maxvmem']])

#
#  Get Table with historical data
#
def all_historical_job_metric(graphql_host,graphql_port,graphql_auth):

    # graphql connection
    graphql_url = 'http://' + graphql_host + ':' + str(graphql_port) + '/graphql'

    url = os.environ.get('GRAPHQL_URL',graphql_url)
    client = GraphQLClient(url)
    client.inject_token(os.environ.get('GRAPHQL_AUTH',graphql_auth))

    output = graphql_queries.query_AllHistoricaJobs(client)

    df = pd.DataFrame()
    allJobs = json.loads(output).get('data',{}).get('allHistoricalJobs',{})

    jobs = allJobs.get('HistoricalJobs',[])
    for j in jobs:
      cols = [1,5,6,7,8,9,10,11,12,13,15,44,45,58]
      #print(j['jobid'])
      df_temp = pd.DataFrame(json_normalize(j))
      #df.drop(df.columns[cols],axis=1,inplace=True)
      df_temp['submission_time_ms'] = j['submission_time_ms']
      df_temp['slots'] = j['slots']
      df = df.append(df_temp,sort=True)
      #pd.to_datetime(df['time'].values, unit='ms', utc=True)

    df.set_index('submission_time_ms',  append=False,inplace=True)
    #df.index = df.index.to_datetime()
    # Use the following for values like 3.5G.  Will remove the 'G' at the end.
    # pd.to_numeric(df['m_mem_used'].str.replace('[^\d.]', ''), errors='coerce')
    return (df[['job_number','owner','slots','qname','project','usage.ru_wallclock','usage.cpu','hostname']])
