#!/bin/bash -e

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

# Compile postgres
echo "Compile postgres"
cd $PGPATH
./install.sh

# Compile DramSim2
cd $DRAMSIMPATH
make clean
make libdramsim.so

# Compile zsim
echo "Compile zsim"
cd $ZSIMPATH
scons -j8
