#!/bin/bash
echo "aura-one/script3.sh"
for i in $(cat $1); do 
		echo "Received: $i";
done
