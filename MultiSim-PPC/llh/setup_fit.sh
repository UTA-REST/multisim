#!/bin/bash
d=$1
icem=$2
cd $d
timenow=`date +%s`
mkdir /data/user/bjones/MultiSimGitHub/Cluster/logs/${2}_$timenow
mkdir /data/user/bjones/MultiSimGitHub/Cluster/logs/${2}_${timenow}/out
mkdir /data/user/bjones/MultiSimGitHub/Cluster/logs/${2}_${timenow}/err
mkdir /data/user/bjones/MultiSimGitHub/Cluster/logs/${2}_${timenow}/log
chmod 777 /data/user/bjones/MultiSimGitHub/Cluster/logs/${2}_$timenow
chmod 777 /data/user/bjones/MultiSimGitHub/Cluster/logs/${2}_$timenow/*

ll="*"
echo "Universe        = vanilla
Notification    = never
Executable      = /data/user/bjones/MultiSimGitHub/MultiSim-PPC/llh/llhnew.sh


Output          = /data/user/bjones/MultiSimGitHub/Cluster/logs/${2}_${timenow}/out/out_\$(Process)
Error           = /data/user/bjones/MultiSimGitHub/Cluster/logs/${2}_${timenow}/err/err_\$(Process)
Log             = /data/user/bjones/MultiSimGitHub/Cluster/logs/${2}_${timenow}/log/log_\$(Process)


request_gpus    = 1
request_memory  = 8GB

requirements    = regexp(\"(gtx-8|gtx-27|gtx-33|gtx-40|rad-0)\", Machine) != True
" > /data/user/bjones/MultiSimGitHub/Cluster/condor/condorsub${2}_$timenow

for b in *.dat
do
    echo "Arguments       = 0 $b 36 1 20 $icem " >> /data/user/bjones/MultiSimGitHub/Cluster/condor/condorsub${2}_$timenow
    echo "queue" >> /data/user/bjones/MultiSimGitHub/Cluster/condor/condorsub${2}_$timenow
    echo "Arguments       = 0 $b 36 21 40 $icem" >> /data/user/bjones/MultiSimGitHub/Cluster/condor/condorsub${2}_$timenow
    echo "queue" >> /data/user/bjones/MultiSimGitHub/Cluster/condor/condorsub${2}_$timenow
    echo "Arguments       = 0 $b 36 41 60 $icem" >> /data/user/bjones/MultiSimGitHub/Cluster/condor/condorsub${2}_$timenow
    echo "queue" >> /data/user/bjones/MultiSimGitHub/Cluster/condor/condorsub${2}_$timenow

done

echo "Done"
