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

from __future__ import print_function
import time
import json
import os
import traceback

# Import my metrics
from . import graphql_queries

from graphqlclient import GraphQLClient
from prometheus_client import  start_http_server, Gauge, Summary,Counter, Histogram 

gauge_jobs = Gauge('jobs_by_state', 'Number of Jobs per State in the cluster',['state'])
gauge_jobs_in_queue = Gauge('jobs_per_queue', 'Number of Jobs per Queue in the cluster',['queue_name'])
gauge_slots_in_queue = Gauge('slots_per_queue', 'Number of Slots per Queue in the cluster',['queue_name'])
gauge_mem_used_per_queue = Gauge('mem_per_queue', 'Memory used by the Jobs per Queue in the cluster',['queue_name'])
gauge_np_load_avg = Gauge('np_load_avg', 'np_load_avg per Host in the cluster',['hostname'])

gauge_tot_jobs_running_byuser = Gauge('count_jobr_user', 'Total Running Jobs by User',['user'])
gauge_tot_jobs_running_byproject = Gauge('count_jobr_project', 'Total Running Jobs by Project',['project'])
gauge_tot_jobs_queued_byuser = Gauge('count_jobq_user', 'Total Queued Jobs by User',['user'])
gauge_tot_jobs_queued_byproject = Gauge('count_jobq_project', 'Total Queued Jobs by Project',['project'])
gauge_tot_slots_byuser = Gauge('count_slots_user', 'Total Slots in use by User',['user'])
gauge_tot_slots_byproject = Gauge('count_slots_project', 'Total Slots in use by Projects',['project'])

#
#
gauge_tot_tasks_running_byuser = Gauge('tasks_running_byuser', 'Total Running Tasks by User',['user'])
gauge_tot_tasks_running_byproject = Gauge('tasks_running_byproject', 'Total Running Tasks by Project',['project'])
gauge_tot_tasks_queued_byuser = Gauge('tasks_queued_byuser', 'Total Queued Tasks by User',['user'])
gauge_tot_tasks_queued_byproject = Gauge('tasks_queued_byproject', 'Total Queued Tasks by Project',['project'])
#
#

# Job Usage by Users
gauge_job_usage_mem_byuser = Gauge('count_usage_mem_user', 'Mem Usage by User',['user'])
gauge_job_usage_iow_byuser = Gauge('count_usage_iow_user', 'IOWaiting Usage by User',['user'])
gauge_job_usage_io_byuser = Gauge('count_usage_io_user', 'IO Usage by User',['user'])
gauge_job_usage_wallclock_byuser = Gauge('count_usage_wallclock_user', 'Wallclock Usage by User',['user'])
gauge_job_usage_vmem_byuser = Gauge('count_usage_vmem_user', 'vmem Usage by User',['user'])
gauge_job_usage_cpu_byuser = Gauge('count_usage_cpu_user', 'cpu Usage by User',['user'])
gauge_job_usage_maxvmem_byuser = Gauge('count_usage_maxvmem_user', 'maxvmem Usage by User',['user'])

# Job Usage by project
gauge_job_usage_mem_byproject = Gauge('count_usage_mem_project', 'Mem Usage by Project',['project'])
gauge_job_usage_iow_byproject = Gauge('count_usage_iow_project', 'IOWaiting Usage by Project',['project'])
gauge_job_usage_io_byproject = Gauge('count_usage_io_project', 'IO Usage by Project',['project'])
gauge_job_usage_wallclock_byproject = Gauge('count_usage_wallclock_project', 'Wallclock Usage by Project',['project'])
gauge_job_usage_vmem_byproject = Gauge('count_usage_vmem_project', 'vmem Usage by Project',['project'])
gauge_job_usage_cpu_byproject = Gauge('count_usage_cpu_project', 'cpu Usage by Project',['project'])
gauge_job_usage_maxvmem_byproject = Gauge('count_usage_maxvmem_project', 'maxvmem Usage by Project',['project'])

# Total Usages for all Jobs
gauge_tot_usage_mem = Gauge('count_usage_mem', 'Total Mem Usage')
gauge_tot_usage_iow = Gauge('count_usage_iow', 'Total IOWaiting Usage')
gauge_tot_usage_io = Gauge('count_usage_io', 'Total IO Usage')
gauge_tot_usage_wallclock = Gauge('count_usage_wallclock', 'Total Wallclock Usage')
gauge_tot_usage_vmem = Gauge('count_usage_vmem', 'Total vmem Usage')
gauge_tot_usage_cpu = Gauge('count_usage_cpu', 'Total cpu Usage')
gauge_tot_usage_maxvmem = Gauge('count_usage_maxvmem', 'Total maxvmem Usage')
gauge_tot_usage_slots = Gauge('slots_in_use', 'Total Slots Usage')
gauge_tot_usage_iops = Gauge('count_usage_iops', 'IOOPS Usage')

# Usage by every Job
gauge_jobid_usage_mem = Gauge('job_usage_mem', 'Mem Usage by Jobid',['job'])
gauge_jobid_usage_iow = Gauge('job_usage_iow', 'IOWaiting Usage by Jobid',['job'])
gauge_jobid_usage_io = Gauge('job_usage_io', 'IO Usage by Jobid',['job'])
gauge_jobid_usage_wallclock = Gauge('job_usage_wallclock', 'Wallclock Usage by Jobid',['job'])
gauge_jobid_usage_vmem = Gauge('job_usage_vmem', 'vmem Usage by Jobid',['job'])
gauge_jobid_usage_cpu = Gauge('job_usage_cpu', 'cpu Usage by Jobid',['job'])
gauge_jobid_usage_maxvmem = Gauge('job_usage_maxvmem', 'maxvmem Usage by Jobid',['job'])


# Server Health
gauge_server_mem_usage = Gauge('server_mem_usage', 'Memory usage by server',['hostname'])
gauge_server_mem_free = Gauge('server_mem_free', 'Memory Free by server',['hostname'])
gauge_server_cpu = Gauge('server_cpu_usage', 'CPU usage by server',['hostname'])
gauge_server_jobcount_usage = Gauge('server_jobcount_usage', 'JobCount usage by server',['hostname'])
gauge_server_np_load_avg = Gauge('server_np_load_avg', 'np_load_avg by server',['hostname'])
gauge_server_virtualmem_used = Gauge('server_virtualmem', 'Vmem usage by server',['hostname'])
gauge_server_scratch_total = Gauge('server_scratch_total', 'Local Scratch capacity by server',['hostname']) 
gauge_server_scratch_used = Gauge('server_scratch_used', 'Local Scratch in use by server',['hostname'])
gauge_server_execd_status = Gauge('server_execd_status', 'Execd process running in the server',['hostname'])

# Cluster Info: Mem used, CPU, nodes, etc
gauge_tot_cores = Gauge('count_cores', 'Total Slots in the Cluster')
gauge_available_memory = Gauge('count_mem', 'Total Amount of Memory in the Cluster')
gauge_mem_used_byHost = Gauge('count_mem_used_byHost', 'Total Amount of Memory Used in the Cluster')
gauge_tot_nodes = Gauge('count_nodes', 'Total Number of Nodes in the Cluster')
gauge_nodes_in_use = Gauge('nodes_in_use', 'Number of Nodes in Use')
gauge_cluster_np_load_avg = Gauge('cluster_np_load_avg', 'Number of Nodes in Use')
#gauge_nodes_cpu_load =  Gauge('execd_cpu_load', 'CPU Load by node',['hostname'])
gauge_cluster_cpu_load =  Gauge('cluster_cpu_load', 'CPU Load by Cluster' )
gauge_host_np_load_avg = Gauge('host_np_load_avg', 'np_load_avg per Host in the cluster',['hostname'])


# Load Sensor: scratch, opt_space
gauge_opt_total = Gauge('opt_total', '/opt total in the cluster')
gauge_opt_used = Gauge('opt_used', '/opt total in the cluster')
gauge_opt_avail = Gauge('opt_avail', '/opt total in the cluster')
gauge_scratch_used = Gauge('scratch_used_in_host', 'Scratch used in the host',['hostname'])

# Cluster Info: Users, Projects
gauge_count_users = Gauge('count_users', 'Users running jobs in the cluster')
gauge_count_projects = Gauge('count_projects', 'Projects running jobs in the cluster')

def main(graphql_host, graphql_port, graphql_auth):
    graphql_url = 'http://' + graphql_host + ':' + str(graphql_port) + '/graphql'
    
    while True:
        try:
            url = os.environ.get('GRAPHQL_URL',graphql_url) 
            client = GraphQLClient(url)
            client.inject_token(os.environ.get('GRAPHQL_AUTH',graphql_auth))
            while True:
                print("Requesting jobs from:", url)

                output_allExecdHosts = graphql_queries.query_allExecdHosts(client)
                output_allJobsRunning = graphql_queries.query_AllJobs_Running(client)
                output_allJobsQueued = graphql_queries.query_AllJobs_Queued(client)
                output_allJobs = graphql_queries.query_allJobs(client)

                #
                # Publish metrics
                #
                tot_running_jobs_byUser(output_allJobsRunning)
                tot_running_jobs_byProject(output_allJobsRunning)
                tot_queued_jobs_byUser(output_allJobsQueued)
                tot_queued_jobs_byProject(output_allJobsQueued)
                tot_slots_byUser(output_allJobsRunning)
                tot_slots_byProject(output_allJobsRunning)
                #tot_running_tasks_byUser(output_allJobsRunning)
                #tot_running_tasks_byProject(output_allJobsRunning)
                #tot_queued_tasks_byUser(output_allJobsQueued)
                #tot_queued_tasks_byProject(output_allJobsQueued)
  

                tot_job_usage_mem_byUser(output_allJobsRunning)
                tot_job_usage_iow_byUser(output_allJobsRunning)
                tot_job_usage_io_byUser(output_allJobsRunning)
                tot_job_usage_wallclock_byUser(output_allJobsRunning)
                tot_job_usage_vmem_byUser(output_allJobsRunning)
                tot_job_usage_cpu_byUser(output_allJobsRunning)
                tot_job_usage_maxvmem_byUser(output_allJobsRunning)
                tot_job_usage_mem_byProject(output_allJobsRunning)
                tot_job_usage_iow_byProject(output_allJobsRunning)
                tot_job_usage_io_byProject(output_allJobsRunning)
                tot_job_usage_wallclock_byProject(output_allJobsRunning)
                tot_job_usage_vmem_byProject(output_allJobsRunning)
                tot_job_usage_cpu_byProject(output_allJobsRunning)
                tot_job_usage_maxvmem_byProject(output_allJobsRunning)

                cluster_info(output_allExecdHosts)

                jobs_by_state(output_allJobs)
                jobs_per_queue(output_allJobsRunning)
                get_queue_slots(output_allJobsRunning)
                get_mem_per_queue(output_allJobsRunning)
 
                server_info_jobcount(output_allExecdHosts)
                server_info_np_load_avg(output_allExecdHosts)
                server_info_memusage(output_allExecdHosts)
                server_info_memfree(output_allExecdHosts)
                server_info_cpu(output_allExecdHosts)
                server_info_virtual_mem(output_allExecdHosts)
                server_info_local_scratch_total(output_allExecdHosts)
                server_info_local_scratch_used(output_allExecdHosts)
                server_info_execd_status(output_allExecdHosts)              
                server_info_scratch_used_status(output_allExecdHosts)

                #jobid_iow_usage(output_allJobsRunning)
                #jobid_mem_usage(output_allJobsRunning)
                #jobid_io_usage(output_allJobsRunning)
                #jobid_wallclock_usage(output_allJobsRunning)
                #jobid_ioops_usage(output_allJobsRunning)
                #jobid_vmem_usage(output_allJobsRunning)
                #jobid_cpu_usage(output_allJobsRunning)
                #jobid_maxvmem_usage(output_allJobsRunning)
  
                time.sleep(30)

        except Exception as ex:
            print("Caught execption", ex)
            time.sleep(5)


###################
# CREATE METRICS  #
###################

#
# Total Running Jobs by User (per cluster)
#
def tot_running_jobs_byUser(myquery):
    job_dict = {}
    slots_used = 0
    count_users = 0
    ioops_used = 0
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        user = j.get('user',"unknown")
        cont_jobr_user = job_dict.get(user,0)
        slots = j.get('slots',0)
        ioops = j.get('usage',0).get('ioops',0)
        ioops_used += ioops
        cont_jobr_user+=1
        job_dict[user] = cont_jobr_user
        slots_used += slots
        count_users+=1
    for k, v in job_dict.items():
        gauge_tot_jobs_running_byuser.labels(k).set(v)
    gauge_tot_usage_slots.set(slots_used)
    gauge_count_users.set(count_users)
    gauge_tot_usage_iops.set(ioops_used)

#
# Total Running Jobs by Project (per cluster)
#
def tot_running_jobs_byProject(myquery):
    job_dict = {}
    count_projects = 0
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        project = j.get('project',"unknown")
        cont_jobr_project = job_dict.get(project,0)
        cont_jobr_project+=1
        job_dict[project] = cont_jobr_project
        count_projects+=1
    for k, v in job_dict.items():
        gauge_tot_jobs_running_byproject.labels(k).set(v)
        gauge_count_projects.set(count_projects)

#
# Total Running Slots/Cores by User
#
def tot_slots_byUser(myquery):
   slots_dict = {}
   allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
   for j in allJobs.get('Jobs',[]):
       user = j.get('user',"unknown")
       slots = j.get('slots',"unknown")
       used_slots = slots_dict.get(user,0)
       used_slots = used_slots + slots
       slots_dict[user] = used_slots
   for k, v in slots_dict.items():
       gauge_tot_slots_byuser.labels(k).set(v)

#
# Total Running Slots/Cores by Project
#
def tot_slots_byProject(myquery):
   slots_dict = {}
   allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
   for j in allJobs.get('Jobs',[]):
       project = j.get('project',"unknown")
       slots = j.get('slots',"unknown")
       used_slots = slots_dict.get(project,0)
       used_slots = used_slots + slots
       slots_dict[project] = used_slots
   for k, v in slots_dict.items():
       gauge_tot_slots_byproject.labels(k).set(v)


#
# Total Running Tasks by User
#
def tot_running_tasks_byUser(myquery):
   tasks_dict = {}
   allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
   for j in allJobs.get('Jobs',[]):
       print("Job %s" %j)
       user = j.get('user',"unknown")
       tasks = int(j.get('taskid',"unknown"))
       count = tasks_dict.get(user,0)
       if tasks > 0:
          count +=1
       tasks_dict[user] = count
   for k, v in tasks_dict.items():
       gauge_tot_tasks_running_byuser.labels(k).set(v)

#
# Total Running Tasks by Project
#
def tot_running_tasks_byProject(myquery):
   tasks_dict = {}
   allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
   for j in allJobs.get('Jobs',[]):
       project = j.get('project',"unknown")
       tasks = int(j.get('taskid',"unknown"))
       count = tasks_dict.get(project,0)
       if tasks > 0:
          count +=1
       tasks_dict[project] = count
   for k, v in tasks_dict.items():
       gauge_tot_tasks_running_byproject.labels(k).set(v)

#
# Total Queued Tasks by User
#
def tot_queued_tasks_byUser(myquery):
   tasks_dict = {}
   allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
   for j in allJobs.get('Jobs',[]):
       user = j.get('user',"unknown")
       tasks = j.get('taskid',"unknown")
       # Taskid--> "6-8:1"
       if tasks:
          t = tasks.split(':')
          task = t[0].split('-')
          value = int(task[1]) - int(task[0])
       count = tasks_dict.get(user,0)
       count += value
       tasks_dict[user] = count
   for k, v in tasks_dict.items():
       gauge_tot_tasks_queued_byuser.labels(k).set(v)


#
# Total Queued Tasks by Project
#
def tot_queued_tasks_byProject(myquery):
   tasks_dict = {}
   allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
   for j in allJobs.get('Jobs',[]):
       project = j.get('project',"unknown")
       tasks = j.get('taskid',"unknown")
       # Taskid--> "6-8:1"
       if tasks:
          t = tasks.split(':')
          task = t[0].split('-')
          value = int(task[1]) - int(task[0])
       count = tasks_dict.get(project,0)
       count += value
       tasks_dict[project] = count
   for k, v in tasks_dict.items():
       gauge_tot_tasks_queued_byproject.labels(k).set(v)

#
# Total Queued Jobs by User
#
def tot_queued_jobs_byUser(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        user = j.get('user',"unknown")
        cont_jobq_user = job_dict.get(user,0)
        cont_jobq_user+=1
        job_dict[user] = cont_jobq_user
    for k, v in job_dict.items():
        gauge_tot_jobs_queued_byuser.labels(k).set(v)

#
# Total Queued Jobs by Project
#
def tot_queued_jobs_byProject(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        project = j.get('project',"unknown")
        cont_jobq_project = job_dict.get(project,0)
        cont_jobq_project+=1
        job_dict[project] = cont_jobq_project
    for k, v in job_dict.items():
        gauge_tot_jobs_queued_byproject.labels(k).set(v)

################################################
# Used CPU Time,vmem, Wallclock and IO by User #
################################################

# Mem Usage by User
def tot_job_usage_mem_byUser(myquery):
    job_dict = {}
    tot_mem_usage = 0
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        user = j.get('user',"unknown")
        conunt_mem_usage = job_dict.get(user,0)
        jobmem = j.get('usage',0).get('mem',0)      
        conunt_mem_usage += jobmem
        job_dict[user] = conunt_mem_usage
        tot_mem_usage += conunt_mem_usage
    for k, v in job_dict.items():
        gauge_job_usage_mem_byuser.labels(k).set(v)
    gauge_tot_usage_mem.set(tot_mem_usage)

# IOWaiting Usage by User
def tot_job_usage_iow_byUser(myquery):
    job_dict = {}
    tot_iow_usage = 0
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        user = j.get('user',"unknown")
        conunt_usage = job_dict.get(user,0)
        iow = j.get('usage',0).get('iow',0)
        conunt_usage += iow
        job_dict[user] = conunt_usage
        tot_iow_usage += conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_iow_byuser.labels(k).set(v)
    gauge_tot_usage_iow.set(tot_iow_usage)

# IO Usage by User
def tot_job_usage_io_byUser(myquery):
    job_dict = {}
    total_value = 0
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        user = j.get('user',"unknown")
        conunt_usage = job_dict.get(user,0)
        io = j.get('usage',0).get('io',0)
        conunt_usage += io
        job_dict[user] = conunt_usage
        total_value += conunt_usage 
    for k, v in job_dict.items():
        gauge_job_usage_io_byuser.labels(k).set(v)
    gauge_tot_usage_iow.set(total_value)

# wallclock Usage by User
def tot_job_usage_wallclock_byUser(myquery):
    job_dict = {}
    total_value = 0
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        user = j.get('user',"unknown")
        conunt_usage = job_dict.get(user,0)
        wallclock = j.get('usage',0).get('wallclock',0)
        conunt_usage += wallclock
        job_dict[user] = conunt_usage
        total_value += conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_wallclock_byuser.labels(k).set(v)
    gauge_tot_usage_wallclock.set(total_value)

# CPU Usage by User
def tot_job_usage_cpu_byUser(myquery):
    job_dict = {}
    total_value = 0
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        user = j.get('user',"unknown")
        conunt_usage = job_dict.get(user,0)
        cpu = j.get('usage',0).get('cpu',0)
        conunt_usage += cpu
        job_dict[user] = conunt_usage
        total_value += conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_cpu_byuser.labels(k).set(v)
    gauge_tot_usage_cpu.set(total_value)

# vmem Usage by User
def tot_job_usage_vmem_byUser(myquery):
    job_dict = {}
    total_value = 0
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        user = j.get('user',"unknown")
        conunt_usage = job_dict.get(user,0)
        vmem = j.get('usage',0).get('vmem',0)
        conunt_usage += vmem
        job_dict[user] = conunt_usage
        total_value += conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_vmem_byuser.labels(k).set(v)
    gauge_tot_usage_vmem.set(total_value)

# Maxvmem Usage by User
def tot_job_usage_maxvmem_byUser(myquery):
    job_dict = {}
    total_value = 0
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]): 
        user = j.get('user',"unknown")
        conunt_usage = job_dict.get(user,0)
        maxvmem = j.get('usage',0).get('maxvmem',0)
        conunt_usage += maxvmem
        job_dict[user] = conunt_usage
        total_value += conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_maxvmem_byuser.labels(k).set(v)
    gauge_tot_usage_maxvmem.set(total_value)

###################################################
# Used CPU Time,vmem, Wallclock and IO by Project #
###################################################

# Mem Usage by Project
def tot_job_usage_mem_byProject(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        project = j.get('project',"unknown")
        conunt_mem_usage = job_dict.get(project,0)
        jobmem = j.get('usage',0).get('mem',0)
        conunt_mem_usage += jobmem
        job_dict[project] = conunt_mem_usage
    for k, v in job_dict.items():
        gauge_job_usage_mem_byproject.labels(k).set(v)

# IOWaiting Usage by Project
def tot_job_usage_iow_byProject(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        project = j.get('project',"unknown")
        conunt_usage = job_dict.get(project,0)
        iow = j.get('usage',0).get('iow',0)
        conunt_usage += iow
        job_dict[project] = conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_iow_byproject.labels(k).set(v)

# IO Usage by Project
def tot_job_usage_io_byProject(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        project = j.get('project',"unknown")
        conunt_usage = job_dict.get(project,0)
        io = j.get('usage',0).get('io',0)
        conunt_usage += io
        job_dict[project] = conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_io_byproject.labels(k).set(v)

# wallclock Usage by Project
def tot_job_usage_wallclock_byProject(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        project = j.get('project',"unknown")
        conunt_usage = job_dict.get(project,0)
        wallclock = j.get('usage',0).get('wallclock',0)
        conunt_usage += wallclock
        job_dict[project] = conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_wallclock_byproject.labels(k).set(v)

# CPU Usage by Project
def tot_job_usage_cpu_byProject(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        project = j.get('project',"unknown")
        conunt_usage = job_dict.get(project,0)
        cpu = j.get('usage',0).get('cpu',0)
        conunt_usage += cpu
        job_dict[project] = conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_cpu_byproject.labels(k).set(v)

# vmem Usage by Project
def tot_job_usage_vmem_byProject(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        project = j.get('project',"unknown")
        conunt_usage = job_dict.get(project,0)
        vmem = j.get('usage',0).get('vmem',0)
        conunt_usage += vmem
        job_dict[project] = conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_vmem_byproject.labels(k).set(v)

# Maxvmem Usage by Project
def tot_job_usage_maxvmem_byProject(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        project = j.get('project',"unknown")
        conunt_usage = job_dict.get(project,0)
        maxvmem = j.get('usage',0).get('maxvmem',0)
        conunt_usage += maxvmem
        job_dict[project] = conunt_usage
    for k, v in job_dict.items():
        gauge_job_usage_maxvmem_byproject.labels(k).set(v)

#########################
# Usage by every JobID  #
#########################

# Mem Usage by JobID
def jobid_mem_usage(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        job = j.get('jobid',"unknown")
        conunt_mem_usage = job_dict.get(job,0)
        jobmem = j.get('usage',0).get('mem',0)
        conunt_mem_usage += jobmem
        job_dict[job] = conunt_mem_usage
    for k, v in job_dict.items():
        gauge_jobid_usage_mem.labels(k).set(v)

# iow Usage by JobID
def jobid_iow_usage(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        job = j.get('jobid',"unknown")
        conunt_usage = job_dict.get(job,0)
        current = j.get('usage',0).get('iow',0)
        conunt_usage += current
        job_dict[job] = conunt_usage
    for k, v in job_dict.items():
        gauge_jobid_usage_iow.labels(k).set(v)

# io Usage by JobID
def jobid_io_usage(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        job = j.get('jobid',"unknown")
        conunt_usage = job_dict.get(job,0)
        current = j.get('usage',0).get('io',0)
        conunt_usage += current
        job_dict[job] = conunt_usage
    for k, v in job_dict.items():
        gauge_jobid_usage_io.labels(k).set(v)

# wallclock Usage by JobID
def jobid_wallclock_usage(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        job = j.get('jobid',"unknown")
        conunt_usage = job_dict.get(job,0)
        current = j.get('usage',0).get('wallclock',0)
        conunt_usage += current
        job_dict[job] = conunt_usage
    for k, v in job_dict.items():
        gauge_jobid_usage_wallclock.labels(k).set(v)

# vmem Usage by JobID
def jobid_vmem_usage(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        job = j.get('jobid',"unknown")
        conunt_usage = job_dict.get(job,0)
        current = j.get('usage',0).get('vmem',0)
        conunt_usage += current
        job_dict[job] = conunt_usage
    for k, v in job_dict.items():
        gauge_jobid_usage_vmem.labels(k).set(v)


# cpu Usage by JobID
def jobid_cpu_usage(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        job = j.get('jobid',"unknown")
        conunt_usage = job_dict.get(job,0)
        current = j.get('usage',0).get('cpu',0)
        conunt_usage += current
        job_dict[job] = conunt_usage
    for k, v in job_dict.items():
        gauge_jobid_usage_cpu.labels(k).set(v)

# maxvmem Usage by JobID
def jobid_maxvmem_usage(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        job = j.get('jobid',"unknown")
        conunt_usage = job_dict.get(job,0)
        current = j.get('usage',0).get('maxvmem',0)
        conunt_usage += current
        job_dict[job] = conunt_usage
    for k, v in job_dict.items():
        gauge_jobid_usage_maxvmem.labels(k).set(v)

# ioops Usage by JobID
def jobid_ioops_usage(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        job = j.get('jobid',"unknown")
        conunt_usage = job_dict.get(job,0)
        current = j.get('usage',0).get('ioops',0)
        conunt_usage += current
        job_dict[job] = conunt_usage
    for k, v in job_dict.items():
        gauge_jobid_usage_ioops.labels(k).set(v)

#################
# Server Health #
#################


# memUsage by server
def server_info_memusage(myquery):
    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        conunt_usage = host_dict.get(hostname,0)
        usage = h.get('resourceNumericValues',0).get('mem_used',0)
        conunt_usage += usage
        host_dict[hostname] = conunt_usage
    for k, v in host_dict.items():
        gauge_server_mem_usage.labels(k).set(v)

# mem free by server
def server_info_memfree(myquery):
    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        conunt_usage = host_dict.get(hostname,0)
        usage = h.get('resourceNumericValues',0).get('mem_free',0)
        conunt_usage += usage
        host_dict[hostname] = conunt_usage
    for k, v in host_dict.items():
        gauge_server_mem_free.labels(k).set(v)


# jobCount by server
def server_info_jobcount(myquery):

    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        conunt_usage = host_dict.get(hostname,0)
        jobcount = h.get('jobCount',0)
        #usage = h.get('resourceNumericValues',0).get('jobCount',0)
        conunt_usage += jobcount
        host_dict[hostname] = conunt_usage
    for k, v in host_dict.items():
        gauge_server_jobcount_usage.labels(k).set(v)
        

# np_load_avg by server
def server_info_np_load_avg(myquery):

    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        conunt_usage = host_dict.get(hostname,0)
        np_load = h.get('resourceNumericValues',0).get('np_load_avg',0)
        conunt_usage += np_load
        host_dict[hostname] = conunt_usage
    for k, v in host_dict.items():
        gauge_server_np_load_avg.labels(k).set(v)

# cpu by server
def server_info_cpu(myquery):
    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        count_usage = host_dict.get(hostname,0)
        value = h.get('resourceNumericValues',0).get('cpu',0)
        count_usage += value
        host_dict[hostname] = count_usage
    for k, v in host_dict.items():
        gauge_server_cpu.labels(k).set(v)

# virtual_mem used by server
def server_info_virtual_mem(myquery):
    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        count_usage = host_dict.get(hostname,0)
        value = h.get('resourceNumericValues',0).get('virtual_used',0)
        count_usage += value
        host_dict[hostname] = count_usage
    for k, v in host_dict.items():
        gauge_server_virtualmem_used.labels(k).set(v)

# local scratch used by server
def server_info_local_scratch_total(myquery):
    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        count_usage = host_dict.get(hostname,0)
        value = h.get('resourceNumericValues',0).get('opt_total_space',0)
        count_usage += float(value)
        host_dict[hostname] = count_usage
    for k, v in host_dict.items():
        gauge_server_scratch_total.labels(k).set(v)

# local scratch used by server
def server_info_local_scratch_used(myquery):
    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        count_usage = host_dict.get(hostname,0)
        value = h.get('resourceNumericValues',0).get('opt_used_space',0)
        count_usage += float(value)
        host_dict[hostname] = count_usage
    for k, v in host_dict.items():
        gauge_server_scratch_used.labels(k).set(v)

#gauge_server_execd_status = Gauge('server_execd_status', 'Execd process running in the server',['hostname'])
# Execd_status in the server. # Values 0 or 1
def server_info_execd_status(myquery):
    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        #count_usage = host_dict.get(hostname,0)
        value = h.get('resourceNumericValues',0).get('execd_running',0)
        #count_usage += float(value)
        host_dict[hostname] = value
    for k, v in host_dict.items():
        gauge_server_execd_status.labels(k).set(v)

#gauge_scratch_used = Gauge('scratch_used_in_host', 'Scratch used in the host',['hostname'])
def server_info_scratch_used_status(myquery):
    host_dict = {}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        #count_usage = host_dict.get(hostname,0)
        value = h.get('resourceNumericValues',0).get('opt_used_space',0)
        if float(value) >= 6:
           val = 0
        else:
           val = 1
        host_dict[hostname] = val
    for k, v in host_dict.items():
        gauge_scratch_used.labels(k).set(v)


#
# Total number of Cores, Memory,Execds, etc
#
def cluster_info(myquery):
    cores = 0
    mem = 0
    nodes = 0
    mem_in_use = 0
    nodes_in_use = 0
    cpu = 0
    np_load = 0 
    opt_total_space = 0
    opt_used_space = 0
    opt_avail_space = 0

    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        #hostname = h.get('hostname',"unknown")
        num_proc = h.get('resourceNumericValues',0).get('num_proc',0)
        mem_total = h.get('resourceNumericValues',0).get('mem_total',0)
        mem_used = h.get('resourceNumericValues',0).get('mem_used',0)
        np_load_avg = h.get('resourceNumericValues',0).get('np_load_avg',0)
        opt_total = h.get('resourceNumericValues',0).get('opt_total_space',0) 
        opt_used = h.get('resourceNumericValues',0).get('opt_used_space',0)
        opt_avail = h.get('resourceNumericValues',0).get('opt_avail_space',0)
 
        cpu_used = h.get('cpu',0)
        jobs = h.get('jobCount',0)
        if jobs > 0 :
           nodes_in_use+=1
        cores += num_proc
        nodes += 1
        mem += mem_total
        mem_in_use += mem_used
        cpu += cpu_used 
        np_load += np_load_avg
        opt_total_space += float(opt_total)
        opt_used_space += float(opt_used)
        opt_avail_space += float(opt_avail)

    gauge_tot_cores.set(cores)
    gauge_available_memory.set(mem)
    gauge_tot_nodes.set(nodes)
    #gauge_tot_mem_used_byHost.set(mem_in_use)
    gauge_mem_used_byHost.set(mem_in_use)
    gauge_nodes_in_use.set(nodes_in_use)

    # cpu load
    load = 0
    npload = 0
    if nodes > 0:
        load = cpu/nodes
        npload = np_load/nodes
    gauge_cluster_cpu_load.set(load)
    # no_load_avg
    gauge_cluster_np_load_avg.set(npload)

    # opt_total_space
    gauge_opt_total.set(opt_total_space) 
    # opt_avail_space
    gauge_opt_avail.set(opt_avail_space)
    # opt_used_space
    gauge_opt_used.set(opt_used_space)


#
# Jobs by State
#
def jobs_by_state(myquery):

    job_status_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    # Walk the results setting our metrics
    for j in allJobs.get('Jobs',[]):
        state = j.get('state',"unknown")
        count = job_status_dict.get(state,0)
        count+=1
        job_status_dict[state] = count
    for k, v in job_status_dict.items():
        gauge_jobs.labels(k).set(v)

#
# Jobs per Queue
#
def jobs_per_queue(myquery):
    job_queue_name_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        queue_name = j.get('queue_name',"unknown")
        count = job_queue_name_dict.get(queue_name,0)
        count+=1
        job_queue_name_dict[queue_name] = count
    for k, v in job_queue_name_dict.items():
        gauge_jobs_in_queue.labels(k).set(v)


def get_queue_slots(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        queue_name = j.get('queue_name',"unknown")
        count = job_dict.get(queue_name,0)
        slots = j.get('slots',0)
        count+=slots
        job_dict[queue_name] = count
    for k, v in job_dict.items():
        gauge_slots_in_queue.labels(k).set(v)

def get_mem_per_queue(myquery):
    job_dict = {}
    allJobs = json.loads(myquery).get('data',{}).get('allJobs',{})
    for j in allJobs.get('Jobs',[]):
        queue_name = j.get('queue_name',"unknown")
        count = job_dict.get(queue_name,0)
        mem = j.get('usage',0).get('mem',0)
        count+=mem
        job_dict[queue_name] = count
    for k, v in job_dict.items():
        gauge_mem_used_per_queue.labels(k).set(v)

def get_np_load_avg(myquery):
    host_dict ={}
    allHosts = json.loads(myquery).get('data',{}).get('allHosts',{})
    for h in allHosts.get('Hosts',[]):
        hostname = h.get('hostname',"unknown")
        np_load_avg = h.get('resourceNumericValues',0).get('np_load_avg',0)
        host_dict[hostname] = np_load_avg
    for k, v in host_dict.items():
        gauge_np_load_avg.labels(k).set(v)
