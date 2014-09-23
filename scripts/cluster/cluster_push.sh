#!/bin/bash -e

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

USER=adria
SERVER=gaudi
SERVER_HOME=/scratch/nas/1/adria
SERVER_DIR=$USER@$SERVER:$SERVER_HOME

#boost
rsync -aP --delete --exclude 'libs' --exclude 'tools' --exclude 'doc' $BOOST $SERVER_DIR/

#postgres
rsync -aP --delete --exclude 'build' --exclude '.git' $PGPATH $SERVER_DIR/

#zsim
rsync -aP --delete --exclude 'build' --exclude '.git' --exclude 'DRAMSim2/' --exclude 'mcpat*' --exclude 'nvmain/.hg' --exclude 'nvmain/build' --exclude 'results' $ZSIMPATH $SERVER_DIR/

#queries
rsync -aP --delete $BASEDIR/../../benchmarks/queries $SERVER_DIR/

#datadir
rsync -aP --delete $BASEDIR/../../data/pgdata1GB-tpch $SERVER_DIR/

#spec
rsync -aP --delete --exclude 'cpu2006_original'  --exclude 'cpu2006_scripts'  --exclude 'execution_scripts' --exclude 'scripts' $SPECDIR $SERVER_DIR/

#install
scp $BASEDIR/cluster_build.sh $SERVER_DIR

ssh $USER@$SERVER $SERVER_HOME/cluster_build.sh
