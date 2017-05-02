#!/bin/bash

CHANCE="0.80"; [ "$(python -c "import random; print random.random()")" \< "$CHANCE" ] && echo fooo 1>&2 && sleep 5 && exit 0

hostname
ip addr show
