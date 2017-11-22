#!/bin/bash
function append_conf_option() {
                KEY=$1
                VALUE=$2
                FILE=$3
                [ "$(grep "$KEY" $FILE | wc -l)" -gt "0" ] && echo "No need to do anything" && return
                LINE_NO=$[$(grep -n "<configuration>" "$FILE" | cut -d: -f1)+1]
                sed -i "${LINE_NO}i\ \t<property>\n\t\t<name>$KEY</name>\n\t\t<value>$VALUE</value>\n\t</property>" $FILE
}

CORES="$(cat /proc/cpuinfo | grep processor | wc -l)"
MEM="$(cat /proc/meminfo | grep MemTotal| awk '{printf $2/1024}' | cut -d. -f1)"

HADOOP_DIR="/opt/hadoop-2.7.4"

# configure core-site.xml
CONF_FILE="$HADOOP_DIR/etc/hadoop/core-site.xml"
append_conf_option "fs.defaultFS" "hdfs://hadoop-master/"  "$CONF_FILE"
append_conf_option "io.file.buffer.size" "65536" "$CONF_FILE"

# configure hdfs-site.xml
CONF_FILE="$HADOOP_DIR/etc/hadoop/hdfs-site.xml"
append_conf_option "dfs.namenode.name.dir" "/opt/namenode" "$CONF_FILE"
append_conf_option "dfs.datanode.data.dir" "/opt/datanode" "$CONF_FILE"
append_conf_option "dfs.replication" "1" "$CONF_FILE"
append_conf_option "dfs.blocksize" "65536" "$CONF_FILE"

# configure mapred-site.xml
CONF_FILE="$HADOOP_DIR/etc/hadoop/mapred-site.xml"
cp $CONF_FILE.template $CONF_FILE
append_conf_option "mapreduce.framework.name" "yarn" "$CONF_FILE"
append_conf_option "mapreduce.map.memory.mb" "$MEM" "$CONF_FILE"
append_conf_option "mapreduce.map.cpu.vcores" "$CORES" "$CONF_FILE"
append_conf_option "mapreduce.reduce.memory.mb" "$MEM" "$CONF_FILE"
append_conf_option "mapreduce.reduce.cpu.vcores" "$CORES" "$CONF_FILE"
append_conf_option "mapreduce.map.java.opts" "-Xmx$MEM" "$CONF_FILE"
append_conf_option "mapreduce.reduce.java.opts" "-Xmx$MEM" "$CONF_FILE"

# configure yarn-site.xml
CONF_FILE="$HADOOP_DIR/etc/hadoop/yarn-site.xml"
append_conf_option "yarn.resourcemanager.hostname" "hadoop-master" "$CONF_FILE"
append_conf_option "yarn.nodemanager.aux-services" "mapreduce_shuffle" "$CONF_FILE"
append_conf_option "yarn.nodemanager.resource.cpu-vcores" "$CORES" "$CONF_FILE"
append_conf_option "yarn.nodemanager.resource.memory-mb" "$MEM" "$CONF_FILE"
append_conf_option "yarn.scheduler.maximum-allocation-mb" "$MEM" "$CONF_FILE"
append_conf_option "yarn.scheduler.maximum-allocation-vcores" "$CORES" "$CONF_FILE"
append_conf_option "yarn.scheduler.minimum-allocation-mb" "256" "$CONF_FILE"


# configure hadoop-env.sh
CONF_FILE="$HADOOP_DIR/etc/hadoop/hadoop-env.sh"
sed -i "/JAVA_HOME/d" $CONF_FILE
echo "export JAVA_HOME=\"/usr/lib/jvm/default-java\"" >> $CONF_FILE

# configure yarn-env.sh
#CONF_FILE="$HADOOP_DIR/etc/hadoop/yarn-env.sh"
#sed -i "/JAVA_HOME/d" $CONF_FILE
#echo "export JAVA_HOME=\"/usr/lib/jvm/default-java\"" >> $CONF_FILE

# configure slaves
CONF_FILE="$HADOOP_DIR/etc/hadoop/slaves"
echo -n > $CONF_FILE
for h in $(grep hadoop-slave /etc/hosts | awk '{print $2}'); do
		echo $h >> $CONF_FILE
done
echo "Configuration DONE"
exit 0
