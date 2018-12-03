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
        'ExposureTime': 0.01,
        'SlewSpeed': 0.8, # to use this as default value comment the calc_blur_pixel(global_PVs, variableDict) function below
        'AcclRot': 10.0,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 600,
        'SampleXIn': 0.0,
        'SampleXOut': 1.0,
        'roiSizeX': 1920, 
        'roiSizeY': 1200,       
        'PostDarkImages': 20,
        'PostWhiteImages': 20,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': '2bmbPG3:', # options: 1. PointGrey: '2bmbPG3:', 2. Gbe '2bmbSP1:' 
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05,
        'Station': '2-BM-B',
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

    setPSO(global_PVs, variableDict)

    fname = global_PVs['HDF1_FileName'].get(as_string=True)
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
            
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = calc_blur_pixel(global_PVs, variableDict)
            variableDict['SlewSpeed'] = rot_speed

            # get sample file name
            fname = global_PVs['HDF1_FileName'].get(as_string=True)
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
