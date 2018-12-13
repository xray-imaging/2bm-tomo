import time
import epics
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *


global variableDict

variableDict = {
        'ExposureTime': 0.040,
        'SlewSpeed': 1.0,           # to use this as default value comment the calc_blur_pixel(global_PVs, variableDict) function below
        'AcclRot': 1.0,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 750,
        'SampleXIn': -0.416,        # to use X change the sampleInOutVertical = False in PCO_lib.py
        'SampleXOut': 0.7,
        'FurnaceYIn': 0.0,          # to use X change the sampleInOutVertical = False in PCO_lib.py
        'FurnaceYOut': 49.0,
        'WaitBeforeStart': 50,      # wait time (s) before starting data collection; usefull to stabilize 
                                    # sample environment 
#        'SampleYIn': 0,            # default white field is taken moving the Y axis
#        'SampleYOut': -3,
        'roiSizeX': 1280, 
        'roiSizeY': 2160,       
        'NumWhiteImages': 20,
        'NumDarkImages': 20,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': 'PCOIOC3:', # options: 1. DIMAX: 'PCOIOC2:', 2. EDGE: 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.04,
        'EnergyPink': 2.657, 
        'EnergyMono': 24.9,
        'Station': '2-BM-A',
        'StartSleep_min': 0,
        #'camScanSpeed': 'Normal', # options: 'Normal', 'Fast', 'Fastest'
        #'camShutterMode': 'Rolling' # options: 'Rolling', 'Global'
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
            print ('*** The %s is on' % (model))
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' with its optinal value 
            blur_pixel, rot_speed, scan_time = calc_blur_pixel(global_PVs, variableDict)
            variableDict['SlewSpeed'] = rot_speed

            edgeInit(global_PVs, variableDict)     
            edgeTest(global_PVs, variableDict)
            setPSO(global_PVs, variableDict)

            # get sample file name
            fname = global_PVs['HDF1_FileName'].get(as_string=True)
            print('  *** File name prefix: %s' % fname)
            edgeSet(global_PVs, variableDict, fname)

            open_shutters(global_PVs, variableDict)
            edgeAcquisition(global_PVs, variableDict)
            edgeAcquireFlat(global_PVs, variableDict) 
            close_shutters(global_PVs, variableDict)
            edgeAcquireDark(global_PVs, variableDict) 

            print(' ')
            print('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
            print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            print('  *** Done!')

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass

   
    
    
if __name__ == '__main__':
    main()


