import time
import epics
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *


global variableDict

variableDict = {
        'ExposureTime': 0.1,
        'SlewSpeed': 1.0, # to use this as default value comment the calc_blur_pixel(global_PVs, variableDict) function below
        'AcclRot': 1.0,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 1500,
        'SampleXIn': 0.0,
        'SampleXOut': 5,
        'roiSizeX': 2560, 
        'roiSizeY': 2160,       
        'PostWhiteImages': 20,
        'PostDarkImages': 20,
        'PreWhiteImages': 0,        
        'PreDarkImages': 0,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': 'PCOIOC3:', # options: 1. DIMAX: 'PCOIOC2:', 2. EDGE: 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05,
        'EnergyPink': 2.657, # for now giver in mirror angle in rads
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

    update_variable_dict(variableDict)
    init_general_PVs(global_PVs, variableDict)

    tic =  time.time()
    update_variable_dict(variableDict)
    init_general_PVs(global_PVs, variableDict)
    
    try: 
        model = global_PVs['Cam1_Model'].get()
        if model == None:
            print('*** The Point Grey Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            print('  *** Failed!')
        else:
            print ('*** The %s is on' % (model))            # get sample file name
            start = 0
            end = 5
            step = 0.01
            
            print(np.arange(start, end, step))
            for i in np.arange(start, end, step):
                
                print ('*** The sample vertical position is at %s mm' % (i))
                global_PVs['Motor_SampleY'].put(i, wait=True)
                time.sleep(.5)
                edgeInit(global_PVs, variableDict)     
                edgeTest(global_PVs, variableDict)
                setPSO(global_PVs, variableDict)

                fname = global_PVs['HDF1_FileName'].get(as_string=True)
                print('  *** File name: %s' % fname)
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
