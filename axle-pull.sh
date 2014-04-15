#!/bin/bash

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

USER=aarmejac
SERVER=axle.bsc.es
SERVER_HOME=/home/Computational/aarmejac
SERVER_DIR=$USER@$SERVER:$SERVER_HOME
RESULTS_DIR=dbms-profiler/results

rsync -aP $SERVER_DIR/$RESULTS_DIR results-axle

#ssh $SERVER $SERVER_HOME/script.sh
