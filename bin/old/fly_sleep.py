#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from datetime import datetime
import numpy as np
import pathlib

import libs.aps2bm_lib as aps2bm_lib
import libs.scan_lib as scan_lib
import libs.log_lib as log_lib
import libs.dm_lib as dm_lib

global variableDict

variableDict = {
        'SleepStep': 4,
        'SleepTime_s': 270,                # wait time (s) between each data collection
        # 'SampleXIn': 0.0,
        # 'SampleXOut': 3,
        'SampleYIn': 19.95,                 # to use Y change the sampleInOutVertical = True
        'SampleYOut': 14.95,
        'SampleInOutVertical': True,     # False: use X to take the white field
        'SampleMoveEnabled': True,        # False to freeze sample motion during white field data collection
        'SampleRotStart': 0.0,
        'SampleRotEnd':180.0,
        'Projections': 1500,
        'NumWhiteImages': 20,
        'NumDarkImages': 20,
        # ####################### DO NOT MODIFY THE PARAMETERS BELOW ###################################
        #'CCD_Readout': 0.0065,              # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
        'CCD_Readout': 0.01,             # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
        'Station': '2-BM-A',
        'ExposureTime': 0.05, #0.01             # to use this as default value comment the variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get() line
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
        'FurnaceYOut': 48.0,
        'RemoteAnalysisDir' : 'tomo@mona3:/local/data/' #'tomo@handyn:/local/data/' #
        }

global_PVs = {}


def getVariableDict():
    global variableDict
    return variableDict


def main():
    # create logger
    # # python 3.5+ 
    # home = str(pathlib.Path.home())
    home = os.path.expanduser("~")
    logs_home = home + '/logs/'

    # make sure logs directory exists
    if not os.path.exists(logs_home):
        os.makedirs(logs_home)

    lfname = logs_home + datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S") + '.log'
    log_lib.setup_logger(lfname)

    tic =  time.time()
    aps2bm_lib.update_variable_dict(variableDict)
    aps2bm_lib.init_general_PVs(global_PVs, variableDict)
    
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log_lib.error('*** The Point Grey Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            log_lib.error('  *** Failed!')
        else:
            log_lib.info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (variableDict['IOC_Prefix'], detector_sn))
            
            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get()
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = aps2bm_lib.calc_blur_pixel(global_PVs, variableDict)
            variableDict['SlewSpeed'] = rot_speed

            # start = variableDict['SleepStart']
            # end = variableDict['SleepEnd']
            # step_size = variableDict['SleepStep']

            start = 0
            end = variableDict['SleepStep']
            step_size = 1

            # init camera
            aps2bm_lib.pgInit(global_PVs, variableDict)
            
            log_lib.info(' ')
            log_lib.info("  *** Running %d scans" % len(np.arange(start, end, step_size)))
            for i in np.arange(start, end, step_size):
                tic_01 =  time.time()
                fname = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + global_PVs['Sample_Name'].get(as_string=True)

                log_lib.info(' ')
                log_lib.info('  *** Start scan %d' % i)

                scan_lib.tomo_fly_scan(global_PVs, variableDict, fname)

                if ((i+1)!=end):
                    log_lib.warning('  *** Wait (s): %s ' % str(variableDict['SleepTime_s']))
                    time.sleep(variableDict['SleepTime_s']) 

                log_lib.info(' ')
                log_lib.info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
                log_lib.info('  *** Total scan time: %s minutes' % str((time.time() - tic_01)/60.))
                log_lib.info('  *** Scan Done!')
    
                dm_lib.scp(global_PVs, variableDict)

            log_lib.info('  *** Total loop scan time: %s minutes' % str((time.time() - tic)/60.))
 
            log_lib.info('  *** Moving rotary stage to start position')
            global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
            log_lib.info('  *** Moving rotary stage to start position: Done!')

            global_PVs['Cam1_ImageMode'].put('Continuous')
 
            log_lib.info('  *** Done!')

    except  KeyError:
        log_lib.error('  *** Some PV assignment failed!')
        pass
        
        

if __name__ == '__main__':
    main()
