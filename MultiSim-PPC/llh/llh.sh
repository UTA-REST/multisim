#!/bin/bash


ppcbase=/data/user/bjones/MultiSimGitHub/MultiSim-PPC/
ice=$ppcbase/ice
ppc=$ppcbase/gpu/ppc
. $ppcbase/ocl/src
. $ppcbase/llh/src

cp /data/user/bjones/MultiSimGitHub/MultiSim-PPC/llh/cdom.txt .
cp /data/user/bjones/MultiSimGitHub/MultiSim-PPC/llh/list.bad .
strings=36


m=0
k=$[$1+0]
a=$1
q=$2
s=$3
lowdom=$4
highdom=$5
echo $s
ICEM="/Amp0/"
ICEM+=$2
if test "$FWID" = ""; then FWID=12; fi
if test "$SREP" = ""; then SREP=10; fi

echo "SHIFT $q"

for b in $q""; do
echo $b
n=0

for str in $strings; do

    det=86
  if test $str == $s; then 
      echo "STRING $str"
      # Add a 1 here to avoid PPC startup issue
      for dom in 1 `seq $lowdom $highdom`; do
	fla=${str}_$dom
	dat=/data/user/bjones/MultiSimGitHub/MultiSim-PPC/dat/all/oux.$fla

	if test -e $dat; then 
	    echo "DOM $dom" 
	    if ! test -e ./fit.$b-$n; then
		mkdir ./fit.$b-$n
	    fi
	    num=`cat $ppcbase/dat/all/num.$fla`
	#    num=10

	    echo $fla > ./fit.$b-$n/fla
	    ln -sf $dat ./fit.$b-$n/dat
	    ln -s /data/user/bjones/MultiSimGitHub/MultiSim-PPC/llh/llh ./fit.$b-$n/llh	
	       
	    ( cat $ppcbase/ice/bad-f2k $ppcbase/dat/detector/bad.ic$det; echo $str $dom; awk '$1=='$str' && $2=='$dom' {print $3, $4}' list.bad ) > ./fit.$b-$n/bad
	    echo "Running"
	    here=$PWD
	    cd ./fit.$b-$n
	    PPCTABLESDIR=$ice/ ICEM=$ICEM FWID=$FWID SREP=$SREP DREP=$num FLSH=$fla FAIL=1 FAST=1 MLPD=0 CYLR=1 FLOR=0 FSEP=1 GSL_RNG_SEED=$RANDOM ./llh $m 2> tmp
	    head -n 20 tmp
	    tail -n 10 tmp
	    rm tmp
	    cd $here
	    
	    n=$[$n+1]
	fi
    done
   fi

done
done

set -o pipefail

echo "done"
