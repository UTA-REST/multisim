#!/bin/bash

host=`hostname -s`
home=/data/user/bjones/MultiSimGitHub/Cluster/condor
cd $home
n=$[$1+0]
b=$2
. ocl/src
. llh/src
llh=../llh/llh

mesg() { dmesg | grep llh; }
host=$host.${_CONDOR_SLOT}.gpu_${GPU_DEVICE_ORDINAL}.job_$n

dir=$home/fit.$b-$n
if test -d $dir; then
    cd $dir

    if ! test -e host; then
	echo $host > host

	env > env
	mesg > dmesg

	. run 2> log > out
	status=$?

	badl=`grep -i err log | wc -l`
	dmesg=`mesg | diff dmesg - | wc -l`

	if test $status = 0 && test $badl = 0 && test $dmesg = 0; then
	    echo $host > done
	else
	    (
		cat host
		echo -----
		cat host
		echo -----
		echo status=$status badl=$badl dmesg=$dmesg
		echo -----
		mesg | diff dmesg -
		echo -----
	    ) > fail
	    rm host
	fi
    fi
fi
