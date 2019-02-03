import time
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *

global variableDict

variableDict = {
        'ExposureTime': 0.0005,             # to use this as default value comment the variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get() line
        'SlewSpeed': 180.0,
        'AcclRot': 180.0,
        'roiSizeX': 2016,                 # to use this as default value comment the variableDict['roiSizeX'] = global_PVs['Cam1_SizeX_RBV'].get() line
        'roiSizeY': 2016,                 # to use this as default value comment the variableDict['roiSizeY'] = global_PVs['Cam1_SizeY_RBV'].get() line
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 1500,
        'SampleMoveEnabled': True,        # False to freeze sample motion during white field data collection
        'SampleInOutVertical': False,     # False: use X to take the white field
        'SampleXIn': 0.0,                 # to use X change the sampleInOutVertical = False
        'SampleXOut': 10,
        'SampleYIn': 0,                   # to use Y change the sampleInOutVertical = True
        'SampleYOut': -4,
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
            loop_start = 0 
            loop_end = 7
            loop_step = 1
            

            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get()

            # calling global_PVs['roiSizeX/Y'] to replace the default 'roiSizeX/Y' with the one set in the camera
            variableDict['roiSizeX'] = global_PVs['Cam1_SizeX_RBV'].get()
            variableDict['roiSizeY'] = global_PVs['Cam1_SizeY_RBV'].get()

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
                
                # for faster scans comment the 3 lines below
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











