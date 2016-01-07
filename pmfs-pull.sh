#!/bin/bash

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

USER=testuser
SERVER=axle.bsc.es
SERVER_HOME=/home/$USER
SERVER_DIR=$USER@$SERVER:$SERVER_HOME
RESULTS_DIR=dbms-profiler/results/

rsync -aP --exclude="perf.data" $SERVER_DIR/$RESULTS_DIR results-axle-pmfs

#ssh $SERVER $SERVER_HOME/script.sh
