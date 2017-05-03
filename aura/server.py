#!/usr/bin/python

from flask import Flask, render_template, redirect, abort
import os
from aura.parsers import ApplicationDescriptionParser
from aura.deployment import ApplicationDeployment
import json
from sys import argv
import uuid
from threading import Thread
import logging

app = Flask("aura")


class AURAContext:
    def __init__(self, conf):
        self.applications = {}
        for path in conf['applications']:
            parser = ApplicationDescriptionParser(path)
            desc = parser.get_description()
            desc['path'] = path
            desc['id'] = str(uuid.uuid4())
            self.applications[desc['id']] = desc

        self.deployments = {}

        self.config = conf

@app.route("/")
def index():
    return redirect('/application/')

@app.route("/application/")
def application_list():
    return render_template("application_list.html", apps = context.applications.values())

@app.route("/application/<app_id>")
def application_show(app_id):
    print context.applications
    if app_id not in context.applications:
        abort(404)
    return render_template("application_view.html", app = context.applications[app_id])

@app.route("/application/<app_id>/deploy")
def application_deploy(app_id):
    if app_id not in context.applications:
        abort(404)
    d = ApplicationDeployment(context.applications[app_id], context.config)
    deployment_id = str(uuid.uuid4())
    context.deployments[deployment_id] = d
    t = Thread(target = d.run)
    t.start()
    return redirect("/deployments/%s" % (deployment_id))

@app.route("/deployments/<dep_id>")
def deployment_show(dep_id):
    if dep_id not in context.deployments:
        abort(404)
    deployment = context.deployments[dep_id]
    return render_template("deployment_view.html", deployment = deployment.status())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    context = AURAContext(json.load(open(argv[1])))
    app.run(debug=True)
