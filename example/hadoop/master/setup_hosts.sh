#!/bin/bash
IP_ADDRESS="$(ip addr show| grep "inet\s" |  grep -v "127.0" | awk '{print $2}' | cut -d'/' -f1)"

echo -e "$IP_ADDRESS\t$HOSTNAME" >> /etc/hosts
echo -e "$IP_ADDRESS\t$HOSTNAME"
for l in $(cat $1); do
	ADDR=$(echo $l | cut -d,  -f1)
	NAME=$(echo $l | cut -d,  -f2)

	echo -e "$ADDR\t$NAME" >> /etc/hosts
	echo -e "$ADDR\t$NAME"
done
