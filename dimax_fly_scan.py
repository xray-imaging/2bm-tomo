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
        'PostDarkImages': 16,
        'PostWhiteImages': 17,
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
        'Station': '2-BM-A'
#        'camScanSpeed': 'Normal', # options: 'Normal', 'Fast', 'Fastest'
#        'camShutterMode': 'Rolling'# options: 'Rolling', 'Global''
        }

global_PVs = {}


def main():

    tic =  time.time()
    update_variable_dict(variableDict)
    init_general_PVs(global_PVs, variableDict)
    
    if(0==0):
    ##try: 
        model = global_PVs['Cam1_Model'].get()
        if model == None:
            print('*** The PCO Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            print('  *** Failed!')
        else:
            print ('*** The %s is on' % (model))            # get sample file name
            dimaxInit(global_PVs, variableDict)     
            dimaxTest(global_PVs, variableDict)

            fname = global_PVs['HDF1_FileName'].get(as_string=True)
            print('  *** File name prefix: %s' % fname)
            
            dimaxSet(global_PVs, variableDict, fname)

            setPSO(global_PVs, variableDict)

            open_shutters(global_PVs, variableDict)
            dimaxAcquisition(global_PVs, variableDict)
            time.sleep(2)                

            dimaxAcquireFlat(global_PVs, variableDict)  
            global_PVs['Cam1_PCODumpCameraMemory'].put(1, wait=True, timeout=1000.0)             
            
            close_shutters(global_PVs, variableDict)
            dimaxAcquireDark(global_PVs, variableDict)
            global_PVs['Cam1_PCODumpCameraMemory'].put(1, wait=True, timeout=1000.0)             

            print(' ')
            print('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
            print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            print('  *** Done!')

    ##except  KeyError:
    ##    print('  *** Some PV assignment failed!')
    ##    pass

     
if __name__ == '__main__':
    main()











