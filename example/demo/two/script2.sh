#!/bin/bash

CHANCE="0.60"
if [ "$(printf "%0.2f\n" $(echo print "$RANDOM/32767." | perl))" \< "$CHANCE" ]; then
	   	echo "Failed script" 1>&2 
		sleep 1
		exit 0
fi

for i in $(cat $1); do 
		echo "Received: $i";
done

echo "$(hostname)"
