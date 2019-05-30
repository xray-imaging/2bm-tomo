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
        'StartY': 19.746750,
        'EndY': 17.946750,
        'StepSizeY': -1.8,
        'StartX': -3.0,
        'EndX': 0.0,
        'StepSizeX': 1.5,
        'SampleXIn': 0.0, 
        'SampleXOut': -5,
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

            start_y = variableDict['StartY']
            end_y = variableDict['EndY']
            step_size_y = variableDict['StepSizeY']


            start_x = variableDict['StartX']
            end_x = variableDict['EndX']
            step_size_x = variableDict['StepSizeX']

            # moved pgInit() here from tomo_fly_scan() 
            pgInit(global_PVs, variableDict)

            Logger("log").info(' ')
            Logger("log").info("  *** Running %d scans" % (len(np.arange(start_x, end_x, step_size_x)) * len(np.arange(start_y, end_y, step_size_y))))
            Logger("log").info(' ')
            Logger("log").info('  *** Horizontal Positions (mm): %s' % np.arange(start_x, end_x, step_size_x))
            Logger("log").info('  *** Vertical Positions (mm): %s' % np.arange(start_y, end_y, step_size_y))
            for i in np.arange(start_y, end_y, step_size_y):
                # Logger("log").info('  *** Moving rotary stage to start position')
                # global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
                # Logger("log").info('  *** Moving rotary stage to start Y position: Done!')

                Logger("log").info('*** The sample vertical position is at %s mm' % (i))
                global_PVs['Motor_SampleY'].put(i, wait=True)
                for j in np.arange(start_x, end_x, step_size_x):
                    Logger("log").info('*** The sample horizontal position is at %s mm' % (j))
                    global_PVs['Motor_Sample_Top_90'].put(j, wait=True)
                    fname = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + "".join([chr(c) for c in global_PVs['Sample_Name'].get()]) 
                    tomo_fly_scan(global_PVs, variableDict, fname)
                Logger("log").info(' ')
                Logger("log").info('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
                Logger("log").info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))

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
