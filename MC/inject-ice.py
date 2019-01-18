#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v2/icetray-start                                                                                                                                        
#METAPROJECT  /data/ana/SterileNeutrino/IC86/HighEnergy/Multisim/Metaprojects/simulation.trunk/build/

##METAPROJECT  /data/ana/SterileNeutrino/IC86/HighEnergy/Multisim/Metaprojects/simulation.trunkdebug/build/


#######################################################################################
## This script injects new ice models in between generated events.                   ##
##                                                                                   ##
##  the events are supplied in the .i3 file specified by the  --infile parameter     ##
##  the type of perturbation to apply is defined by which Perturber object is used.  ##
##                                                                                   ##
##  to specify the perturber, edit these two lines:                                  ##

from PlusModePerturber import *
ThePerturber=PlusModePerturber(os.environ['I3_BUILD']+"/ice-models/resources/models/spice_3.2")

##  the perturber has a __call__ method that accepts an IceXModelNumber and returns  ##
##  an M-Frame containing the new ice model and all relevsnt ice metadata.           ##
##                                                                                   ##
##  Then, every -e events, a new ice model is created and inserted. The events store ##
##  the corresponding IceXModelNumber for indexing purposes.                         ##
##                                                                                   ##
##       Questions? ben.jones@uta.edu or timothy.watson@mavs.uta.edu                 ##
#######################################################################################


import numpy as np
from os.path import expandvars
import copy
import subprocess
import argparse
import os, sys


from icecube import icetray, dataclasses, dataio
from icecube import clsim

parser = argparse.ArgumentParser()

parser.add_argument('-i','--infile',dest='infile', default='/data/ana/SterileNeutrino/IC86/HighEnergy/Multisim/Nominal/Gen/00001-01000/Gen_01000.i3.zst',
		help='Sets the name of the input file containing Hot muons')
parser.add_argument('-o','--outfile',dest='outfile', default='/data/user/saxani/test_Ice_01000.i3.bz2',
		help='Sets the name of the Output file')
parser.add_argument('-m','--initialmodel',dest='initial_model', default='-1',
		help='Model number to start on. If -1, use Spencers file name scheme')
parser.add_argument('-e','--eventspermodel',dest='events_per_model', default='100',
		help='Number of events to make per model used')

args = parser.parse_args()

#load arguments
infile 	 	= args.infile
outfile 	= args.outfile
initial_model   = int(args.initial_model)
EventsPerModel  = int(args.events_per_model)

# if -1, use Spencers file name scheme
if(initial_model==-1):
    initial_model = int(infile.split('_')[-1].split('.')[0] + '00000')


InputEvents = dataio.I3File(infile)


TotalEventCount=0.
while InputEvents.more():
    frame = InputEvents.pop_daq()
    TotalEventCount += 1.
print(TotalEventCount)

InputEvents = dataio.I3File(infile)

if TotalEventCount > 100000.:
	print('Rethink the seed.')

NModels = int(TotalEventCount/EventsPerModel)
TotalEventCount = int(TotalEventCount)

print('     Event Count: ' + str(TotalEventCount))
print('Number of Models: ' + str(NModels))
print('Events Per Model: ' + str(EventsPerModel))

if(not(np.remainder(TotalEventCount,EventsPerModel) == 0)):
       raise RuntimeError('Number of models is not compatible with total muon count (non-integer events per model)')



########################################################

def MakeModels(outfile, infile,ThePerturber):

	# Open a file for output
	outf = dataio.I3File(outfile, 'w')
	
	# Send the simulation frame to the outfile.
	frame = InputEvents.pop_frame(icetray.I3Frame.Simulation)	
	outf.push(frame)

        #### Select model range here #####
        ModelNumbers = range(initial_model, initial_model + NModels)        
	
        ##### By definition, a IceXModelNumber = 0 corresponds to the central model

	# Start Off-Central Model Generator Loop
	for IceXModelNumber in ModelNumbers: 
            
            frame = ThePerturber(IceXModelNumber)
            outf.push(frame)
            
            for k in range(0, EventsPerModel):
                InputEvent = InputEvents.pop_daq()
                InputEvent['IceXModelNumber'] = frame['IceXModelNumber']
                outf.push(InputEvent)
	outf.close()
	del outf

if __name__ == "__main__":
        print "Running"
        MakeModels(outfile, infile, ThePerturber)

