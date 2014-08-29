#!/bin/bash

NAS_HOME=/scratch/nas/1/adria
cd $NAS_HOME

# Zsim paths
export PINPATH=$NAS_HOME/zsim/pin_kit
export NVMAINPATH=$NAS_HOME/zsim/nvmain
export ZSIMPATH=$NAS_HOME/zsim
export PGPATH=$NAS_HOME/postgres
export BOOST=$NAS_HOME/boost
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$BOOST/stage/lib

# Set PATH for postgresql
export PATH=$PGPATH/build/bin:$PATH

# gcc
export CC=gcc
export CXX=g++

CORES=$(cat /proc/cpuinfo | grep processor -c)
if [ $CORES -eq 1 ]; then
    # single-core node, compile on some other node!
    echo "On single-core node $(hostname). Jumping to another node."
    qrsh -l medium $NAS_HOME/cluster_build.sh
    exit $?
else
    echo "Building on: $(hostname), with $CORES cores"
fi

# Compile zsim
cd zsim
scons -j$CORES
echo "ZSim compilation done."
echo "---------------------------------"

# Compile postgres
cd ../postgres
./install.sh
echo "Postgres compilation done."
echo "---------------------------------"
