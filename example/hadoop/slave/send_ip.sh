#!/bin/bash
IP_ADDRESS="$(ip addr show| grep "inet\s" |  grep -v "127.0" | awk '{print $2}' | cut -d'/' -f1)"
echo $IP_ADDRESS,$HOSTNAME
