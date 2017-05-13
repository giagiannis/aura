#!/bin/bash

CHANCE="0.60"
if [ "$(printf "%0.2f\n" $(echo print "$RANDOM/32767." | perl))" \< "$CHANCE" ]; then
	echo "Failed script" 1>&2 
	sleep 1
	exit 0
fi


# parsing input
DATABASE_HOST=$(cat $1 | cut -d, -f1)
DATABASE_NAME=$(cat $1 | cut -d, -f2)
DATABASE_USER=$(cat $1 | cut -d, -f3)
DATABASE_PASS=$(cat $1 | cut -d, -f4)

# starting wordpress configuration
WORDPRESS_ROOT="/opt/wordpress/"
WWW_PUBLIC="/var/www/html/"

cd $WORDPRESS_ROOT
cp wp-config-sample.php wp-config.php
sed -i -e "s/database_name_here/$DATABASE_NAME/g" wp-config.php
sed -i -e "s/username_here/$DATABASE_USER/g" wp-config.php
sed -i -e "s/password_here/$DATABASE_PASS/g" wp-config.php
sed -i -e "s/localhost/$DATABASE_HOST/g" wp-config.php


# move everything to /var/www/html
rm -r $WWW_PUBLIC && mkdir $WWW_PUBLIC
rsync -avP $WORDPRESS_ROOT $WWW_PUBLIC
chown -R www-data:www-data $WWW_PUBLIC
mkdir $WWW_PUBLIC/wp-content/uploads
chown -R :www-data $WWW_PUBLIC/wp-content/uploads

exit 0
