#!/bin/bash

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

USER=adria
SERVER=axle.bsc.es
SERVER_HOME=/home/adria
SERVER_DIR=$USER@$SERVER:$SERVER_HOME
RESULTS_DIR=dbms-profiler/results*

rsync -aP $SERVER_DIR/$RESULTS_DIR .

#ssh $SERVER $SERVER_HOME/script.sh
