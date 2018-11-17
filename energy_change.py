import time
import epics
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *


global variableDict

variableDict = {'PreDarkImages': 0,
        'PreWhiteImages': 0,
        'Projections': 1500,
        'PostDarkImages': 20,
        'PostWhiteImages': 20,
        'SampleXIn': 0.0,
        'SampleXOut': 5,
        'SampleStartPos': 0.0,
        'SampleEndPos': 180.0,
        'StartSleep_min': 0,
        'SlewSpeed': 1.0,
        'ExposureTime': 0.1,
        'ExposureTime_flat': 0.1,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': 'PCOIOC3:', # options: 'PCOIOC2:', 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05,
        'AcclRot': 1.0,
        'EnergyPink': 2.657, # for now giver in mirror angle in rads
        'EnergyMono': 24.9
#        'camScanSpeed': 'Normal', # options: 'Normal', 'Fast', 'Fastest'
#        'camShutterMode': 'Rolling'# options: 'Rolling', 'Global''
        }

global_PVs = {}

    
def main():

    init_general_PVs(global_PVs, variableDict)
    angle_calibrated = change2Pink()
    energy_calibrated = setEnergy()
 
    
if __name__ == '__main__':
    main()
