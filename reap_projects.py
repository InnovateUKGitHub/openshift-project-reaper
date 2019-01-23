#!/usr/bin/env python

from datetime import timedelta, datetime
from pprint import pprint
import urllib3
from openshift import client, config
from kubernetes.client.rest import ApiException
from yaml import load, dump
from pprint import pprint
import subprocess
import re
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def matching_rule(project_name):
    for rule in data['projects']['rules']:
        pattern = re.compile(rule['project'])
        pattern.match(project_name)
        if pattern.match(project_name):
            return rule
    return None

def process_project(project, max_age_in_hours):
    print "Project {} was created {}".format(
        project.metadata.name, project.metadata.creation_timestamp)
    if project_createtime < now - timedelta(hours=max_age_in_hours):
        print "  REAPING {} AS IT IS OLDER THAN {} HOURS".format(
            project.metadata.name, max_age_in_hours)
        try:
            api_response = oapi.delete_project(project.metadata.name)
            pprint(api_response)
        except ApiException as e:
            print("Exception when trying to delete project: %s\n" % e)
    else:
        print "  Young enough to survive the {}h reaper".format(
            max_age_in_hours)


with open("settings.yml", 'r') as stream:
    data = load(stream)

# Disable SSL warnings
urllib3.disable_warnings()

# FIXME Authentication should be via pyhton API
if data['endpoint'].has_key('token'):
    print "Attempting to auth using token..."
    print "--token={}".format(data['endpoint']['token'])
    result = subprocess.check_output(['oc', 'login', data['endpoint']['options'] if data['endpoint'].has_key('options') else '', data['endpoint']['uri'], "--token={}".format(data['endpoint']['token'])])
else:
    print "Attempting to auth using username & password..."
    result = subprocess.check_output(['oc', 'login', '-u', data['endpoint']['username'], '-p', data['endpoint']['password'], data['endpoint']['options'] if data['endpoint'].has_key('options') else '', data['endpoint']['uri']])
print result

config.load_kube_config()

oapi             = client.OapiApi()
project_list     = oapi.list_project()
now              = datetime.utcnow()
default_max_age_in_hours = data['default_max_age_in_hours']

filtered_projects = []
for project in project_list.items:
    if project.metadata.name in data['projects']['preserve']:
        print "Project {} is whitelisted and will not be deleted".format(project.metadata.name)
    else:
        filtered_projects.append(project)

print "\n"

for project in filtered_projects:
    project_createtime = datetime.strptime(project.metadata.creation_timestamp, '%Y-%m-%dT%H:%M:%SZ')
    if matching_rule(project.metadata.name) is not None:
        process_project(project, matching_rule(project.metadata.name)['max_age_in_hours'])
    else:
        process_project(project, default_max_age_in_hours)
