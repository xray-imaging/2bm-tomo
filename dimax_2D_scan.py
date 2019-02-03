import time
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *

global variableDict

variableDict = {
        'ExposureTime': 0.01,             # to use this as default value comment the variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get() line
        'roiSizeX': 2016,                 # to use this as default value comment the variableDict['roiSizeX'] = global_PVs['Cam1_SizeX_RBV'].get() line
        'roiSizeY': 2016,                 # to use this as default value comment the variableDict['roiSizeY'] = global_PVs['Cam1_SizeY_RBV'].get() line
        'Projections': 12000,
        'SampleMoveEnabled': True,        # False to freeze sample motion during white field data collection
        'SampleInOutVertical': False,     # False: use X to take the white field
        'SampleXIn': 0,                   # to use X change the sampleInOutVertical = False
        'SampleXOut': 0,
        'SampleYIn': 0,                   # to use Y change the sampleInOutVertical = True
        'SampleYOut': -4,
        'NumWhiteImages': 20,
        'NumDarkImages': 25,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': 'PCOIOC2:',         # options: 1. DIMAX: 'PCOIOC2:', 2. EDGE: 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.0001,
        'EnergyPink': 2.657, 
        'EnergyMono': 24.9,
        'Station': '2-BM-A',
        'SlewSpeed': 37.5,               # to use this as default value comment the calc_blur_pixel(global_PVs, variableDict) function below
        'AcclRot': 90.0,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'StartSleep_s': 0,                # wait time (s) before starting data collection; usefull to stabilize sample environment 
        'UseFurnace': False,              # True: moves the furnace  to FurnaceYOut position to take white field: 
                                          #       Note: this flag is active ONLY when both 1. and 2. are met:
                                          #           1. SampleMoveEnabled = True
                                          #           2. SampleInOutVertical = False  
        'FurnaceYIn': 0.0,                
        'FurnaceYOut': 48.0,
         }

global_PVs = {}

def getVariableDict():
    global variableDict
    return variableDict

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


            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get()

            # calling global_PVs['roiSizeX/Y'] to replace the default 'roiSizeX/Y' with the one set in the camera
            variableDict['roiSizeX'] = global_PVs['Cam1_SizeX_RBV'].get()
            variableDict['roiSizeY'] = global_PVs['Cam1_SizeY_RBV'].get()

            dimaxInit(global_PVs, variableDict)            
            dimaxTest(global_PVs, variableDict)
            
            fname = global_PVs['HDF1_FileName'].get(as_string=True)
            print(' ')
            print('  *** File name prefix: %s' % fname)
            
            dimaxSet2D(global_PVs, variableDict, fname)

            dimaxAcquisition2D(global_PVs, variableDict)

            proj_time = variableDict['ExposureTime'] * variableDict['Projections']
            print('  *** Total projection time: %s s' % str(proj_time))            
            print('  *** Total memory dump time: %s s' % str((time.time() - tic) - proj_time))
            time.sleep(2)

            dimaxAcquireFlat2D(global_PVs, variableDict)  

            close_shutters(global_PVs, variableDict)
            dimaxAcquireDark2D(global_PVs, variableDict)

            print(' ')
            print('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
            print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            print('  *** Done!')

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass

     
if __name__ == '__main__':
    main()











