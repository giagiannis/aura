#!/bin/bash

CHANCE="0.60"
[ "$(printf "%0.2f\n" $(echo print "$RANDOM/32767." | perl))" \< "$CHANCE" ] && echo fooo 1>&2 && sleep 5 && exit 0

hostname
ip addr show
