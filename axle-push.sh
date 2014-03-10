#!/bin/bash

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

USER=adria
SERVER=axle.bsc.es
SERVER_HOME=/home/adria
SERVER_DIR=$USER@$SERVER:$SERVER_HOME

rsync -aP --delete --exclude 'results' $BASEDIR $SERVER_DIR/

#ssh $SERVER $SERVER_HOME/script.sh
