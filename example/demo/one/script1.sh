#!/bin/bash

CHANCE="0.60"
if [ "$(printf "%0.2f\n" $(echo print "$RANDOM/32767." | perl))" \< "$CHANCE" ]; then
	   	echo "Failed script" 1>&2 
		sleep 1
		exit 0
fi

NET_INTERFACE='eth0'
IP_ADDRESS=$(ip addr show $NET_INTERFACE | grep "inet\s" |  cat | awk '{print $2}' | cut -d'/' -f1)

echo "$(hostname),$IP_ADDRESS"
