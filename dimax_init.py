import time
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *

global variableDict

variableDict = {
        'ExposureTime': 0.0005,
        'SlewSpeed': 180.0,
        'AcclRot': 180.0,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 1500,
        'SampleInOutVertical': False,     # False: use X to take the white field
        'SampleXIn': 0,                   # to use X change the sampleInOutVertical = False
        'SampleXOut': -2,
        'SampleYIn': 0,                   # to use Y change the sampleInOutVertical = True
        'SampleYOut': -4,
        'roiSizeX': 2016, 
        'roiSizeY': 900,        
        'NumWhiteImages': 20,
        'NumDarkImages': 20,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': 'PCOIOC2:',         # options: 1. DIMAX: 'PCOIOC2:', 2. EDGE: 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05,
        'EnergyPink': 2.657,              # for now giver in mirror angle in rads
        'EnergyMono': 24.9,
        'Station': '2-BM-A',
        'StartSleep_s': 0,                # wait time (s) before starting data collection; usefull to stabilize sample environment 
        'SampleMoveEnabled': False,       # False to freeze sample motion during white field data collection
        'UseFurnace': False,              # True: moves the furnace  to FurnaceYOut position to take white field: 
                                          #       Note: this flag is active ONLY when SampleInOutVertical = False 
        'FurnaceYIn': 0.0,          
        'FurnaceYOut': 49.0,
        }

global_PVs = {}


def main():

    tic =  time.time()
    update_variable_dict(variableDict)
    init_general_PVs(global_PVs, variableDict)
    
    try: 
        model = global_PVs['Cam1_Model'].get()
        if model == None:
            print('*** The PCO Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            print('  *** Failed!')
        else:
            print ('*** The %s is on' % (model))            # get sample file name
            dimaxInit(global_PVs, variableDict)     

            dimaxTest(global_PVs, variableDict)

            print('  *** Done!')

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass

     
if __name__ == '__main__':
    main()











