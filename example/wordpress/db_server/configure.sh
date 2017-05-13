#!/bin/bash
CHANCE="0.60"
if [ "$(printf "%0.2f\n" $(echo print "$RANDOM/32767." | perl))" \< "$CHANCE" ]; then
	echo "Failed script" 1>&2 
	sleep 1
	exit 0
fi

sed -i -e "s/127.0.0.1/0.0.0.0/g" /etc/mysql/mysql.conf.d/mysqld.cnf
service mysql restart
exit 0
