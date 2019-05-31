'''
    Auto focus for 2-BM

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

from flir.flir_lib import *

# global variableDict

# variableDict = {
#         'rscan_range': 2,                 # relative motion in mm
#         'nSteps': 20,
#         'StartSleep_min': 0,
#         'StabilizeSleep_ms': 250,
#         # ####################### DO NOT MODIFY THE PARAMETERS BELOW ###################################
#         'CCD_Readout': 0.006,              # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
#         # 'CCD_Readout': 0.01,             # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
#         'Station': '2-BM-A',
#         'ExposureTime': 0.1,                # to use this as default value comment the variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get() line
#         'IOC_Prefix': '2bmbSP1:',           # options: 1. PointGrey: '2bmbPG3:', 2. Gbe '2bmbSP1:' 
#         }

# global_PVs = {}

# LOG = logging.basicConfig(format = "%(asctime)s %(logger_name)s %(color)s  %(message)s %(endColor)s", level=logging.INFO)

# def getVariableDict():
#     global variableDict
#     return variableDict


# def focus_scan(variableDict):
#     Logger("log").info(' ')

#     def cleanup(signal, frame):
#         stop_scan(global_PVs, variableDict)
#         sys.exit(0)
#     signal.signal(signal.SIGINT, cleanup)

#     if variableDict.has_key('StopTheScan'):
#         stop_scan(global_PVs, variableDict)
#         return

#     pgInit(global_PVs, variableDict)
#     pgSet(global_PVs, variableDict) 
#     open_shutters(global_PVs, variableDict)

#     Logger("log").info('  *** start focus scan')
#     # Get the CCD parameters:
#     nRow = global_PVs['Cam1_SizeY_RBV'].get()
#     nCol = global_PVs['Cam1_SizeX_RBV'].get()
#     image_size = nRow * nCol

#     Motor_Name = global_PVs['Motor_Focus_Name'].get()
#     Logger("log").info('  *** Scanning ' + Motor_Name)

#     Motor_Start_Pos = global_PVs['Motor_Focus'].get() - float(variableDict['rscan_range']/2)
#     Motor_End_Pos = global_PVs['Motor_Focus'].get() + float(variableDict['rscan_range']/2)
#     vector_pos = numpy.linspace(Motor_Start_Pos, Motor_End_Pos, int(variableDict['nSteps']))
#     vector_std = numpy.copy(vector_pos)

#     global_PVs['Cam1_FrameType'].put(FrameTypeData, wait=True)
#     global_PVs['Cam1_NumImages'].put(1, wait=True)
#     global_PVs['Cam1_TriggerMode'].put('Off', wait=True)
#     wait_time_sec = int(variableDict['ExposureTime']) + 5

#     cnt = 0
#     for sample_pos in vector_pos:
#         Logger("log").info('  *** Motor position: %s' % sample_pos)
#         # for testing with out beam: comment focus motor motion
#         global_PVs['Motor_Focus'].put(sample_pos, wait=True)
#         time.sleep(float(variableDict['StabilizeSleep_ms'])/1000)
#         time.sleep(1)
#         global_PVs['Cam1_Acquire'].put(DetectorAcquire, wait=True, timeout=1000.0)
#         time.sleep(0.1)
#         if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec) == False: # adjust wait time
#             global_PVs['Cam1_Acquire'].put(DetectorIdle)
        
#         # Get the image loaded in memory
#         img_vect = global_PVs['Cam1_Image'].get(count=image_size)
#         #img = np.reshape(img_vect,[nRow, nCol])
#         vector_std[cnt] = numpy.std(img_vect)
#         Logger("log").info('  ***   *** Standard deviation: %s ' % str(vector_std[cnt]))
#         cnt = cnt + 1

#     # # move the lens to the focal position:
#     # max_std = numpy.max(vector_std)
#     # focal_pos = vector_pos[numpy.where(vector_std == max_std)]
#     # Logger("log").info('  *** Highest standard deviation: ', str(max_std))
#     # Logger("log").info('  *** Move piezo to ', str(focal_pos))
#     # global_PVs[Motor_Focus].put(focal_pos, wait=True)

#     # # Post scan:
#     # close_shutters(global_PVs, variableDict)
#     # time.sleep(2)
#     # pgInit(global_PVs, variableDict)
    
#     return

# def main():

#     update_variable_dict(variableDict)
#     init_general_PVs(global_PVs, variableDict)
#     try:
#         detector_sn = global_PVs['Cam1_SerialNumber'].get()
#         if ((detector_sn == None) or (detector_sn == 'Unknown')):
#             Logger("log").error('*** The Point Grey Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
#             Logger("log").error('  *** Failed!')
#         else:
#             Logger("log").info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
#                 % (variableDict['IOC_Prefix'], detector_sn))
#             focus_scan(variableDict)
#     except  KeyError:
#         Logger("log").error('  *** Some PV assignment failed!')
#         # Logger("log").error('  *** Some PV assignment failed!', KeyError)
#         pass


# if __name__ == '__main__':
#     main()
