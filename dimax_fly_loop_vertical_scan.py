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
        'SampleMoveEnabled': False,       # False to freeze sample motion during white field data collection
        'SampleInOutVertical': False,     # False: use X to take the white field
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 1500,
        'NumWhiteImages': 20,
        'NumDarkImages': 20,
        # ####################### DO NOT MODIFY THE PARAMETERS BELOW ###################################
        'Station': '2-BM-A',
        'ExposureTime': 0.0005,             # to use this as default value comment the variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get() line
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
            loop_start = 0 
            loop_end = 18
            loop_step = 1
            

            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get()

            # calling global_PVs['roiSizeX/Y'] to replace the default 'roiSizeX/Y' with the one set in the camera
            variableDict['roiSizeX'] = global_PVs['Cam1_SizeX_RBV'].get()
            variableDict['roiSizeY'] = global_PVs['Cam1_SizeY_RBV'].get()

            dimaxInit(global_PVs, variableDict)
            dimaxTest(global_PVs, variableDict)

            fname_prefix = global_PVs['HDF1_FileName'].get(as_string=True)
            #open_shutters(global_PVs, variableDict)

            vertical_start = 0 
            vertical_end = 2
            vertical_step = 1.5
            
            findex_loop = 0
            findex_vertical = 0
            
            for i in np.arange(loop_start, loop_end, loop_step):
                print("###############OUTER LOOP#####")
                global_PVs['HDF1_FileNumber'].put(0, wait=True)

                findex_vertical = 0
                print(' ')
                print ('  *** Scan number %s' % (i))
                for j in np.arange(vertical_start, vertical_end, vertical_step):
                    print("         ###############INNER LOOP#####")
                    tic_scan =  time.time()

                    print ('                *** The sample vertical position is at %s mm' % (j))
                    global_PVs['Motor_SampleY'].put(j, wait=True)

                    fname = fname_prefix + '_' + str(findex_loop) + '_' + str(findex_vertical)
                    findex_vertical = findex_vertical + 1

                    print(' ')
                    print('                 *** File name prefix: %s' % fname)

                    dimaxSet(global_PVs, variableDict, fname)
                    global_PVs['HDF1_FileTemplate'].put('%s%s.h5', wait=True, timeout=1000.0) 

                    setPSO(global_PVs, variableDict)
                    dimaxAcquisition(global_PVs, variableDict)

                findex_loop = findex_loop + 1 
                findex_vertical = 0

                
    
            print(' ')
            print('  *** Total scan time: %s s' % str((time.time() - tic_scan)))
            print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            print('  *** Done!')
            
            global_PVs['HDF1_FileTemplate'].put('%s%s_%4.4d.h5', wait=True, timeout=1000.0) 
            dimaxAcquireFlat(global_PVs, variableDict)                
            #close_shutters(global_PVs, variableDict)               
            dimaxAcquireDark(global_PVs, variableDict)

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass

     
if __name__ == '__main__':
    main()











