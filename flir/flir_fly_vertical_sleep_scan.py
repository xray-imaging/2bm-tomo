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

from flir_lib import *
from flir_scan_lib import *

global variableDict

variableDict = {
        'StartY': 20.0,
        'EndY': 32.5,
        'StepSize': 3.0,
        'SampleXIn': 0.0,
        'SampleXOut': -11.0,
        'StartSleep_s': 180,              # wait time (s) between each data collection
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
        # 'CCD_Readout': 0.006,             # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
        'CCD_Readout': 0.01,             # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
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


def main():
    tic =  time.time()
    update_variable_dict(variableDict)
    init_general_PVs(global_PVs, variableDict)
    
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            Logger("log").info('*** The Point Grey Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            Logger("log").info('  *** Failed!')
        else:
            Logger("log").info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
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

            # moved pgInit() here from tomo_fly_scan() 
            pgInit(global_PVs, variableDict)

            Logger("log").info(' ')
            Logger("log").info("  *** Running %d scans" % len(np.arange(start, end, step_size)))
            Logger("log").info(' ')
            Logger("log").info('  *** Vertical Positions (mm): %s' % np.arange(start, end, step_size))
            for ii in range(200):
                for i in np.arange(start, end, step_size):
                    fname = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + "".join([chr(c) for c in global_PVs['Sample_Name'].get()]) 
                    # Logger("log").info('  *** Moving rotary stage to start position')
                    # global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
                    # Logger("log").info('  *** Moving rotary stage to start position: Done!')

                    Logger("log").info('*** The sample vertical position is at %s mm' % (i))
                    global_PVs['Motor_SampleY'].put(i, wait=True)

                    tomo_fly_scan(global_PVs, variableDict, fname)
                    Logger("log").info(' ')
                    Logger("log").info('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
                    Logger("log").info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
                Logger("log").info('          *** Wait (s): %s ' % str(variableDict['StartSleep_s']))
                time.sleep(variableDict['StartSleep_s']) 

            Logger("log").info('  *** Moving rotary stage to start position')
            global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
            Logger("log").info('  *** Moving rotary stage to start position: Done!')

            global_PVs['Cam1_ImageMode'].put('Continuous')

            Logger("log").info('  *** Done!')

    except  KeyError:
        Logger("log").error('  *** Some PV assignment failed!')
        pass
        
        

if __name__ == '__main__':
    main()
