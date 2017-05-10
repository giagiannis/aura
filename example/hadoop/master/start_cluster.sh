#!/bin/bash
HADOOP_DIR="/opt/hadoop-2.7.3"

# format the FS
$HADOOP_DIR/bin/hadoop namenode -format 2>&1

# start the cluster
$HADOOP_DIR/sbin/start-dfs.sh 2>&1
$HADOOP_DIR/sbin/start-yarn.sh 2>&1
