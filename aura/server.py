#!/usr/bin/python

from flask import Flask, render_template, redirect, abort, Response
import os
from aura.core import ApplicationDescriptionParser, ApplicationDeployment
import json
from sys import argv
import uuid
from threading import Thread
import logging
from copy import deepcopy

app = Flask("aura")

class AURAContext:
    def __init__(self):
        pass
        
    def allocate(self, conf):
        self.applications = {}
        for path in conf['applications']:
            parser = ApplicationDescriptionParser(path)
            desc = parser.get_description()
            desc['path'] = path
            desc['id'] = str(uuid.uuid4())
            self.applications[desc['id']] = desc

        self.deployments = {}

        self.config = conf

global context
context = AURAContext()

# API
@app.route("/")
def index():
    return redirect('/application/')

@app.route("/application/")
def application_list():
    return render_template("application_list.html", apps = context.applications.values())

@app.route("/application/<app_id>")
def application_show(app_id):
    if app_id not in context.applications:
        abort(404)
    return render_template("application_view.html", app = context.applications[app_id])

@app.route("/application/<app_id>/deploy")
def application_deploy(app_id):
    if app_id not in context.applications:
        abort(404)
    parser = ApplicationDescriptionParser(context.applications[app_id]['path'])
    desc = parser.expand_description()
    logging.info(desc)
    d = ApplicationDeployment(desc, context.config)
    deployment_id = str(uuid.uuid4())
    context.deployments[deployment_id] = d
    t = Thread(target = d.run)
    t.start()
    return redirect("/deployments/%s" % (deployment_id))


@app.route("/deployments/")
def deployment_list():
    deps = []
    for x in context.deployments.keys():
        cur = context.deployments[x].status()
        cur['id'] = x
        deps.append(cur)
    return render_template("deployment_list.html", deps = deps)

@app.route("/deployments/<dep_id>")
def deployment_show(dep_id):
    if dep_id not in context.deployments:
        abort(404)
    deployment = context.deployments[dep_id].status()
    deployment['id'] = dep_id
    return render_template("deployment_view.html", deployment = deployment)


@app.route("/deployments/<dep_id>/delete")
def deployment_delete(dep_id):
    if dep_id not in context.deployments:
        abort(404)
    deployment = context.deployments[dep_id]
    deployment.delete()
    del context.deployments[dep_id]
    return redirect("/deployments/")

@app.route("/deployments/<dep_id>/status")
def deployment_status(dep_id):
    if dep_id not in context.deployments:
        abort(404)
    deployment = context.deployments[dep_id]
    return json.dumps(deployment.status())

@app.route("/deployments/<dep_id>/<module_name>/<script_seq>/<log_type>/")
def deployment_script_logs(dep_id, module_name, script_seq, log_type):
    if dep_id not in context.deployments:
        abort(404)
    print "(%s, %s, %s, %s)" % (dep_id, module_name, script_seq, log_type)
    deployment = context.deployments[dep_id].status()
    for m in deployment['modules']:
        print m
        for s in m['scripts']:
            print s
            if m['name'] == module_name and script_seq == str(s['seq']):
                if log_type == 'stdout' or log_type == 'stderr':
                    if log_type in s:
                        return Response(s[log_type], mimetype='text/plain', headers={"Content-Disposition": "attachment;filename=%s_%s_%s_%s.log" % (dep_id, module_name, script_seq, log_type)})
                    else:
                        return "Nothing yet"
    return "Not found"

@app.route("/about/")
def about():
    return render_template("about.html")
