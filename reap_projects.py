#!/usr/bin/env python

from datetime import timedelta, datetime
from pprint import pprint
from openshift import client, config
from yaml import load, dump
import subprocess
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

with open("settings.yml", 'r') as stream:
    data = load(stream)

# FIXME Authentication should be via pyhton API
if data['endpoint'].has_key('token'):
    print "Attempting to auth using token..."
    print "--token={}".format(data['endpoint']['token'])
    result = subprocess.check_output(['oc', 'login', data['endpoint']['uri'], "--token={}".format(data['endpoint']['token'])])
else:
    print "Attempting to auth using username & password..."
    result = subprocess.check_output(['oc', 'login', '-u', data['endpoint']['username'], '-p', data['endpoint']['password'], data['endpoint']['uri']])
print result

config.load_kube_config()

oapi             = client.OapiApi()
project_list     = oapi.list_project()
now              = datetime.utcnow()
max_age_in_hours = data['max_age_in_hours']

for project in project_list.items:
    project_createtime = datetime.strptime(project.metadata.creation_timestamp, '%Y-%m-%dT%H:%M:%SZ')
    if project.metadata.name in data['projects']['preserve']:
        print "Project {} is whitelisted and will not be deleted".format(project.metadata.name)
    else:
        print "Project {} was created {}".format(project.metadata.name,project.metadata.creation_timestamp)
        if project_createtime < now - timedelta(hours = max_age_in_hours):
            print "  DELETING {} AS IT IS OLDER THAN {} HOURS".format(project.metadata.name,max_age_in_hours)
            oapi.delete_project(project.metadata.name)
        else:
            print "  Young enough to survive the reaper"
