#!/bin/bash -e

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

USER=aarmejac
SERVER=axle.bsc.es
SERVER_HOME=/home/Computational/aarmejac
SERVER_DIR=$USER@$SERVER:$SERVER_HOME

#dbms-profiler
rsync -aP --delete --exclude 'results*' --exclude 'data' --exclude 'figures' --exclude '.hg' $BASEDIR $SERVER_DIR/

#postgres
rsync -aP --delete --exclude 'build' --exclude '.git' $PGPATH $SERVER_DIR/

#zsim
rsync -aP --delete --exclude 'build' --exclude '.git' --exclude 'DRAMSim2/.git' --exclude 'nvmain/.hg' --exclude 'results' $ZSIMPATH $SERVER_DIR/

#install
scp axle-install.sh $SERVER_DIR

ssh $USER@$SERVER $SERVER_HOME/axle-install.sh
