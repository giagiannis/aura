#!/bin/bash
# helpful file used to automate the tar creation
APPLICATION_NAME="demo"
cd $APPLICATION_NAME
tar cfv $APPLICATION_NAME.tar *
mv $APPLICATION_NAME.tar ..
