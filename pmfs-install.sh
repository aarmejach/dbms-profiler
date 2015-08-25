#!/bin/bash -e

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

# Compile postgres
echo "Compile postgres"
cd $PGPATH
./install.sh
