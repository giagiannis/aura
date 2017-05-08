#!/bin/bash
# Apache, Mysql client, PHP installation
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install  -y -qq apache2 libapache2-mod-php apache2 php-mysql wget
service apache2 reload

# Wordpress download
cd /opt/
wget --quiet http://wordpress.org/latest.tar.gz
tar xfz latest.tar.gz
exit 0
