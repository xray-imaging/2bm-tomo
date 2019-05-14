'''
    TomoScan for Sector 32 ID C

'''
import sys
import json
import time
from epics import PV
import h5py
import shutil
import os
import imp
import traceback
import numpy

from tomo_scan_lib import *

global variableDict

variableDict = {
        'rscan_range': 0.2,                 # relative motion in mm
        'nSteps': 5,
        'StartSleep_min': 0,
        'StabilizeSleep_ms': 250,
        'ExposureTime': 0.005,
        'IOC_Prefix': '2bmbSP1:',           # options: 1. PointGrey: '2bmbPG3:', 2. Gbe '2bmbSP1:' 
        'Display_live': 1
        }

global_PVs = {}

def getVariableDict():
    global variableDict
    return variableDict

def getVariableDict():
    return variableDict

print('#######################################')
print('############ Starting Scan ############')
print('#######################################')

def lens_scan():
    print 'lens_scan()'

    # Get the CCD parameters:
    nRow = global_PVs['nRow'].get()
    nCol = global_PVs['nCol'].get()
    image_size = nRow * nCol

    Motor_Name = global_PVs[Motor_Focus_Name].get()
    print('*** Scanning ' + Motor_Name)

    Motor_Start_Pos = global_PVs[Motor_Focus].get() - float(variableDict['rscan_range']/2)
    Motor_End_Pos = global_PVs[Motor_Focus].get() + float(variableDict['rscan_range']/2)
    vector_pos = numpy.linspace(Motor_Start_Pos, Motor_End_Pos, int(variableDict['nSteps']))
    vector_std = numpy.copy(vector_pos)

    global_PVs['Cam1_FrameType'].put(FrameTypeData, wait=True)
    global_PVs['Cam1_NumImages'].put(1, wait=True)
    
    cnt = 0
    for sample_pos in vector_pos:
        print('  '); print('  ### Motor position:', sample_pos); print('  ')
        global_PVs[Motor_Focus].put(sample_pos, wait=True)
        time.sleep(float(variableDict['StabilizeSleep_ms'])/1000)

        global_PVs['Cam1_Acquire'].put(DetectorAcquire)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)
        global_PVs['Cam1_SoftwareTrigger'].put(1)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, 60)
        
        # Get the image loaded in memory
        img_vect = global_PVs['Cam1_Image'].get(count=image_size)
        #img = np.reshape(img_vect,[nRow, nCol])
        vector_std[cnt] = numpy.std(img_vect)
        print(' --> Standard deviation: ', str(vector_std[cnt]))
        cnt = cnt + 1

    # move the lens to the focal position:
    max_std = numpy.max(vector_std)
    focal_pos = vector_pos[numpy.where(vector_std == max_std)]
    print(' *** Highest standard deviation: ', str(max_std))
    print(' *** Move piezo to ', str(focal_pos))
    global_PVs[Motor_Focus].put(focal_pos, wait=True)
    
    return


def start_scan():
    print 'start_scan()'
    init_general_PVs(global_PVs, variableDict)
        if variableDict.has_key('StopTheScan'): # stopping the scan in a clean way
        stop_scan(global_PVs, variableDict)
        return
    setup_detector(global_PVs, variableDict)
    open_shutters(global_PVs, variableDict)
    
    # Main scan:
    ####################################################
    lens_scan()
    ####################################################

    # Post scan:
    close_shutters(global_PVs, variableDict)
    reset_CCD(global_PVs, variableDict)

def main():
    update_variable_dict(variableDict)
    start_scan()

if __name__ == '__main__':
    main()
