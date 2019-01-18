#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v3.0.1/icetray-start
#METAPROJECT /data/user/bjones/MultiSimUpdate/build

#==============================#
# Spencer N. Axani             #
# Questions? saxani@mit.edu    #
#==============================#

import os
import sys,getopt,string
from os.path import expandvars
from optparse import OptionParser
import logging
import subprocess
import time

print("Importing IceTray Modules")
from icecube.simprod  import ipmodule
from icecube.simprod.util import CombineHits, DrivingTime, choose_max_efficiency
from icecube.simprod.util.fileutils import download,untar,isurl
from icecube import icetray, dataclasses, dataio, phys_services, interfaces
from I3Tray import I3Tray,I3Units
from icecube.simprod.modules import ClSim
from icecube.simprod import segments
from icecube import clsim

start_time = time.time()

usage = "usage: %prog [options] inputfile" 
parser = OptionParser(usage)

parser.add_option(      "--osg",               type="string", default="False")
parser.add_option("-g", "--gcdfile",           type="string", default="/home/twatson/simulation.multisim/testing/GCD/GeoCalibDetectorStatus_AVG_Fit_55697-57531_SPE_PASS2_Raw.i3.gz")
parser.add_option("-i", "--infile",            type="string", default="/home/twatson/simulation.multisim/testing/input/test_muons.i3.zst") 
parser.add_option("-o", "--outfile",           type="string", default="/home/twatson/simulation.multisim/testing/output/test_photons.i3.zst")
parser.add_option("-s", "--seed",              type="string", default="1")
parser.add_option(      "--usegpus",           type="string", default="True")
parser.add_option(      "--maxparallelevents", type="int",    default="5")
parser.add_option("-e", "--generated_domeff",  type="float",  default="1.7")
parser.add_option(      "--ice_model",         type="string", default="spice_3.2", help='spice_3.2, spice_mie')
parser.add_option("-m", "--move",      	       type="string", default="True")
parser.add_option("-n", "--nFrames",           type="int",    default="10",   dest="nFrames", help="The number of Frames to process")    


(options,args) = parser.parse_args() 

gcdfile 	  = options.gcdfile
infile 		  = options.infile
outfile 	  = options.outfile
osg	 	  = options.osg
move 	 	  = options.osg
generated_domeff  = float(options.generated_domeff)
seed 		  = options.seed
maxparallelevents = options.maxparallelevents

if options.usegpus == "True":
	usegpus = True
	usecpus = False
else:
	usegpus = False
	usecpus = True

if options.ice_model not in ['spice_3.2','spice_mie','spice_lea']:
	print('Invalid Icemodel: '+options.ice_model)
	sys.exit()
	
icemodellocation = expandvars("$I3_BUILD/ice-models/resources/models/")
if not icemodellocation.endswith('/'):
    icemodellocation = icemodellocation + '/' 
ice_model = options.ice_model

print('GCD file: '+gcdfile)
print('Infile: '+infile)
print('Outfile: '+outfile)
print('DOM eff: ' + str(generated_domeff)) 
print('IceModel: '+ icemodellocation + ice_model)
print('Using GPUs: '+str(usegpus))

if osg == 'True':
	def copy_to_OSG(NPX_file):
		subprocess.check_call(['globus-url-copy','-nodcau','-rst', NPX_file,"file:"+os.getcwd()+'/'+str(NPX_file.split('/')[-1])])
	def copy_to_NPX(NPX_file):
		subprocess.check_call(['globus-url-copy','-nodcau','-rst',"file:"+os.getcwd()+'/'+str(NPX_file.split('/')[-1]), NPX_file])

	gcdfile_NPX = str('gsiftp://gridftp.icecube.wisc.edu' + gcdfile)
	gcdfile = str(os.getcwd()+'/'+gcdfile.split('/')[-1])

	infile_NPX = str('gsiftp://gridftp.icecube.wisc.edu' + infile)
	infile = str(os.getcwd()+'/'+infile.split('/')[-1])

	copy_to_OSG(gcdfile_NPX)
	copy_to_OSG(infile_NPX)

	#copy_to_OSG('gsiftp://gridftp.icecube.wisc.edu/data/user/twatson/Ice/build/CLSimModels.i3')                                                                                                 
	#os.rename(str(os.getcwd()) + "/CLSimModels.i3", str(os.getcwd()) + "/MultiSimBuild.RHEL_6_x86_64/CLSimModels.i3")
        print gcdfile
	infiles = [gcdfile,infile]
	outfile  = str('gsiftp://gridftp.icecube.wisc.edu' + outfile)
	outfile_temp = str(os.getcwd()+'/'+outfile.split('/')[-1])
else:
	infiles = [gcdfile, infile]
	outfile_temp = '/data/ana/SterileNeutrino/IC86/HighEnergy/MC/scripts/temp/'+outfile.split('/')[-1]


tray = I3Tray()
icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)
print('Making RNGs.')
randomServicePhotons = phys_services.I3GSLRandomService(seed = int(seed))#SPENCER -- I set the seed back to what it was to keep it consistent with old MC.
randomServicePropagators = phys_services.I3GSLRandomService(seed = int(seed))

tray.AddModule("I3Reader", "reader",filenamelist=infiles)
tray.AddModule("Rename",keys=["I3MCTree","I3MCTree_preMuonProp"])
tray.AddSegment(segments.PropagateMuons, "PropagateMuons",
	RandomService = randomServicePropagators)

tray.context['I3RandomService'] = randomServicePhotons
print('Making Photons.')
tray.AddSegment(clsim.I3CLSimMakePhotons, "MakingPhotons",
		UseCPUs								= usecpus,
		UseGPUs								= usegpus,
		UseOnlyDeviceNumber					= None,
		MCTreeName							= "I3MCTree",
		OutputMCTreeName					= None,
		FlasherInfoVectName					= None,
		FlasherPulseSeriesName				= None,
		MMCTrackListName					= "MMCTrackList",
		PhotonSeriesName					= "PhotonSeriesMap",
		ParallelEvents						= maxparallelevents,
		TotalEnergyToProcess				= 0,
		RandomService						= "I3RandomService",
		IceModelLocation					= icemodellocation + ice_model,
		DisableTilt							= False,
		UnWeightedPhotons					= False,
		UnWeightedPhotonsScalingFactor		= None,
		UseGeant4							= False,
		CrossoverEnergyEM					= None,
		CrossoverEnergyHadron				= None,
		UseCascadeExtension					= False,
		StopDetectedPhotons					= True,
		PhotonHistoryEntries				= 0,
		DoNotParallelize					= False,
		DOMOversizeFactor					= 1.0,
		UnshadowedFraction					= float(generated_domeff),
		HoleIceParameterization 			= expandvars('$I3_BUILD/ice-models/resources/models/angsens/as.nominal'),
		WavelengthAcceptance				= None,
		DOMRadius							= 0.16510*icetray.I3Units.m, # 13" diameter
		OverrideApproximateNumberOfWorkItems= None,
		IgnoreSubdetectors                  = ['IceTop'],
		ExtraArgumentsToI3CLSimModule		= dict(),
		If=lambda f: True )

i3streams = [icetray.I3Frame.DAQ, icetray.I3Frame.Physics, icetray.I3Frame.Stream('S'), icetray.I3Frame.Stream('M')]
#i3streams = [icetray.I3Frame.DAQ, icetray.I3Frame.Physics, icetray.I3Frame.Stream('S')]
if move == "True":
	tray.AddModule("I3Writer","i3writer")(
		("Filename",outfile_temp),
		("Streams",i3streams)
		)
else:
	tray.AddModule("I3Writer","i3writer")(
		("Filename",outfile),
		("Streams",i3streams)
		)


if(options.nFrames==0):
    tray.Execute()
else:
    tray.Execute(int(options.nFrames))
tray.Finish()


if move == 'True':
	if osg == "True":
		copy_to_NPX(outfile)
	else:
		os.system(str("mv "+str(outfile_temp) + " " +str(outfile)))
else:
	if osg =="True":
		print('You need options. Move to be True if using the OSG')
		pass

print("Time: " + str(time.time() - start_time))
del tray

