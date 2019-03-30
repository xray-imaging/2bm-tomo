'''
    FlyScan for Sector 2-BM

'''
from __future__ import print_function

import sys
import json
import time
from epics import PV
import h5py
import shutil
import os
import imp
import traceback

from pg_lib import *

global variableDict

variableDict = {
        'StartY': 0,
        'EndY': 100,
        'StepSize': 1,
        'StartSleep_s': 180,              # wait time (s) between each data collection
        'SampleXIn': 0.0,
        'SampleXOut': -11,
        # 'SampleYIn': 0,                 # to use Y change the sampleInOutVertical = True
        # 'SampleYOut': -4,
        'SampleInOutVertical': False,     # False: use X to take the white field
        'SampleMoveEnabled': True,        # False to freeze sample motion during white field data collection
        'SampleRotStart': 0.0,
        'SampleRotEnd':180.0,
        'Projections': 2000,
        'NumWhiteImages': 30,
        'NumDarkImages': 20,
        # ####################### DO NOT MODIFY THE PARAMETERS BELOW ###################################
        'CCD_Readout': 0.006,             # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
        # 'CCD_Readout': 0.01,             # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
        'Station': '2-BM-A',
        'ExposureTime': 0.01,             # to use this as default value comment the variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get() line
        # 'roiSizeX': 2448, 
        # 'roiSizeY': 2048,       
        'SlewSpeed': 5.0,                 # to use this as default value comment the calc_blur_pixel(global_PVs, variableDict) function below
        'AcclRot': 1.0,
        'IOC_Prefix': '2bmbSP1:',         # options: 1. PointGrey: '2bmbPG3:', 2. Gbe '2bmbSP1:' 
        'FileWriteMode': 'Stream',
        'ShutterOpenDelay': 0.00,
        'Recursive_Filter_Enabled': False,
        'Recursive_Filter_N_Images': 4,
        'UseFurnace': False,              # True: moves the furnace  to FurnaceYOut position to take white field: 
                                          #       Note: this flag is active ONLY when both 1. and 2. are met:
                                          #           1. SampleMoveEnabled = True
                                          #           2. SampleInOutVertical = False  
        'FurnaceYIn': 0.0,                
        'FurnaceYOut': 48.0
        }

global_PVs = {}


def getVariableDict():
    global variableDict
    return variableDict


def start_scan(variableDict, fname):
    print(' ')
    print('  *** start_scan')

    def cleanup(signal, frame):
        stop_scan(global_PVs, variableDict)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    if variableDict.has_key('StopTheScan'):
        stop_scan(global_PVs, variableDict)
        return

    pgInit(global_PVs, variableDict)
    setPSO(global_PVs, variableDict)

    # fname = global_PVs['HDF1_FileName'].get(as_string=True)
    print('  *** File name prefix: %s' % fname)

    pgSet(global_PVs, variableDict, fname) 

    open_shutters(global_PVs, variableDict)

    # # run fly scan
    theta = pgAcquisition(global_PVs, variableDict)
    # print(theta)
    pgAcquireFlat(global_PVs, variableDict)
    close_shutters(global_PVs, variableDict)
    time.sleep(2)

    pgAcquireDark(global_PVs, variableDict)

    checkclose_hdf(global_PVs, variableDict)

    add_theta(global_PVs, variableDict, theta)



def main():
    tic =  time.time()
    update_variable_dict(variableDict)
    init_general_PVs(global_PVs, variableDict)
    
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if detector_sn == None:
            print('*** The Point Grey Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            print('  *** Failed!')
        else:
            print ('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (variableDict['IOC_Prefix'], detector_sn))
            
            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get()
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = calc_blur_pixel(global_PVs, variableDict)
            variableDict['SlewSpeed'] = rot_speed

            # get sample file name
            # fname = global_PVs['HDF1_FileName'].get(as_string=True)

            start = variableDict['StartY']
            end = variableDict['EndY']
            step_size = variableDict['StepSize']

            print("Sleep Scan: ", np.arange(start, end, step_size))
            for i in np.arange(start, end, step_size):
                fname = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + "".join([chr(c) for c in global_PVs['Sample_Name'].get()]) 
                print('  *** Moving rotary stage to start position')
                global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
                print('  *** Moving rotary stage to start position: Done!')

                start_scan(variableDict, fname)

                if ((i+1)!=end):
                    print('          *** Wait (s): %s ' % str(variableDict['StartSleep_s']))
                    time.sleep(variableDict['StartSleep_s']) 

                print(' ')
                print('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
                print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            global_PVs['Cam1_ImageMode'].put('Continuous')
            print('  *** Done!')

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass
        
        

if __name__ == '__main__':
    main()
