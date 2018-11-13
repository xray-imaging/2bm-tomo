import time
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *

global variableDict

variableDict = {
        'ExposureTime': 0.0002,
        'SlewSpeed': 180.0,
        'AcclRot': 80.0,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 1500,
        'SampleXIn': 0.0,
        'SampleXOut': 5,
        'roiSizeX': 2016, 
        'roiSizeY': 600,        
        'PostWhiteImages': 20,
        'PostDarkImages': 20,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': 'PCOIOC2:', # options: 1. DIMAX: 'PCOIOC2:', 2. EDGE: 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05,
        'EnergyPink': 2.657, # for now giver in mirror angle in rads
        'EnergyMono': 24.9,
        'Station': '2-BM-A',
        'StartSleep_min': 0,#        'camScanSpeed': 'Normal', # options: 'Normal', 'Fast', 'Fastest'
#        'camShutterMode': 'Rolling'# options: 'Rolling', 'Global''
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
            start = 0
            end = 1
            step = 0.1
            
            dimaxInit(global_PVs, variableDict)     

            dimaxTest(global_PVs, variableDict)
            
            print(np.arange(start, end, step))
            for i in np.arange(start, end, step):
                print ('*** The sample vertical position is at %s mm' % (i))
                global_PVs['Motor_SampleY'].put(i, wait=True)
                time.sleep(1)

                fname = global_PVs['HDF1_FileName'].get(as_string=True)
                print(' ')
                print('  *** File name prefix: %s' % fname)
                print('start: %s' % str((time.time() - tic)))


                dimaxSet(global_PVs, variableDict, fname)
                print('set camera: %s' % str((time.time() - tic)))

                setPSO(global_PVs, variableDict)
                print('set fly scan: %s' % str((time.time() - tic)))

                open_shutters(global_PVs, variableDict)
                print('open shutter: %s' % str((time.time() - tic)))
                
                dimaxAcquisition(global_PVs, variableDict)
                print('acquisition: %s' % str((time.time() - tic)))
                            
                time.sleep(1)                

                dimaxAcquireFlat(global_PVs, variableDict)
                print('flat: %s' % str((time.time() - tic)))
                
                close_shutters(global_PVs, variableDict)
                print('close: %s' % str((time.time() - tic)))
                
                dimaxAcquireDark(global_PVs, variableDict)
                print('dark: %s' % str((time.time() - tic)))
                
                print(' ')
                print('  *** Total scan time: %s minutes' % str((time.time() - tic)))
                print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
                print('  *** Done!')

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass

     
if __name__ == '__main__':
    main()











