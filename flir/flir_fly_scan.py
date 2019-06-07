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

import flir_lib
import flir_scan_lib
import log_lib 
import dm_lib 


global variableDict

variableDict = {
        'SampleXIn': 0, 
        'SampleXOut': 3,
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
        'FurnaceYOut': 48.0,
        'LogFileName': 'log.log'
        }

global_PVs = {}

lfname = 'logs/' + datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S") + '.log'
LOG, fHandler = log_lib.setup_logger(lfname)
variableDict['LogFileName'] = lfname


def getVariableDict():
    global variableDict
    return variableDict


def main():
    tic =  time.time()
    flir_lib.update_variable_dict(variableDict)
    flir_lib.init_general_PVs(global_PVs, variableDict)
    
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log_lib.Logger(lfname).info('*** The Point Grey Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            log_lib.Logger(lfname).info('  *** Failed!')
        else:
            log_lib.Logger(lfname).info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (variableDict['IOC_Prefix'], detector_sn))
            
            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get()
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = flir_lib.calc_blur_pixel(global_PVs, variableDict)
            variableDict['SlewSpeed'] = rot_speed

            # moved pgInit() here from tomo_fly_scan() 
            flir_lib.pgInit(global_PVs, variableDict)
            # get sample file name
            # fname = global_PVs['HDF1_FileName'].get(as_string=True)
            fname = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + "".join([chr(c) for c in global_PVs['Sample_Name'].get()]) 

            flir_scan_lib.tomo_fly_scan(global_PVs, variableDict, fname)

            log_lib.Logger(lfname).info(' ')
            log_lib.Logger(lfname).info('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
            log_lib.Logger(lfname).info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))

            log_lib.Logger(lfname).info('  *** Moving rotary stage to start position')
            global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
            log_lib.Logger(lfname).info('  *** Moving rotary stage to start position: Done!')

            global_PVs['Cam1_ImageMode'].put('Continuous')

            dm_lib.scp(global_PVs, variableDict)

            log_lib.Logger(lfname).info('  *** Done!')

    except  KeyError:
        log_lib.Logger(lfname).error('  *** Some PV assignment failed!')
        pass
        
        

if __name__ == '__main__':
    main()
