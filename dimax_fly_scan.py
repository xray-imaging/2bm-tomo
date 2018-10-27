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
        'Projections': 15,
        'PostDarkImages': 2,
        'PostWhiteImages': 2,
        'SampleXIn': 0.0,
        'SampleXOut': 5,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 18.0,
        'StartSleep_min': 0,
        'SlewSpeed': 1.0,
        'ExposureTime': 0.1,
        'ExposureTime_flat': 0.1,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': 'PCOIOC2:', # options: 1. DIMAX: 'PCOIOC2:', 2. EDGE: 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05,
        'AcclRot': 1.0,
        'EnergyPink': 2.657, # for now giver in mirror angle in rads
        'EnergyMono': 24.9,
        'Station': '2-BM-B'
#        'camScanSpeed': 'Normal', # options: 'Normal', 'Fast', 'Fastest'
#        'camShutterMode': 'Rolling'# options: 'Rolling', 'Global''
        }

global_PVs = {}


                
def main():

    update_variable_dict(variableDict)
    init_general_PVs(global_PVs, variableDict)

    dimaxInit(global_PVs, variableDict)
    ##dimaxTest(global_PVs, variableDict)
    ##dimaxSet(global_PVs, variableDict)
    
if __name__ == '__main__':
    main()











