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
        'SampleXIn': 0.0,
        'SampleXOut': 1.0,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'Projections': 1500,
        'NumWhiteImages': 20,
        'NumDarkImages': 20,
        # ####################### DO NOT MODIFY THE PARAMETERS BELOW ###################################
        'Station': '2-BM-B',
        'ExposureTime': 0.01,             # to use this as default value comment the variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get() line
        # 'roiSizeX': 2448, 
        # 'roiSizeY': 2048,       
        'SlewSpeed': 5.0,                 # to use this as default value comment the calc_blur_pixel(global_PVs, variableDict) function below
        # 'AcclRot': 10.0,
        'IOC_Prefix': '2bmbSP1:',         # options: 1. PointGrey: '2bmbPG3:', 2. Gbe '2bmbSP1:' 
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.005,             # options: 1. 8bit: 0.005, 2. 16-bit: 0.01
        'ShutterOpenDelay': 0.00,
        'Recursive_Filter_Enabled': False,
        'Recursive_Filter_N_Images': 4
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


    pgInit(global_PVs, variableDict)

    # pgSet(global_PVs, variableDict, fname) 



def main():
    tic =  time.time()
    update_variable_dict(variableDict)
    init_general_PVs(global_PVs, variableDict)
    
    if (0==0):
    # try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            Logger("log").info('*** The Point Grey Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            Logger("log").info('  *** Failed!')
        else:
            print ('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (variableDict['IOC_Prefix'], detector_sn))
            
            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get()
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = calc_blur_pixel(global_PVs, variableDict)
            variableDict['SlewSpeed'] = rot_speed

            # get sample file name
            fname = global_PVs['HDF1_FileName'].get(as_string=True)
            Logger("log").info('  *** Moving rotary stage to start position')
            global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
            Logger("log").info('  *** Moving rotary stage to start position: Done!')
            start_scan(variableDict, fname)
            Logger("log").info(' ')
            Logger("log").info('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
            Logger("log").info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            Logger("log").info('  *** Done!')

    # except  KeyError:
    #     Logger("log").error('  *** Some PV assignment failed!')
    #     pass
        
        

if __name__ == '__main__':
    main()
