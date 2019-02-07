'''
    FlyScan for Sector 2-BM using Point Grey Grasshooper3 or FLIR Oryx cameras

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
        'SampleXIn': 0.0,
        'SampleXOut': 1.0,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 1500,
        'NumDarkImages': 20,
        'NumWhiteImages': 20,
        # ####################### DO NOT MODIFY THE PARAMETERS BELOW ###################################
        'Station': '2-BM-B',
        'ExposureTime': 0.1,              # to use this as default value comment the variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get() line
        'roiSizeX': 1920, 
        'roiSizeY': 1200,       
        'SlewSpeed': 0.8,                  # to use this as default value comment the calc_pixel_blur(global_PVs, variableDict) function below
        'AcclRot': 10.0,
        'IOC_Prefix': '2bmbPG3:',          # options: 1. PointGrey: '2bmbPG3:', 2. FLIR Oryx '2bmbSP1:' 
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05,
        'ShutterOpenDelay': 0.00,
        'Recursive_Filter_Enabled': True,
        'Recursive_Filter_N_Images': 4
        }

global_PVs = {}


def getVariableDict():
    global variableDict
    return variableDict


def start_scan(variableDict, fname):
    print(' ')
    print('  *** Start scan')

    def cleanup(signal, frame):
        stop_scan(global_PVs, variableDict)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    if variableDict.has_key('StopTheScan'):
        stop_scan(global_PVs, variableDict)
        return

    pgInit(global_PVs, variableDict)
    setPSO(global_PVs, variableDict)

    fname = global_PVs['HDF1_FileName'].get(as_string=True)
    print(' ')
    print('  *** File name prefix: %s' % fname)

    pgSet(global_PVs, variableDict, fname) 

    open_shutters(global_PVs, variableDict)

    # run fly scan
    theta = pgAcquisition(global_PVs, variableDict)

    pgAcquireFlat(global_PVs, variableDict)
    close_shutters(global_PVs, variableDict)
    time.sleep(2)

    pgAcquireDark(global_PVs, variableDict)

    add_theta(global_PVs, variableDict, theta)
    global_PVs['Fly_ScanControl'].put('Standard')

    if wait_pv(global_PVs['HDF1_Capture'], 0, 10) == False:
        global_PVs['HDF1_Capture'].put(0)
    pgInit(global_PVs, variableDict)
    print('  *** Start scan: Done!')


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
            # calling calc_pixel_blur() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = calc_pixel_blur(global_PVs, variableDict)
            variableDict['SlewSpeed'] = rot_speed

            # get sample file name
            fname = global_PVs['HDF1_FileName'].get(as_string=True)
            print(' ')
            print('  *** Moving rotary stage to start position')
            global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
            print('  *** Moving rotary stage to start position: Done!')
            start_scan(variableDict, fname)
            print(' ')
            print('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
            print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            print('  *** Done!')

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass
        
        

if __name__ == '__main__':
    main()
