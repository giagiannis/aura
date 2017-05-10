#!/bin/bash

# key generation
KEY_NAME='/root/.ssh/id_rsa'
rm -f $KEY_NAME $KEY_NAME.pub
ssh-keygen -b 4096 -t rsa -N '' -f $KEY_NAME -C 'master@hadoop' > /dev/null
cat $KEY_NAME.pub
cat $KEY_NAME

# add to authorized_keys file
cat $KEY_NAME.pub >> ~/.ssh/authorized_keys

# configure
cat >> ~/.ssh/config << EOF
Host *
StrictHostKeyChecking no
UserKnownHostsFile=/dev/null
EOF
