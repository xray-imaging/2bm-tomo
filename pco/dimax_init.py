import time
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *

global variableDict

variableDict = {
        'SampleXIn': 0,                   # to use X change the sampleInOutVertical = False
        'SampleXOut': -2,
        # 'SampleYIn': 0,                   # to use Y change the sampleInOutVertical = True
        # 'SampleYOut': -4,
        'SampleInOutVertical': False,     # False: use X to take the white field
        'SampleMoveEnabled': False,       # False to freeze sample motion during white field data collection
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 1500,
        'NumWhiteImages': 20,
        'NumDarkImages': 20,
        # ####################### DO NOT MODIFY THE PARAMETERS BELOW ###################################
        'Station': '2-BM-A',
        'ExposureTime': 0.0005,           
        'roiSizeX': 2016,                 # to use this as default value comment the variableDict['roiSizeX'] = global_PVs['Cam1_SizeX_RBV'].get() line
        'roiSizeY': 2016,                 # to use this as default value comment the variableDict['roiSizeY'] = global_PVs['Cam1_SizeY_RBV'].get() line
        'StartSleep_s': 0,                # wait time (s) before starting data collection; usefull to stabilize sample environment 
        'SlewSpeed': 180.0,
        'AcclRot': 180.0,
        'IOC_Prefix': 'PCOIOC2:',         # options: 1. DIMAX: 'PCOIOC2:', 2. EDGE: 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05,
        'ShutterOpenDelay': 0.00,
        'UseFurnace': False,              # True: moves the furnace  to FurnaceYOut position to take white field: 
                                          #       Note: this flag is active ONLY when both 1. and 2. are met:
                                          #           1. SampleMoveEnabled = True
                                          #           2. SampleInOutVertical = False  
        'FurnaceYIn': 0.0,                
        'FurnaceYOut': 48.0,
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











