###################################################################################
##  This is an example of a perturber. It perturbs the plus modes of the         ##
##   logarithmic depth dependent abs+scat FFTs.                                  ##
##                                                                               ##
## It has two key methods:                                                       ##
##                                                                               ## 
##     __init__ to set up the model when the object is                           ##
##     __call__ which maps integers to perturbed ice models.                     ##
##             the return value is an M frame incuding ice model and             ##
##             ice metadata.                                                     ##
##                                                                               ##
## Any class with these two functions that returns a frame (not even necessarily ##
##  an  M-frame) can be used as a Perturber for the Multisim technique           ##
##   as a Perturber for the MultiSim technique.                                  ##
##                                                                               ##
##  Questions? ben.jones@uta.edu or timothy.watson@mavs.uta.edu                  ##
###################################################################################

import numpy as np
from os.path import expandvars
import copy
import subprocess
import argparse
import os, sys

from icecube import icetray, dataclasses, dataio
from icecube import clsim


from FourierToolset import *



# Hard coded size of variants

Rel_Amp_Sigmas = np.asarray([0.00500100, 0.03900780, 0.04500900, 0.17903581, 0.07101420, 0.30306061, 0.14502901, 0.09501900, 0.16103221, 0.13302661, 0.15703141, 0.13302661])
Rel_Phs_Sigmas = np.asarray([0.00000001, 0.01664937, 0.02708014, 0.43171273, 0.02351273, 2.33565571, 0.16767628, 0.05414841, 0.31355088, 0.04227052, 0.27955606, 4.02237848])
Modes_to_Shift = [0,1,2,3,4,5,6,7,8,9,10,11]

#Warning: The perturbations used in MEOWS are Abs_Phs_Sigmas - convert to above by multiplying phase spectrum

class PlusModePerturber:
      ### ---------------------------------------------------------------### 
      ###  Set up the perturber,    taking as an input an ice model path ### 
      ### ---------------------------------------------------------------### 
      def __init__(self, IceModelDir):

            self.depths, Sca_dat, Abs_dat, temp = np.loadtxt(IceModelDir+'/icemodel.dat',unpack=True)
            self.m, self.iceParams = clsim.MakeIceCubeMediumProperties(
                iceDataDirectory=expandvars(IceModelDir),
                returnParameters=True)

            self.Sca=[]
            self.Abs=[]

            for i in range(0, len(self.depths)):
                 # CLSim defines the ScatteringLength as the scattering_coeff/(1-cos(dir)), where cos(dir) ==0.9  
                 self.Sca.append(self.m.GetScatteringLength(i).b400) # CLSim changes the effective scattering coefficient to the scattering coefficient by dividing by 10. 
                                                                                                                                                                              
                 # Note: This is just the absorption due to dust. There is another term in PPC that is for the absorption of ice.
                 # We'll just use the absorption of dust as an approximation. totalAbs = aDust + aIce 
                 self.Abs.append(self.m.GetAbsorptionLength(i).aDust400)

            self.Sca    = np.array(self.Sca)
            self.Abs    = np.array(self.Abs)

            # For some reason, the Abs of the deepest layer is set to 999. This messes with our Fourier Transform. 
            # Let's Decapatate our Abs and Sca and then stitch them back together in a second
            self.Sca_Head = self.Sca[0]
            self.Abs_Head = self.Abs[0]

            self.Abs = np.delete(self.Abs, 0)
            self.Sca = np.delete(self.Sca, 0)
            
            # Calculate Central Models via log perscription
            self.Central_Plus  = 0.5 * np.log10(self.Abs*self.Sca)
            self.Central_Minus = 0.5 * np.log10(self.Abs/self.Sca)

            # Get Central Fourier Series
            self.Central_FS_Plus  = FourierSeries(self.depths[1:], self.Central_Plus)

  
      ### ---------------------------------------------------------------### 
      ###  This method accepts a model number and returns a new M frame  ### 
      ### ---------------------------------------------------------------### 
      def __call__(self,IceXModelNumber):

            # Calculate the Pertubed Series as the perturbed phase model of the pertubed amplitude model (These operations commute, of course)
            np.random.RandomState(int(IceXModelNumber))

            if IceXModelNumber is 0:
                Rand_Amp_Shifts = np.zeros(len(Modes_to_Shift))
                Rand_Phs_Shifts = np.zeros(len(Modes_to_Shift))
            else:
                Rand_Amp_Shifts = np.random.normal(0, Rel_Amp_Sigmas, len(Modes_to_Shift))
                Rand_Phs_Shifts = np.random.normal(0, Rel_Phs_Sigmas, len(Modes_to_Shift))

            Perturbed_FS_Plus  =   PerturbPhases(PerturbAmplitudes(self.Central_FS_Plus, Modes_to_Shift, Rand_Amp_Shifts), Modes_to_Shift, Rand_Phs_Shifts)

            Perturbed_Sca = 10**(Perturbed_FS_Plus[1] - self.Central_Minus)
            Perturbed_Abs = 10**(Perturbed_FS_Plus[1] + self.Central_Minus)
            #Stitch Heads Back on                                                                                                                                            
            Perturbed_Sca[-1] = self.Sca[-1]
            Perturbed_Abs[-1] = self.Abs[-1]
            Perturbed_Sca = np.insert(Perturbed_Sca, 0, self.Sca_Head )
            Perturbed_Abs = np.insert(Perturbed_Abs, 0, self.Abs_Head )

            # Make a new ice model object                                                                                                                                     
            new_m = copy.deepcopy(self.m)
            for i in range(0,len(self.depths)):
                oldScat = new_m.GetScatteringLength(i)
                oldAbs  = new_m.GetAbsorptionLength(i)

                newScat = clsim.I3CLSimFunctionScatLenIceCube(
                    alpha = oldScat.alpha,
                    b400  = float(Perturbed_Sca[i])
                )

                newAbs = clsim.I3CLSimFunctionAbsLenIceCube(
                    kappa    = oldAbs.kappa,
                    A        = oldAbs.A,
                    B        = oldAbs.B,
                    D        = oldAbs.D,
                    E        = oldAbs.E,
                    aDust400    = float(Perturbed_Abs[i]),
                    deltaTau = oldAbs.deltaTau
                )

                new_m.SetScatteringLength(i, newScat)
                new_m.SetAbsorptionLength(i, newAbs)

            # Store ice model in the frame 
            frame = icetray.I3Frame('M')
            frame.Put("MediumProperties"        ,new_m)

            # Store ice metadata in the frame
            IceModelDict = {}
            IceModelDict['MultisimAmplitudes'] = []
            IceModelDict['MultisimPhases'] = []
            IceModelDict['MultisimModes'] = []

            for i in range(len(Modes_to_Shift)):
                IceModelDict['MultisimAmplitudes'].append(Rand_Amp_Shifts[i])
                IceModelDict['MultisimPhases'].append(Rand_Phs_Shifts[i])
                IceModelDict['MultisimModes'].append(Modes_to_Shift[i])

            frame.Put('MultisimAmplitudes'  ,dataclasses.I3VectorDouble(IceModelDict['MultisimAmplitudes']))
            frame.Put('MultisimPhases'      ,dataclasses.I3VectorDouble(IceModelDict['MultisimPhases']))
            frame.Put('MultisimModes'       ,dataclasses.I3VectorDouble(IceModelDict['MultisimModes']))
            frame.Put('IceXModelNumber'     ,dataclasses.I3String(str(IceXModelNumber)))

            return frame
