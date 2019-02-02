import time
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *

global variableDict

variableDict = {
        'ExposureTime': 0.007,
        'SlewSpeed': 37.5,                # to use this as default value comment the calc_blur_pixel(global_PVs, variableDict) function below
        'AcclRot': 90.0,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 2000,
        'SampleInOutVertical': False,     # False: use X to take the white field
        'SampleXIn': 0,                   # to use X change the sampleInOutVertical = False
        'SampleXOut': -2,
        'SampleYIn': 0,                   # to use Y change the sampleInOutVertical = True
        'SampleYOut': -4,
        'NumWhiteImages': 20,
        'NumDarkImages': 20,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': 'PCOIOC2:',         # options: 1. DIMAX: 'PCOIOC2:', 2. EDGE: 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.0001,
        'EnergyPink': 2.657, 
        'EnergyMono': 24.9,
        'Station': '2-BM-A',
        'StartSleep_s': 0,                # wait time (s) before starting data collection; usefull to stabilize sample environment 
        'SampleMoveEnabled': False,       # False to freeze sample motion during white field data collection
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

            # calling calc_blur_pixel() to replace the default 'SlewSpeed' with its optinal value 
            blur_pixel, rot_speed, scan_time = calc_blur_pixel(global_PVs, variableDict)
            variableDict['SlewSpeed'] = rot_speed

            dimaxInit(global_PVs, variableDict)            
            dimaxTest(global_PVs, variableDict)
            
            fname = global_PVs['HDF1_FileName'].get(as_string=True)
            print(' ')
            print('  *** File name prefix: %s' % fname)
            
            dimaxSet(global_PVs, variableDict, fname)

            setPSO(global_PVs, variableDict)
            
            dimaxAcquisition(global_PVs, variableDict)
            
            print('  *** Total projection time: %s s' % str((time.time() - tic)))
            time.sleep(2)                

            dimaxAcquireFlat(global_PVs, variableDict)  

            close_shutters(global_PVs, variableDict)
            dimaxAcquireDark(global_PVs, variableDict)

            print(' ')
            print('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
            print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            print('  *** Done!')

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass

     
if __name__ == '__main__':
    main()











