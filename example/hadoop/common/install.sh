#!/bin/bash

# install the prerequisites 
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq	&2>/1
apt-get install -qq -y default-jdk rsync &2>1
echo  "export JAVA_HOME=\"/usr/lib/jvm/default-java\"" >> /root/.bashrc

# download & extract HADOOP
TARBALL="hadoop-2.7.4.tar.gz"
rm -f /opt/$TARBALL
HADOOP_URL="ftp://ftp.cc.uoc.gr/mirrors/apache/hadoop/common/hadoop-2.7.4/$TARBALL"
cd /opt
wget --quiet $HADOOP_URL
tar xfa $TARBALL
