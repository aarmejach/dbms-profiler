#!/bin/bash -e

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

USER=testuser
SERVER=axle.bsc.es
SERVER_HOME=/home/$USER
SERVER_DIR=$USER@$SERVER:$SERVER_HOME

#dbms-profiler
rsync -aP --delete --exclude 'results*' --exclude 'data' --exclude 'figures' --exclude '.hg' $BASEDIR $SERVER_DIR/

#postgres
rsync -aP --delete --exclude 'build' --exclude '.git' $PGPATH $SERVER_DIR/

#install
scp pmfs-install.sh $SERVER_DIR

ssh $USER@$SERVER $SERVER_HOME/dbms-profiler/pmfs-install.sh
