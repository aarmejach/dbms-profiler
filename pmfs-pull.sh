#!/bin/bash

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

USER=aarmejach
SERVER=84.88.52.252
SERVER_HOME=/home/$USER
SERVER_DIR=$USER@$SERVER:$SERVER_HOME
RESULTS_DIR=dbms-profiler/results/

rsync -aP --exclude="perf.data" $SERVER_DIR/$RESULTS_DIR results-pmfs

#ssh $SERVER $SERVER_HOME/script.sh
