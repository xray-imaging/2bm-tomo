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
import logging

from pg_lib import *

global variableDict

variableDict = {
        'StartY': 0,
        'EndY': 300,
        'StepSize': 1,
        'StartSleep_s': 0,              # wait time (s) between each data collection
        'SampleXIn': 0.0,
        'SampleXOut': 1,
        # 'SampleYIn': 0,                 # to use Y change the sampleInOutVertical = True
        # 'SampleYOut': -4,
        'SampleInOutVertical': False,     # False: use X to take the white field
        'SampleMoveEnabled': True,        # False to freeze sample motion during white field data collection
        'SampleRotStart': 0.0,
        'SampleRotEnd':180.0,
        'Projections': 1500,
        'NumWhiteImages': 20,
        'NumDarkImages': 20,
        # ####################### DO NOT MODIFY THE PARAMETERS BELOW ###################################
        'CCD_Readout': 0.006,              # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
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

LOG = logging.basicConfig(format = "%(asctime)s %(logger_name)s %(color)s  %(message)s %(endColor)s", level=logging.INFO)


def getVariableDict():
    global variableDict
    return variableDict


def start_scan(variableDict, fname):
    Logger("log").info(' ')
    Logger("log").info('  *** start_scan')

    def cleanup(signal, frame):
        stop_scan(global_PVs, variableDict)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    if variableDict.has_key('StopTheScan'):
        stop_scan(global_PVs, variableDict)
        return

    # moved to outer loop in main()
    # pgInit(global_PVs, variableDict)

    setPSO(global_PVs, variableDict)

    # fname = global_PVs['HDF1_FileName'].get(as_string=True)
    Logger("log").info('  *** File name prefix: %s' % fname)

    pgSet(global_PVs, variableDict, fname) 

    open_shutters(global_PVs, variableDict)

    # # run fly scan
    theta = pgAcquisition(global_PVs, variableDict)

    theta_end =  global_PVs['Motor_SampleRot_RBV'].get()
    if (theta_end < 180.0):
        # print('\x1b[2;30;41m' + '  *** Rotary Stage ERROR. Theta stopped at: ***' + theta_end + '\x1b[0m')
        Logger("log").error('  *** Rotary Stage ERROR. Theta stopped at: %s ***' % str(theta_end))

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
            Logger("log").error('*** The Point Grey Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            Logger("log").error('  *** Failed!')
        else:
            Logger("log").info ('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
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

            # Logger("log").info("Sleep Scan: ", np.arange(start, end, step_size))

            # moved pgInit() here from start_scan() 
            pgInit(global_PVs, variableDict)
            
            for i in np.arange(start, end, step_size):
                tic_01 =  time.time()
                fname = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + "".join([chr(c) for c in global_PVs['Sample_Name'].get()]) 
                Logger("log").info('  *** Moving rotary stage to start position')
                global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
                Logger("log").info('  *** Moving rotary stage to start position: Done!')

                start_scan(variableDict, fname)

                if ((i+1)!=end):
                    Logger("log").info('          *** Wait (s): %s ' % str(variableDict['StartSleep_s']))
                    time.sleep(variableDict['StartSleep_s']) 

                Logger("log").info(' ')
                Logger("log").info('  *** Total scan time: %s minutes' % str((time.time() - tic_01)/60.))
                Logger("log").info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            Logger("log").info('  *** Total loop scan time: %s minutes' % str((time.time() - tic)/60.))
            global_PVs['Cam1_ImageMode'].put('Continuous')
            Logger("log").info('  *** Done!')

    except  KeyError:
        Logger("log").info('  *** Some PV assignment failed!')
        pass
        
        

if __name__ == '__main__':
    main()
