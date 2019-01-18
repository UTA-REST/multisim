#!/bin/bash


ppcbase=/data/user/bjones/MultiSimGitHub/MultiSim-PPC/
ice=$ppcbase/ice
ppc=$ppcbase/gpu/ppc
. $ppcbase/ocl/src
. $ppcbase/llh/src

cp $ppcbase/llh/cdom.txt .
cp $ppcbase/llh/list.bad .
strings=36

if [ -z ${_CONDOR_SCRATCH_DIR+x} ]
then
    mkdir "/scratch/$USER"
    BaseDir="/scratch/$USER"
else
    BaseDir=$_CONDOR_SCRATCH_DIR
fi


m=0
k=$[$1+0]
a=$1
q=$2
s=$3
lowdom=$4
highdom=$5
ICEM="/$6/"
echo $s
#ICEM="/Amp0/"
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
      #Add another 1 here for PPC LLH startup issue
      for dom in 1 `seq $lowdom $highdom`; do
	fla=${str}_$dom
	dat=$ppcbase/dat/all/oux.$fla

	if test -e $dat; then 
	    echo "DOM $dom" 
	    if ! test -e $BaseDir/fit.$b-$n; then
		mkdir $BaseDir/fit.$b-$n
	    fi
	    num=`cat $ppcbase/dat/all/num.$fla`
	#    num=10

	    echo $fla > $BaseDir/fit.$b-$n/fla
	    ln -sf $dat $BaseDir/fit.$b-$n/dat
	    ln -s $ppcbase/llh/llh $BaseDir/fit.$b-$n/llh	
	       
	    ( cat $ppcbase/ice/bad-f2k $ppcbase/dat/detector/bad.ic$det; echo $str $dom; awk '$1=='$str' && $2=='$dom' {print $3, $4}' list.bad ) > $BaseDir/fit.$b-$n/bad
	    echo "Running"
	    here=$PWD
	    cd $BaseDir/fit.$b-$n
	    PPCTABLESDIR=$ice/ ICEM=$ICEM FWID=$FWID SREP=$SREP DREP=$num FLSH=$fla FAIL=1 FAST=1 MLPD=0 CYLR=1 FLOR=0 FSEP=1 GSL_RNG_SEED=$RANDOM ./llh $m 2> $BaseDir/tmpf
	    head -n 20 $BaseDir/tmpf
	    tail -n 10 $BaseDir/tmpf
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
