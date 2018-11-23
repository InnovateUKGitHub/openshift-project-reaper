# openshift-project-reaper

This tool can auto-delete up openshift projects that are older than a specific age.  A list of projects to retain can also be specified.


## Preparation


### On Linux

```bash
# `apt-get install python python-virtualenv` or similar
virtualenv venv
. bin/venv/activate
pip install -r requirements.txt
```


### On OSX

I found there was a problem as the version of openssl in MacOS was too old, so I had to use the python from `brew` in the `virtualenv` command below:

```bash
brew install python
pip install virtualenv
virtualenv -p/usr/local/bin/python venv
. bin/venv/activate
pip install -r requirements.txt
```


## YAML Settings

There are only a few supported keys at present:

  - `enpoint.uri: ""` set this to point to the openshift instance endpoint
  - `endpoint.username: ""` set the username to use for Authentication
  - `endpoint.password: ""` set the password to go with the username
  - `endpoint.token:` set this to use token auth instead of username & password
  - `endpoint.options:` any additional parameters for the `oc login` command, eg. `--insecure-skip-tls-verify`
  - `projects.preserve: []` is a list of project to whitelist (ie. never delete these regardless of age)
  - `max_age_in_hours: 48` set this to the age threshold you would like, ie. projects older than this will be deleted, so long as they are not in the `preserve` list


## Testing

I created a series of projects locally and then used the `max_age_in_hours` set to 1 hour to see which would be deleted.  You could even change it to minutes in the code if you are impatient.

Test doing something like this:

- Modify `settings.yml` to have a short `default_max_age_in_hours`:

```yaml
endpoint:
  uri: https://127.0.0.1:8443
  # either...
  username: developer
  password: developer
  options: --insecure-skip-tls-verify
  # or...
  # token: xyz
projects:
  preserve:
    - coscale1
    - default
    - demo
    - innovateuk
    - kube-system
    - logging
    - management-infra
    - openshift
    - openshift-infra
    - perf
    - production
    - storage-prod
    - sysint
    - test
    - uat
  rules:
    - project: "^at-.*"
      max_age_in_hours: 18
default_max_age_in_hours: 48
```

- Run the following commands:

```bash
oc cluster up
oc new-project dev-nige-1
oc new-project dev-nige-2
oc new-project dev-nige-3
oc new-project demo
sleep 3601
oc new-project dev-nige-4
oc new-project dev-nige-5
oc new-project sysint
./reap_projects.py
```

> You should see older projects are deleted, whitelisted and younger projects are retained.

```bash
oc projects
```
