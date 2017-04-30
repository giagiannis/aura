#!/usr/bin/python

from flask import Flask


class ServerShit:
    def __init__(self):
        self.deployments = []

app = Flask(__name__)
shit = ServerShit()

@app.route("/")
def index():
    return str(shit.deployments)

@app.route("/api/add")
def add_shit():
    shit.deployments.append(1)
    return ""


if __name__ == "__main__":
    app.run()
