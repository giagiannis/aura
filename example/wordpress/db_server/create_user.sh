#!/bin/bash
# $1 contains a space/newline separated list of the Web Server IP addresses
DATABASE_NAME='wordpressdb'
DATABASE_USER='wordpressuser'
DATABASE_PASS="$(openssl rand -hex 5)"
DATABASE_HOST="$(ip addr show| grep "inet\s" |  grep -v "127.0" | awk '{print $2}' | cut -d'/' -f1)"
mysql -u root  << EOF
CREATE DATABASE $DATABASE_NAME;
EOF
for IP in $(cat $1); do
mysql -u root  << EOF
CREATE USER $DATABASE_USER@'$IP' IDENTIFIED BY '$DATABASE_PASS';
GRANT ALL PRIVILEGES ON $DATABASE_NAME.* TO $DATABASE_USER@'$IP';
FLUSH PRIVILEGES;
EOF
done
echo $DATABASE_HOST,$DATABASE_NAME,$DATABASE_USER,$DATABASE_PASS
exit 0
