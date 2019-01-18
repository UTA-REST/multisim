#!/bin/bash

HE_FILE=$1
LE_FILE=$2
OUTFILE=$3

eval $(/cvmfs/icecube.opensciencegrid.org/py2-v2/setup.sh) 
if [ -z ${_CONDOR_SCRATCH_DIR+x} ]
then
    mkdir "/scratch/$USER"
    BaseDir="/scratch/$USER"
else
    BaseDir=$_CONDOR_SCRATCH_DIR
fi

mkdir ${BaseDir}/out

cp $1 ${BaseDir}/Multisim`basename $1`
cp $2 ${BaseDir}/Multisim`basename $2`
python /data/user/bjones/MultiSimUpdate/trunk/clsim/multisim/ExtractGradients/MakeSplits.py -p -n -1  -i ${BaseDir}/Multisim`basename $1` -o $3
#python /data/user/bjones/MultiSimUpdate/trunk/clsim/multisim/ExtractGradients/MakeSplits.py -a -n 24900000  -i ${BaseDir}/Multisim`basename $1`  -o ${BaseDir}/


