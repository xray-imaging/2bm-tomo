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
        'SampleXIn': 0.0,
        'SampleXOut': 10,
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
            loop_start = 0 
            loop_end = 7
            loop_step = 1
            
            dimaxInit(global_PVs, variableDict)     

            dimaxTest(global_PVs, variableDict)

            fname_prefix = global_PVs['HDF1_FileName'].get(as_string=True)
            
            print(np.arange(loop_start, loop_end, loop_step))
            open_shutters(global_PVs, variableDict)
            
            findex_loop = 0
            for i in np.arange(loop_start, loop_end, loop_step):
                tic_scan =  time.time()

                global_PVs['HDF1_FileNumber'].put(0, wait=True)

                print(' ')
                print ('  *** Scan number %s' % (i))
                #global_PVs['Motor_SampleY'].put(i, wait=True)
                time.sleep(1)

                fname = fname_prefix + '_' + str(findex_loop)
                findex_loop = findex_loop + 1
                
                print(' ')
                print('  *** File name prefix: %s' % fname)

                dimaxSet(global_PVs, variableDict, fname)

                setPSO(global_PVs, variableDict)
                
                dimaxAcquisition(global_PVs, variableDict)
                            
                #time.sleep(1)                

                #dimaxAcquireFlat(global_PVs, variableDict)
                
                #close_shutters(global_PVs, variableDict)
                
                #dimaxAcquireDark(global_PVs, variableDict)
                
                print(' ')
                print('  *** Total scan time: %s s' % str((time.time() - tic_scan)))
                print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
                print('  *** Done!')
            
            dimaxAcquireFlat(global_PVs, variableDict)                
            close_shutters(global_PVs, variableDict)               
            dimaxAcquireDark(global_PVs, variableDict)

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass

     
if __name__ == '__main__':
    main()











