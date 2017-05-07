#!/usr/bin/python

from flask import Flask, render_template, redirect, abort
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
    d = ApplicationDeployment(deepcopy(context.applications[app_id]), context.config)
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
    deployment = context.deployments[dep_id]
    return render_template("deployment_view.html", deployment = deployment.status())


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


@app.route("/about/")
def about():
    return render_template("about.html")
