#!/bin/bash
# add to authorized_keys file
# this first line is the public part
cat $1 | head -n 1 >> ~/.ssh/authorized_keys
cat $1 | tail -n $[$(wc -l $1 | awk '{print $1}')-1] > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa

# configure
cat >> ~/.ssh/config << EOF
Host *
StrictHostKeyChecking no
UserKnownHostsFile=/dev/null
EOF
