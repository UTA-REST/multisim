import tables
import numpy as np
import scipy as sp
import matplotlib as mpl
import random
import itertools

from scipy.stats import norm as nm

import matplotlib.mlab as mlab
import copy
import os
import sys
import argparse

pi = np.pi

print("\n")


    
############ SET BINNING 


e_bins=10**(np.arange(np.log10(500),np.log10(10000),0.1))
z_bins=np.arange(-1,0.25,0.05)


########### Load Spencer's import_MC class here 
class import_MC(object):
    def __init__(self, infiles, MC, desired_keys='',MSAmps=False, MSPhases=False):
        self.infiles    = infiles
        self.MC         = MC
        self.desired_keys = desired_keys
        self.allocate_variables(infiles,desired_keys,MSAmps,MSPhases)
    def allocate_variables(self, infiles, desired_keys,MSAmps,MSPhases):
        variable_dict = {}
        f = tables.openFile(infiles[0])
        for i,j in f.root.keysDict.coldescrs.iteritems():
            if desired_keys:
                    if i in desired_keys:
                        variable_dict[i] = []
            else:
                variable_dict[i] = []
        MultisimAmplitudesArray = []
        MultisimPhasesArray = []
        for infile in infiles:
            scale_factor = float(infile.split('_')[-1].split('.h5')[0])/5000.
            f = tables.openFile(infile) 

            for i,j in f.root.keysDict.coldescrs.iteritems():
                print i
                if desired_keys:
                    if i == 'weights':
                        variable_dict['weights'] += np.ndarray.tolist(f.root.keysDict[:]['weights']/scale_factor)
                    elif i in desired_keys:
                        variable_dict[i] += np.ndarray.tolist(f.root.keysDict[:][i])
                else:
                    if i == 'weights':
                        variable_dict['weights'] += np.ndarray.tolist(f.root.keysDict[:]['weights']/scale_factor)
                    else:
                        variable_dict[i] += np.ndarray.tolist(f.root.keysDict[:][i])
            for i,j in f.root.keysDict.coldescrs.iteritems():
                if desired_keys:
                    print "loading table " + str(i)
                    if i == 'weights':
                        if self.MC == False:
                            print('Uploading Data')
                            setattr(self, 'weights', np.ones(len(variable_dict['weights'])))
                        else:
                            setattr(self, 'weights', np.asarray(variable_dict['weights']))
                    elif i in desired_keys:
                        setattr(self, i, np.asarray(variable_dict[i]))
                else:
                    if i == 'weights':
                        setattr(self, 'weights', np.asarray(variable_dict['weights']))
                    else:
                        setattr(self, i, np.asarray(variable_dict[i]))

            if MSAmps:
                print "Loading MSAmps"
                MultisimAmplitudesArray.extend(f.root.MultisimAmplitudes.cols.item[:])

            if MSPhases:
                print "Loading MSPhases"
                MultisimPhasesArray.extend(f.root.MultisimPhases.cols.item[:])

        self.rate = sum(self.weights)

        if(MSAmps):
            len_of_array = int(len(MultisimAmplitudesArray)/len(self.weights))
            self.MultisimAmplitudes =  np.asarray([MultisimAmplitudesArray[x:x+len_of_array] for x in xrange(0, len(MultisimAmplitudesArray),len_of_array)]) 

        if(MSPhases):                     
            len_of_array = int(len(MultisimPhasesArray)/len(self.weights))
            self.MultisimPhases =  np.asarray([MultisimPhasesArray[x:x+len_of_array] for x in xrange(0, len(MultisimPhasesArray),len_of_array)])
            
        print('Rate: '+ str(sum(self.weights))+' mHz +/- '+ str(np.sqrt(sum(np.power(self.weights,2))))+' mHz')


################################################################################################################################################

####### Parse Arguments here

parser = argparse.ArgumentParser(prog='PROG')

parser.add_argument('-i','--infiles', dest='infiles', nargs = '+', help='List of MultiSim Monte Carlo Sets to Process.')
parser.add_argument('-o','--outpath', dest='outpath', default = os.getcwd(), help='Name of the Output File.')
parser.add_argument('-n', '--max_events', dest='nevents', default=-1, help='Maximum Number of MC Events to Use.')
parser.add_argument('-m','--modes', dest='splitmodes', nargs = '+', default=[], help='List of Modes to Calculate.')
parser.add_argument('-s', '--splitpoint', dest='splitpoint', default=0,  help='Point In Nuisance Space to Split')

parser.add_argument('-p', '--phases',     dest='SplitPhases',     action='store_true',  help='Split Along Phases.')
parser.add_argument('-a', '--amplitudes', dest='SplitAmplitudes', action='store_true',  help='Split Along Amplitudes.')



args = parser.parse_args()

######### Load Arguments


SplitPhases        = args.SplitPhases
SplitAmplitudes    = args.SplitAmplitudes


splitmodes = [int(i) for i in args.splitmodes]
nevents         =  int(args.nevents)
splitpoint      =   float(args.splitpoint)

infiles         =      args.infiles
outpath         =      args.outpath
indirs          =      []

####### Raise "Friendly" Exceptions Here
if (not (args.infiles)):
    raise RuntimeError("You must specify at leats one input file \n")
if SplitPhases and SplitAmplitudes:
    raise RuntimeError("You cannot split phases and amplitudes simultaneously \n")
if not (SplitPhases or SplitAmplitudes):
    raise RuntimeError("You must specify parameter to split \n")
if len(splitmodes) == 0: 
    print("No Modes to Split Specified... Splitting all Available Modes \n")

######### Configure Input and Output Paths

for i in range(len(infiles)):
    indirs.append(infiles[i][ 0 : infiles[i].rfind('/') ])
    infiles[i] =  infiles[i][ (infiles[i].rfind('/') + 1) : len(infiles[i]) ]

inpaths = []
heads = []
tails = []

######### Slice and Dice Inputs

for i in range(len(infiles)):
    if ".h5" or ".hdf5" in infiles[i]:
        inpaths.append(os.path.join(indirs[i], infiles[i]))
        MC_name = infiles[i].replace('.h5','')
        MC_name = MC_name.replace('.hdf5','')
        heads.append(str( MC_name[ 0 : (MC_name.rfind('_')) ]))
        if '_LE' in indirs[i]:    
            tails.append('LE-' + ( MC_name[ (MC_name.rfind('_') + 1) : len(MC_name) ] ))
        if '_HE' in indirs[i]:    
            tails.append('HE-' + ( MC_name[ (MC_name.rfind('_') + 1) : len(MC_name) ] ))   
        if not ('_LE' in indirs[i]) and not ('_HE' in indirs[i]):
            print("Energy Set Not Specified, Check if MC is complete!")
            tails.append( MC_name[ (MC_name.rfind('_') + 1) : len(MC_name) ] )
    else:
        inpaths.append(os.path.join(indirs[i], infiles[i] + '.h5'))

### Get Heads

for i in range(len(list(set(heads)))):
    if i == 0:
        head = list(set(heads))[0] + '_'
    else:
        head = head  + list(set(heads))[i] + '_'

##### Get Tails

for i in range(len(list(set(tails)))):
    if i == 0 and i != max(range(len(list(set(tails))))):
        tail = list(set(tails))[0] + '_'
    if i == max(range(len(list(set(tails))))) and i != 0:
        tail = tail  + list(set(tails))[i]
    if i != max(range(len(list(set(tails))))) and i != 0:
        tail = tail  + list(set(tails))[i] + '_'
    if i == max(range(len(list(set(tails))))) and i == 0:
        tail = list(set(tails))[i] 
        
#outpath = os.path.join(outpath, head + tail)
    
### Dont overwrite existing directories....

if os.path.exists(outpath):
    print("Writing Output to Existing Directory.")
    print("Output Directory:     " + str(outpath))
else:
    print("Writing Output to new Directory.")
    print("Creating Directory:     " + str(outpath))
    os.mkdir(outpath)

#### Load MC (Takes a while....)

print("Loading Monte Carlo (this will take a while)")

Multisim = True
if SplitAmplitudes:
    my_MC = import_MC(inpaths, MC=True, desired_keys=['MuExEnergy','MuExZenith','weights'],MSAmps=True)
if SplitPhases:
    my_MC = import_MC(inpaths, MC=True, desired_keys=['MuExEnergy','MuExZenith','weights'],MSPhases=True)
########## Configure My Parameters:
############ SET SPLIT PARAMETERS

if nevents is -1:
    nevents = int(len(my_MC.MuExEnergy))
if SplitAmplitudes and len(splitmodes) == 0:
   splitmodes = np.arange(0,len(my_MC.MultisimAmplitudes[0]))
if SplitPhases and len(splitmodes) == 0:
   splitmodes = np.arange(0,len(my_MC.MultisimPhases[0]))



############################################################
######### Begin Loop over Modes ############################
############################################################

gradients = []

for splitmode in splitmodes:
    print("Splitting Mode " + str(splitmode))
    
########### READ DATA FROM (PRELOADED) MONTE CARLO
   
    splitindex    =    splitmode

    if SplitPhases:
            mc_pos_e        =    my_MC.MuExEnergy[ my_MC.MultisimPhases[:,splitindex] > splitpoint][:nevents]
            mc_neg_e        =    my_MC.MuExEnergy[ my_MC.MultisimPhases[:,splitindex] < splitpoint][:nevents]
            weight_pos_e    =    my_MC.weights[    my_MC.MultisimPhases[:,splitindex] > splitpoint][:nevents]
            weight_neg_e    =    my_MC.weights[    my_MC.MultisimPhases[:,splitindex] < splitpoint][:nevents]

            mc_pos_z        =    np.cos(my_MC.MuExZenith[ my_MC.MultisimPhases[:,splitindex] > splitpoint][:nevents])
            mc_neg_z        =    np.cos(my_MC.MuExZenith[ my_MC.MultisimPhases[:,splitindex] < splitpoint][:nevents])
            weight_pos_z    =    my_MC.weights[    my_MC.MultisimPhases[:,splitindex] > splitpoint][:nevents]
            weight_neg_z    =    my_MC.weights[    my_MC.MultisimPhases[:,splitindex] < splitpoint][:nevents]            
    else:
            print "Shapes: 1 ", np.shape(my_MC.MuExEnergy)
            print "Shapes: 2 ", np.shape(my_MC.MultisimAmplitudes)
            mc_pos_e        =    my_MC.MuExEnergy[ my_MC.MultisimAmplitudes[:,splitindex] > splitpoint][:nevents]
            mc_neg_e        =    my_MC.MuExEnergy[ my_MC.MultisimAmplitudes[:,splitindex] < splitpoint][:nevents]
            weight_pos_e    =    my_MC.weights[    my_MC.MultisimAmplitudes[:,splitindex] > splitpoint][:nevents]
            weight_neg_e    =    my_MC.weights[    my_MC.MultisimAmplitudes[:,splitindex] < splitpoint][:nevents]

            mc_pos_z        =    np.cos(my_MC.MuExZenith[ my_MC.MultisimAmplitudes[:,splitindex] > splitpoint][:nevents])
            mc_neg_z        =    np.cos(my_MC.MuExZenith[ my_MC.MultisimAmplitudes[:,splitindex] < splitpoint][:nevents])
            weight_pos_z    =    my_MC.weights[    my_MC.MultisimAmplitudes[:,splitindex] > splitpoint][:nevents]
            weight_neg_z    =    my_MC.weights[    my_MC.MultisimAmplitudes[:,splitindex] < splitpoint][:nevents]     

######## CONFIGURE HISTOGRAM 

    pos_hist_e, bins_e = np.histogram(mc_pos_e, bins=e_bins, weights=weight_pos_e)
    neg_hist_e, bins_e = np.histogram(mc_neg_e, bins=e_bins, weights=weight_neg_e) 
    pos_hist_z, bins_z = np.histogram(mc_pos_z, bins=z_bins, weights=weight_pos_z)
    neg_hist_z, bins_z = np.histogram(mc_neg_z, bins=z_bins, weights=weight_neg_z) 
    
    bin_centers_e = (e_bins[:-1] + e_bins[1:]) / 2
    bin_widths_e  = abs((e_bins[1:] - e_bins[:-1]) / 2)

    bin_centers_z = (z_bins[:-1] + z_bins[1:]) / 2
    bin_widths_z  = abs((z_bins[1:] - z_bins[:-1]) / 2)

######## CALCULATE WEIGHTED UNCERTAINTIES
    
    pos_errors_e = np.zeros(len(bin_centers_e))
    neg_errors_e = np.zeros(len(bin_centers_e))

    pos_errors_z = np.zeros(len(bin_centers_z))
    neg_errors_z = np.zeros(len(bin_centers_z))
    
    for i in range(len(mc_pos_e)):
        for j in range(len(e_bins)-1):
            if mc_pos_e[i] > e_bins[j] and mc_pos_e[i] < e_bins[j+1]:
                pos_errors_e[j] = pos_errors_e[j] + (weight_pos_e[i])**2
    
    for i in range(len(mc_neg_e)):
        for j in range(len(e_bins)-1):
            if mc_neg_e[i] > e_bins[j] and mc_neg_e[i] < e_bins[j+1]:
                neg_errors_e[j] = neg_errors_e[j] + (weight_neg_e[i])**2
    
    pos_errors_e = np.sqrt(pos_errors_e)
    neg_errors_e = np.sqrt(neg_errors_e)

    for i in range(len(mc_pos_z)):
        for j in range(len(z_bins)-1):
            if mc_pos_z[i] > z_bins[j] and mc_pos_z[i] < z_bins[j+1]:
                pos_errors_z[j] = pos_errors_z[j] + (weight_pos_z[i])**2
    
    for i in range(len(mc_neg_z)):
        for j in range(len(z_bins)-1):
            if mc_neg_z[i] > z_bins[j] and mc_neg_z[i] < z_bins[j+1]:
                neg_errors_z[j] = neg_errors_z[j] + (weight_neg_z[i])**2
    
    pos_errors_z = np.sqrt(pos_errors_z)
    neg_errors_z = np.sqrt(neg_errors_z)

########### GET MC DISTRIBUTIONS ##########

    mc_pos_dist_e, bins_e = np.histogram( mc_neg_e, bins=e_bins, weights=weight_neg_e, 
                                                normed=False)
    mc_neg_dist_e, bins_e = np.histogram( mc_pos_e, bins=e_bins, weights=weight_pos_e, 
                                                 normed=False)       

    mc_pos_dist_z, bins_z = np.histogram( mc_neg_z, bins=z_bins, weights=weight_neg_z, 
                                                normed=False)
    mc_neg_dist_z, bins_z = np.histogram( mc_pos_z, bins=z_bins, weights=weight_pos_z, 
                                                 normed=False)       

    ############# CALCULATE GRADIENT ############


    str_a = "SplitCounts_" 
    if SplitPhases:
        str_b = "Phs_"
    else:
        str_b = "Amp_"      
    str_c_e = "Energy_"
    str_c_z = "Zenith_"

    str_d = splitmode

    fname_e = str(str_a ) + str(str_b) + str(str_c_e) + str(str_d) + '.csv'
    fname_z = str(str_a ) + str(str_b) + str(str_c_z) + str(str_d) + '.csv'

    outfile_e = os.path.join(outpath, fname_e) 
    outfile_z = os.path.join(outpath, fname_z) 
    
    if os.path.isfile(outfile_e) or os.path.isfile(outfile_z):
        print('ERROR: THIS GRADIENT FILE EXISTS! \n Aborting.')
        sys.exit()
    if not(os.path.isfile(outfile_e)):
        print('Writing energy gradients to: ' + str(outfile_e)) 
    if not(os.path.isfile(outfile_z)):
        print('Writing zenith gradients to: ' + str(outfile_z)) 



    tosave_e=np.array([bin_centers_e,bin_widths_e, mc_pos_dist_e,pos_errors_e,mc_neg_dist_e,neg_errors_e])
    tosave_z=np.array([bin_centers_z,bin_widths_z, mc_pos_dist_z,pos_errors_z,mc_neg_dist_z,neg_errors_z])
    print "Saving to " +str(outfile_e)
    print tosave_e
    np.savetxt(outfile_e,tosave_e)

    print "Saving to " +str(outfile_z)
    print tosave_z
    np.savetxt(outfile_z,tosave_z)

print("Done! :-) \n")
