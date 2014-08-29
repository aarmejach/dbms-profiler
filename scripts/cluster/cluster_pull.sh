#!/bin/bash

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

USER=adria
SERVER=gaudi
SERVER_HOME=/scratch/nas/1/$USER
SERVER_DIR=$SERVER:$SERVER_HOME


ssh $USER@$SERVER << EndOfCommands
while [ \$(qstat | wc -l) -gt 0 ]; do
    echo Waiting on running jobs:
    qstat
    sleep 5;
done
cd $SERVER_HOME
EndOfCommands

IFS='
'

mkdir -p $BASEDIR/../../results-zsim
rsync -aP $USER@$SERVER:$SERVER_HOME/results-zsim/ $BASEDIR/../../results-zsim
