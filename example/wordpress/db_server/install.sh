#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
apt-get -qq update
apt-get install -qq -y mysql-server
exit 0
