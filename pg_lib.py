'''
    Tomo Scan Lib for Sector 2-BM  using Point Grey Grasshooper3 or FLIR Oryx cameras
    
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
import math
import signal

import numpy as np

TESTING = True

ShutterAisFast = True           # True: use m7 as shutter; False: use Front End Shutter

ShutterA_Open_Value = 1
ShutterA_Close_Value = 0
ShutterB_Open_Value = 1
ShutterB_Close_Value = 0

FrameTypeData = 0
FrameTypeDark = 1
FrameTypeWhite = 2

DetectorIdle = 0
DetectorAcquire = 1
EPSILON = 0.1

Recursive_Filter_Type = 'RecursiveAve'


def update_variable_dict(variableDict):
    argDic = {}
    if len(sys.argv) > 1:
        strArgv = sys.argv[1]
        argDic = json.loads(strArgv)
    # print('orig variable dict', variableDict)
    # for k,v in argDic.items(): # python 3
    for k,v in argDic.iteritems():
        variableDict[k] = v
    # print('new variable dict', variableDict)


def wait_pv(pv, wait_val, max_timeout_sec=-1):
#wait on a pv to be a value until max_timeout (default forever)

    #print('wait_pv(', pv.pvname, wait_val, max_timeout_sec, ')')
    
    # delay for pv to change
    time.sleep(.01)
    startTime = time.time()
    while(True):
        pv_val = pv.get()
        if type(pv_val) == float:
            if abs(pv_val - wait_val) < EPSILON:
                return True
        if (pv_val != wait_val):
            if max_timeout_sec > -1:
                curTime = time.time()
                diffTime = curTime - startTime
                if diffTime >= max_timeout_sec:
                    print('  *** ERROR: DROPPED IMAGES ***')
                    print('  *** wait_pv(', pv.pvname, wait_val, max_timeout_sec, ') reached max timeout. Return False')
                    print('  *** ERROR: DROPPED IMAGES ***')
                    return False
            time.sleep(.01)
        else:
            return True


def init_general_PVs(global_PVs, variableDict):

    # shutter pv's
    global_PVs['ShutterA_Open'] = PV('2bma:A_shutter:open.VAL')
    global_PVs['ShutterA_Close'] = PV('2bma:A_shutter:close.VAL')
    global_PVs['ShutterA_Move_Status'] = PV('PA:02BM:STA_A_FES_OPEN_PL')
    global_PVs['ShutterB_Open'] = PV('2bma:B_shutter:open.VAL')
    global_PVs['ShutterB_Close'] = PV('2bma:B_shutter:close.VAL')
    global_PVs['ShutterB_Move_Status'] = PV('PA:02BM:STA_B_SBS_OPEN_PL')

    global_PVs['Sample_Name'] = PV('2bmb:caputRecorderGbl_4')

    if variableDict['Station'] == '2-BM-A':
        print('*** Running in station A:')
        # Set sample stack motor pv's:
        global_PVs['Motor_SampleX'] = PV('2bma:m49.VAL')
        global_PVs['Motor_SampleY'] = PV('2bma:m20.VAL')
        global_PVs['Motor_SampleRot'] = PV('2bma:m82.VAL') # Aerotech ABR-250
        global_PVs['Motor_SampleRot_Cnen'] = PV('2bma:m82.CNEN') 
        global_PVs['Motor_SampleRot_Accl'] = PV('2bma:m82.ACCL') 
        global_PVs['Motor_SampleRot_Stop'] = PV('2bma:m82.STOP') 
        global_PVs['Motor_SampleRot_Set'] = PV('2bma:m82.SET') 
        global_PVs['Motor_SampleRot_Velo'] = PV('2bma:m82.VELO') 
        global_PVs['Motor_Sample_Top_0'] = PV('2bmS1:m2.VAL')
        global_PVs['Motor_Sample_Top_90'] = PV('2bmS1:m1.VAL') 
        # Set FlyScan
        global_PVs['Fly_ScanDelta'] = PV('2bma:PSOFly2:scanDelta')
        global_PVs['Fly_StartPos'] = PV('2bma:PSOFly2:startPos')
        global_PVs['Fly_EndPos'] = PV('2bma:PSOFly2:endPos')
        global_PVs['Fly_SlewSpeed'] = PV('2bma:PSOFly2:slewSpeed')
        global_PVs['Fly_Taxi'] = PV('2bma:PSOFly2:taxi')
        global_PVs['Fly_Run'] = PV('2bma:PSOFly2:fly')
        global_PVs['Fly_ScanControl'] = PV('2bma:PSOFly2:scanControl')
        global_PVs['Fly_Calc_Projections'] = PV('2bma:PSOFly2:numTriggers')
        global_PVs['Theta_Array'] = PV('2bma:PSOFly2:motorPos.AVAL')

        global_PVs['Fast_Shutter'] = PV('2bma:m23.VAL')
        global_PVs['Motor_Focus'] = PV('2bma:m54.VAL')
        global_PVs['Motor_Focus_Name'] = PV('2bma:m54.DESC')
        
    elif variableDict['Station'] == '2-BM-B':   
        print('*** Running in station B:')
        # Sample stack motor pv's:
        global_PVs['Motor_SampleX'] = PV('2bmb:m63.VAL')
        global_PVs['Motor_SampleY'] = PV('2bmb:m57.VAL') 
        global_PVs['Motor_SampleRot'] = PV('2bmb:m100.VAL') # Aerotech ABR-150
        global_PVs['Motor_SampleRot_Accl'] = PV('2bma:m100.ACCL') 
        global_PVs['Motor_SampleRot_Stop'] = PV('2bma:m100.STOP') 
        global_PVs['Motor_SampleRot_Set'] = PV('2bma:m100.SET') 
        global_PVs['Motor_SampleRot_Velo'] = PV('2bma:m100.VELO') 
        global_PVs['Motor_Sample_Top_0'] = PV('2bmb:m76.VAL') 
        global_PVs['Motor_Sample_Top_90'] = PV('2bmb:m77.VAL')

        # Set CCD stack motor PVs:
        global_PVs['Motor_CCD_Z'] = PV('2bmb:m31.VAL')

        # Set FlyScan
        global_PVs['Fly_ScanDelta'] = PV('2bmb:PSOFly:scanDelta')
        global_PVs['Fly_StartPos'] = PV('2bmb:PSOFly:startPos')
        global_PVs['Fly_EndPos'] = PV('2bmb:PSOFly:endPos')
        global_PVs['Fly_SlewSpeed'] = PV('2bmb:PSOFly:slewSpeed')
        global_PVs['Fly_Taxi'] = PV('2bmb:PSOFly:taxi')
        global_PVs['Fly_Run'] = PV('2bmb:PSOFly:fly')
        global_PVs['Fly_ScanControl'] = PV('2bmb:PSOFly:scanControl')
        global_PVs['Fly_Calc_Projections'] = PV('2bmb:PSOFly:numTriggers')
        global_PVs['Theta_Array'] = PV('2bmb:PSOFly:motorPos.AVAL')

        global_PVs['Motor_Focus'] = PV('2bmb:m78.VAL')
        global_PVs['Motor_Focus_Name'] = PV('2bmb:m78.DESC')

    else:
        print('*** %s is not a valid station' % variableDict['Station'])

    # detector pv's
    if ((variableDict['IOC_Prefix'] == '2bmbPG3:') or (variableDict['IOC_Prefix'] == '2bmbSP1:')): 
    
        # init Point Grey PV's
        # general PV's
        global_PVs['Cam1_SerialNumber'] = PV(variableDict['IOC_Prefix'] + 'cam1:SerialNumber_RBV')
        global_PVs['Cam1_ImageMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:ImageMode')
        global_PVs['Cam1_ArrayCallbacks'] = PV(variableDict['IOC_Prefix'] + 'cam1:ArrayCallbacks')
        global_PVs['Cam1_AcquirePeriod'] = PV(variableDict['IOC_Prefix'] + 'cam1:AcquirePeriod')
        global_PVs['Cam1_TriggerMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:TriggerMode')
        global_PVs['Cam1_SoftwareTrigger'] = PV(variableDict['IOC_Prefix'] + 'cam1:SoftwareTrigger')  ### ask Mark is this is exposed in the medm screen
        global_PVs['Cam1_AcquireTime'] = PV(variableDict['IOC_Prefix'] + 'cam1:AcquireTime')
        global_PVs['Cam1_FrameType'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType')
        global_PVs['Cam1_NumImages'] = PV(variableDict['IOC_Prefix'] + 'cam1:NumImages')
        global_PVs['Cam1_Acquire'] = PV(variableDict['IOC_Prefix'] + 'cam1:Acquire')
        global_PVs['Cam1_AttributeFile'] = PV(variableDict['IOC_Prefix'] + 'cam1:NDAttributesFile')
        global_PVs['Cam1_FrameTypeZRST'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType.ZRST')
        global_PVs['Cam1_FrameTypeONST'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType.ONST')
        global_PVs['Cam1_FrameTypeTWST'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType.TWST')
        global_PVs['Cam1_Display'] = PV(variableDict['IOC_Prefix'] + 'image1:EnableCallbacks')

        global_PVs['Cam1_SizeX'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeX')
        global_PVs['Cam1_SizeY'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeY')
        global_PVs['Cam1_SizeX_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeX_RBV')
        global_PVs['Cam1_SizeY_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeY_RBV')
        global_PVs['Cam1_MaxSizeX_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:MaxSizeX_RBV')
        global_PVs['Cam1_MaxSizeY_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:MaxSizeY_RBV')
        global_PVs['Cam1PixelFormat_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:PixelFormat_RBV')

        global_PVs['Cam1_Image'] = PV(variableDict['IOC_Prefix'] + 'image1:ArrayData')

        # hdf5 writer PV's
        global_PVs['HDF1_AutoSave'] = PV(variableDict['IOC_Prefix'] + 'HDF1:AutoSave')
        global_PVs['HDF1_DeleteDriverFile'] = PV(variableDict['IOC_Prefix'] + 'HDF1:DeleteDriverFile')
        global_PVs['HDF1_EnableCallbacks'] = PV(variableDict['IOC_Prefix'] + 'HDF1:EnableCallbacks')
        global_PVs['HDF1_BlockingCallbacks'] = PV(variableDict['IOC_Prefix'] + 'HDF1:BlockingCallbacks')
        global_PVs['HDF1_FileWriteMode'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileWriteMode')
        global_PVs['HDF1_NumCapture'] = PV(variableDict['IOC_Prefix'] + 'HDF1:NumCapture')
        global_PVs['HDF1_Capture'] = PV(variableDict['IOC_Prefix'] + 'HDF1:Capture')
        global_PVs['HDF1_Capture_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:Capture_RBV')
        global_PVs['HDF1_FileName'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileName')
        global_PVs['HDF1_FullFileName_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FullFileName_RBV')
        global_PVs['HDF1_FileTemplate'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileTemplate')
        global_PVs['HDF1_ArrayPort'] = PV(variableDict['IOC_Prefix'] + 'HDF1:NDArrayPort')
        global_PVs['HDF1_FileNumber'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileNumber')
        global_PVs['HDF1_XMLFileName'] = PV(variableDict['IOC_Prefix'] + 'HDF1:XMLFileName')

        global_PVs['HDF1_QueueSize'] = PV(variableDict['IOC_Prefix'] + 'HDF1:QueueSize')
        global_PVs['HDF1_QueueFree'] = PV(variableDict['IOC_Prefix'] + 'HDF1:QueueFree')
                                                                      
        # proc1 PV's
        global_PVs['Image1_Callbacks'] = PV(variableDict['IOC_Prefix'] + 'image1:EnableCallbacks')
        global_PVs['Proc1_Callbacks'] = PV(variableDict['IOC_Prefix'] + 'Proc1:EnableCallbacks')
        global_PVs['Proc1_ArrayPort'] = PV(variableDict['IOC_Prefix'] + 'Proc1:NDArrayPort')
        global_PVs['Proc1_Filter_Enable'] = PV(variableDict['IOC_Prefix'] + 'Proc1:EnableFilter')
        global_PVs['Proc1_Filter_Type'] = PV(variableDict['IOC_Prefix'] + 'Proc1:FilterType')
        global_PVs['Proc1_Num_Filter'] = PV(variableDict['IOC_Prefix'] + 'Proc1:NumFilter')
        global_PVs['Proc1_Reset_Filter'] = PV(variableDict['IOC_Prefix'] + 'Proc1:ResetFilter')
        global_PVs['Proc1_AutoReset_Filter'] = PV(variableDict['IOC_Prefix'] + 'Proc1:AutoResetFilter')
        global_PVs['Proc1_Filter_Callbacks'] = PV(variableDict['IOC_Prefix'] + 'Proc1:FilterCallbacks')       

        global_PVs['Proc1_Enable_Background'] = PV(variableDict['IOC_Prefix'] + 'Proc1:EnableBackground')
        global_PVs['Proc1_Enable_FlatField'] = PV(variableDict['IOC_Prefix'] + 'Proc1:EnableFlatField')
        global_PVs['Proc1_Enable_Offset_Scale'] = PV(variableDict['IOC_Prefix'] + 'Proc1:EnableOffsetScale')
        global_PVs['Proc1_Enable_Low_Clip'] = PV(variableDict['IOC_Prefix'] + 'Proc1:EnableLowClip')
        global_PVs['Proc1_Enable_High_Clip'] = PV(variableDict['IOC_Prefix'] + 'Proc1:EnableHighClip')


    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):
        global_PVs['Cam1_FrameRateOnOff'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameRateOnOff')

    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):
        global_PVs['Cam1_AcquireTimeAuto'] = PV(variableDict['IOC_Prefix'] + 'cam1:AcquireTimeAuto')
        global_PVs['Cam1_FrameRateOnOff'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameRateEnable')

        global_PVs['Cam1_TriggerSource'] = PV(variableDict['IOC_Prefix'] + 'cam1:TriggerSource')
        global_PVs['Cam1_TriggerOverlap'] = PV(variableDict['IOC_Prefix'] + 'cam1:TriggerOverlap')
        global_PVs['Cam1_ExposureMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:ExposureMode')
        global_PVs['Cam1_TriggerSelector'] = PV(variableDict['IOC_Prefix'] + 'cam1:TriggerSelector')
        global_PVs['Cam1_TriggerActivation'] = PV(variableDict['IOC_Prefix'] + 'cam1:TriggerActivation')
    
    else:
        print ('Detector %s is not defined' % variableDict['IOC_Prefix'])
        return            


def stop_scan(global_PVs, variableDict):
        print(' ')
        print('  *** Stop scan called!')
        global_PVs['Motor_SampleRot_Stop'].put(1)
        global_PVs['HDF1_Capture'].put(0)
        wait_pv(global_PVs['HDF1_Capture'], 0)
        pgInit(global_PVs, variableDict)
        ##pgInit(global_PVs, variableDict)


def pgInit(global_PVs, variableDict):
    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):   
        print('  *** init Point Grey camera')
        global_PVs['Cam1_TriggerMode'].put('Internal', wait=True)    # 
        global_PVs['Cam1_TriggerMode'].put('Overlapped', wait=True)  # sequence Internal / Overlapped / internal because of CCD bug!!
        global_PVs['Cam1_TriggerMode'].put('Internal', wait=True)    #
        global_PVs['Proc1_Filter_Callbacks'].put( 'Every array' )
        global_PVs['Cam1_ImageMode'].put('Single', wait=True)
        global_PVs['Cam1_Display'].put(1)
        global_PVs['Cam1_Acquire'].put(DetectorAcquire)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)
        global_PVs['Proc1_Callbacks'].put('Disable')
        global_PVs['Proc1_Filter_Enable'].put('Disable')
        global_PVs['HDF1_ArrayPort'].put('PG3')
        print('  *** init Point Grey camera: Done!')
    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):   
        print('  *** init FLIR camera')
        global_PVs['Cam1_Acquire'].put(DetectorIdle)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, 2)
        # global_PVs['Proc1_Filter_Callbacks'].put( 'Every array', wait=True) # commented out to test if crash (ValueError: invalid literal for int() with base 0: 'Single') still occurs
        time.sleep(2) 
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)    # 
        time.sleep(7) 
        global_PVs['Cam1_ImageMode'].put('Single', wait=True)   # here is where it crashes with (ValueError: invalid literal for int() with base 0: 'Single') Added 7 s delay before
        global_PVs['Cam1_Display'].put(1)
        global_PVs['Cam1_Acquire'].put(DetectorAcquire)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2) 
        if variableDict['Station'] == '2-BM-A':
            global_PVs['Cam1_AttributeFile'].put('flir2bmaDetectorAttributes.xml')
            global_PVs['HDF1_XMLFileName'].put('flir2bmaLayout.xml')           
        else: # Mona (B-station)
            global_PVs['Cam1_AttributeFile'].put('flir2bmbDetectorAttributes.xml', wait=True) 
            global_PVs['HDF1_XMLFileName'].put('flir2bmbLayout.xml', wait=True) 
        print('  *** init FLIR camera: Done!')


def pgSet(global_PVs, variableDict, fname=None):

    # Set detectors
    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):   
        # setup Point Grey PV's
        print(' ')
        print('  *** setup Point Grey')

        # mona runf always in B with PG camera
        global_PVs['Cam1_AttributeFile'].put('monaDetectorAttributes.xml', wait=True) 
        global_PVs['HDF1_XMLFileName'].put('monaLayout.xml', wait=True) 

        global_PVs['Cam1_ImageMode'].put('Multiple')
        global_PVs['Cam1_ArrayCallbacks'].put('Enable')
        #global_PVs['Image1_Callbacks'].put('Enable')
        global_PVs['Cam1_AcquirePeriod'].put(float(variableDict['ExposureTime']))
        global_PVs['Cam1_AcquireTime'].put(float(variableDict['ExposureTime']))
        # if we are using external shutter then set the exposure time
        global_PVs['Cam1_FrameRateOnOff'].put(0)

        wait_time_sec = int(variableDict['ExposureTime']) + 5
        global_PVs['Cam1_TriggerMode'].put('Overlapped', wait=True) #Ext. Standard
        global_PVs['Cam1_NumImages'].put(1, wait=True)
        global_PVs['Cam1_Acquire'].put(DetectorAcquire)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)
        global_PVs['Cam1_SoftwareTrigger'].put(1)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec)
        global_PVs['Cam1_Acquire'].put(DetectorAcquire)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)
        global_PVs['Cam1_SoftwareTrigger'].put(1)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec)
        print('  *** setup Point Grey: Done!')

    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):
        # setup Point Grey PV's
        print(' ')
        print('  *** setup FLIR camera')

        if variableDict['Station'] == '2-BM-A':
            global_PVs['Cam1_AttributeFile'].put('flir2bmaDetectorAttributes.xml')
            global_PVs['HDF1_XMLFileName'].put('flir2bmaLayout.xml')           
        else: # Mona (B-station)
            global_PVs['Cam1_AttributeFile'].put('flir2bmbDetectorAttributes.xml', wait=True) 
            global_PVs['HDF1_XMLFileName'].put('flir2bmbLayout.xml', wait=True) 

        global_PVs['Cam1_Acquire'].put(DetectorIdle)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, 2)

        # #########################################################################
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)
        global_PVs['Cam1_TriggerSource'].put('Line2', wait=True)
        global_PVs['Cam1_TriggerOverlap'].put('ReadOut', wait=True)
        global_PVs['Cam1_ExposureMode'].put('Timed', wait=True)
        global_PVs['Cam1_TriggerSelector'].put('FrameStart', wait=True)
        global_PVs['Cam1_TriggerActivation'].put('RisingEdge', wait=True)

        # #########################################################################

        global_PVs['Cam1_ImageMode'].put('Multiple')
        global_PVs['Cam1_ArrayCallbacks'].put('Enable')
        #global_PVs['Image1_Callbacks'].put('Enable')
        #global_PVs['Cam1_AcquirePeriod'].put(float(variableDict['ExposureTime']))
        global_PVs['Cam1_FrameRateOnOff'].put(0)
        global_PVs['Cam1_AcquireTimeAuto'].put('Off')

        global_PVs['Cam1_AcquireTime'].put(float(variableDict['ExposureTime']))
        # if we are using external shutter then set the exposure time

        wait_time_sec = int(variableDict['ExposureTime']) + 5

        global_PVs['Cam1_TriggerMode'].put('On', wait=True)
        print('  *** setup FLIR camera: Done!')
    
    else:
        print ('Detector %s is not defined' % variableDict['IOC_Prefix'])
        return
    if fname is not None:
        setup_hdf_writer(global_PVs, variableDict, fname)

def setup_frame_type(global_PVs, variableDict):
    global_PVs['Cam1_FrameTypeZRST'].put('/exchange/data')
    global_PVs['Cam1_FrameTypeONST'].put('/exchange/data_dark')
    global_PVs['Cam1_FrameTypeTWST'].put('/exchange/data_white')


def setup_hdf_writer(global_PVs, variableDict, fname=None):

    if (variableDict['IOC_Prefix'] == '2bmbPG3:') or (variableDict['IOC_Prefix'] == '2bmbSP1:'):   
        # setup Point Grey hdf writer PV's
        print('  ')
        print('  *** setup hdf_writer')
        setup_frame_type(global_PVs, variableDict)
        if variableDict.has_key('Recursive_Filter_Enabled'):
            if variableDict['Recursive_Filter_Enabled'] == True:
                print('    *** Recursive Filter Enabled')
                global_PVs['Proc1_Enable_Background'].put('Disable', wait=True)
                global_PVs['Proc1_Enable_FlatField'].put('Disable', wait=True)
                global_PVs['Proc1_Enable_Offset_Scale'].put('Disable', wait=True)
                global_PVs['Proc1_Enable_Low_Clip'].put('Disable', wait=True)
                global_PVs['Proc1_Enable_High_Clip'].put('Disable', wait=True)

                global_PVs['Proc1_Callbacks'].put('Enable', wait=True)
                global_PVs['Proc1_Filter_Enable'].put('Enable', wait=True)
                global_PVs['HDF1_ArrayPort'].put('PROC1', wait=True)
                global_PVs['Proc1_Filter_Type'].put(Recursive_Filter_Type, wait=True)
                global_PVs['Proc1_Num_Filter'].put(int(variableDict['Recursive_Filter_N_Images']), wait=True)
                global_PVs['Proc1_Reset_Filter'].put(1, wait=True)
                global_PVs['Proc1_AutoReset_Filter'].put('Yes', wait=True)
                global_PVs['Proc1_Filter_Callbacks'].put('Array N only', wait=True)
                print('    *** Recursive Filter Enabled: Done!')
            else:
                global_PVs['Proc1_Filter_Enable'].put('Disable')
                global_PVs['HDF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
        else:
            global_PVs['Proc1_Filter_Enable'].put('Disable')
            print("1:done")
            global_PVs['HDF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
            print("2:Done")
        global_PVs['HDF1_AutoSave'].put('Yes')
        global_PVs['HDF1_DeleteDriverFile'].put('No')
        global_PVs['HDF1_EnableCallbacks'].put('Enable')
        global_PVs['HDF1_BlockingCallbacks'].put('No')

        # if (variableDict['Recursive_Filter_Enabled'] == False):
        #     variableDict['Recursive_Filter_N_Images'] = 1

        totalProj = ((int(variableDict['Projections'] / image_factor(global_PVs, variableDict))) + int(variableDict['NumDarkImages']) + \
                        int(variableDict['NumWhiteImages']))

        global_PVs['HDF1_NumCapture'].put(totalProj)
        global_PVs['HDF1_FileWriteMode'].put(str(variableDict['FileWriteMode']), wait=True)
        if fname is not None:
            global_PVs['HDF1_FileName'].put(fname)
        global_PVs['HDF1_Capture'].put(1)
        wait_pv(global_PVs['HDF1_Capture'], 1)
        print('  *** setup hdf_writer: Done!')
    else:
        print ('Detector %s is not defined' % variableDict['IOC_Prefix'])
        return


def image_factor(global_PVs, variableDict):

    if (variableDict['Recursive_Filter_Enabled'] == False):
        factor = 1 
    else:
        factor = variableDict['Recursive_Filter_N_Images']
    return int(factor)


def pgAcquisition(global_PVs, variableDict):
    theta = []
    # Estimate the time needed for the flyscan
    flyscan_time_estimate = (float(variableDict['Projections']) * (float(variableDict['ExposureTime']) + \
                      float(variableDict['CCD_Readout'])) ) + 30
    print(' ')
    print('  *** Fly Scan Time Estimate: %f minutes' % (flyscan_time_estimate/60.))

    global_PVs['Cam1_FrameType'].put(FrameTypeData, wait=True)
    time.sleep(2)    

    if (variableDict['SampleInOutVertical']):
        global_PVs['Motor_SampleY'].put(str(variableDict['SampleYIn']), wait=True, timeout=1000.0)                    
    else:
        global_PVs['Motor_SampleX'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0) 
        if (variableDict['UseFurnace']):
            global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYIn']), wait=True, timeout=1000.0)

    # global_PVs['Cam1_AcquireTime'].put(float(variableDict['ExposureTime']) )

    if (variableDict['Recursive_Filter_Enabled'] == False):
        variableDict['Recursive_Filter_N_Images'] = 1

    num_images = int(variableDict['Projections'])  * image_factor(global_PVs, variableDict)   
    global_PVs['Cam1_NumImages'].put(num_images, wait=True)


    # Set detectors
    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):   
        global_PVs['Cam1_TriggerMode'].put('Overlapped', wait=True)
    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):
        global_PVs['Cam1_TriggerMode'].put('On', wait=True)

    # start acquiring
    global_PVs['Cam1_Acquire'].put(DetectorAcquire)
    wait_pv(global_PVs['Cam1_Acquire'], 1)

    print(' ')
    print('  *** Fly Scan: Start!')
    global_PVs['Fly_Run'].put(1, wait=True)
    # wait for acquire to finish 
    wait_pv(global_PVs['Fly_Run'], 0)

    # if the fly scan wait times out we should call done on the detector
#    if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, flyscan_time_estimate) == False:
    if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, 5) == False:
        global_PVs['Cam1_Acquire'].put(DetectorIdle)
        #  got error here once when missing 100s of frames: wait_pv( 2bmbSP1:cam1:Acquire 0 5 ) reached max timeout. Return False
    
    print('  *** Fly Scan: Done!')
    # Set trigger mode to internal for post dark and white
    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):   
        global_PVs['Cam1_TriggerMode'].put('Internal')
    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)


    theta = global_PVs['Theta_Array'].get(count=int(variableDict['Projections']))
    if (image_factor(global_PVs, variableDict) > 1):
        theta = np.mean(theta.reshape(-1, image_factor(global_PVs, variableDict)), axis=1)
    
    return theta
            

def pgAcquireFlat(global_PVs, variableDict):
    print('      *** White Fields')
    if (variableDict['SampleMoveEnabled']):
        print('      *** *** Move Sample Out')
        if (variableDict['SampleInOutVertical']):
            global_PVs['Motor_SampleY'].put(str(variableDict['SampleYOut']), wait=True, timeout=1000.0)                
        else:
            if (variableDict['UseFurnace']):
                global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYOut']), wait=True, timeout=1000.0)
            global_PVs['Motor_SampleX'].put(str(variableDict['SampleXOut']), wait=True, timeout=1000.0)
    else:
        print('      *** *** Sample Stack is Frozen')

    global_PVs['Cam1_ImageMode'].put('Multiple')
    global_PVs['Cam1_FrameType'].put(FrameTypeWhite)             

    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):
        global_PVs['Cam1_TriggerMode'].put('Overlapped')
    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)
        
    # Set detectors
    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):   
        wait_time_sec = int(variableDict['ExposureTime']) + 5
        global_PVs['Cam1_NumImages'].put(1)

        for i in range(int(variableDict['NumWhiteImages']) * image_factor(global_PVs, variableDict)):
            global_PVs['Cam1_Acquire'].put(DetectorAcquire)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)
            time.sleep(0.1)
            global_PVs['Cam1_SoftwareTrigger'].put(1, wait=True)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec)
            time.sleep(0.1)

    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):
        wait_time_sec = float(variableDict['NumWhiteImages']) * float(variableDict['ExposureTime']) + 60.0
        global_PVs['Cam1_NumImages'].put(int(variableDict['NumWhiteImages']))
        global_PVs['Cam1_Acquire'].put(DetectorAcquire, wait=True, timeout=1000.0)
        time.sleep(0.1)
        if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec) == False: # adjust wait time
            global_PVs['Cam1_Acquire'].put(DetectorIdle)
    if (variableDict['SampleMoveEnabled']):
        print('      *** *** Move Sample In')
        if (variableDict['SampleInOutVertical']):
            global_PVs['Motor_SampleY'].put(str(variableDict['SampleYIn']), wait=True, timeout=1000.0)                
        else:
            if (variableDict['UseFurnace']):
                global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYIn']), wait=True, timeout=1000.0)
            global_PVs['Motor_SampleX'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0)
    else:
        print('      *** *** Sample Stack is Frozen')

    print('      *** White Fields: Done!')


def checkclose_hdf(global_PVs, variableDict):

    buffer_queue = global_PVs['HDF1_QueueSize'].get() - global_PVs['HDF1_QueueFree'].get()
    wait_on_hdd = 10
    # wait_on_hdd = buffer_queue / 55.0 + 10
    # wait_on_hdd = (global_PVs['HDF1_QueueSize'].get() - global_PVs['HDF1_QueueFree'].get()) / 55.0 + 10
    print('  *** Buffer Queue (frames): ', buffer_queue)
    print('  *** Wait HDD (s): ', wait_on_hdd)
    if wait_pv(global_PVs["HDF1_Capture_RBV"], 0, wait_on_hdd) == False: # needs to wait for HDF plugin queue to dump to disk
        global_PVs["HDF1_Capture"].put(0)
        print('  *** File was not closed => forced to close')
        print('      *** before ', global_PVs["HDF1_Capture_RBV"].get())
        wait_pv(global_PVs["HDF1_Capture_RBV"], 0, 5) 
        print('      *** after ', global_PVs["HDF1_Capture_RBV"].get())
        if (global_PVs["HDF1_Capture_RBV"].get() == 1):
            print ('  *** ERROR HDF FILE DID NOT CLOSE; add_theta will fail')


def pgAcquireDark(global_PVs, variableDict):
    print("      *** Dark Fields") 
    global_PVs['Cam1_ImageMode'].put('Multiple')
    global_PVs['Cam1_FrameType'].put(FrameTypeDark)             

    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):
        global_PVs['Cam1_TriggerMode'].put('Overlapped')
    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)
        
    # Set detectors
    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):   

        wait_time_sec = int(variableDict['ExposureTime']) + 5
        global_PVs['Cam1_NumImages'].put(1)

        for i in range(int(variableDict['NumDarkImages']) * image_factor(global_PVs, variableDict)):
            global_PVs['Cam1_Acquire'].put(DetectorAcquire)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)
            time.sleep(0.1)
            global_PVs['Cam1_SoftwareTrigger'].put(1, wait=True)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec)
            time.sleep(0.1)
        wait_pv(global_PVs["HDF1_Capture_RBV"], 0, 600)

    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):
        wait_time_sec = float(variableDict['NumDarkImages']) * float(variableDict['ExposureTime']) + 60.0
        global_PVs['Cam1_NumImages'].put(int(variableDict['NumDarkImages']))
        #ver 2
        global_PVs['Cam1_Acquire'].put(DetectorAcquire, wait=True, timeout=1000.0)
        time.sleep(0.1)
        if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec) == False: # adjust wait time
            global_PVs['Cam1_Acquire'].put(DetectorIdle)

    print('      *** Dark Fields: Done!')
    print('  *** Acquisition: Done!')        


def move_sample_in(global_PVs, variableDict):
    print(' ')
    print('  *** horizontal move_sample_in')
    global_PVs['Motor_SampleX'].put(float(variableDict['SampleXIn']), wait=True)
    if wait_pv(global_PVs['Motor_SampleX'], float(variableDict['SampleXIn']), 60) == False:
        print('Motor_SampleX did not move in properly')
        print (global_PVs['Motor_SampleX'].get())
        print('\r\n\r\n')
    print('  *** horizontal move_sample_in: Done!')


def move_sample_out(global_PVs, variableDict):
    print(' ')
    print('  *** horizontal move_sample_out')
    global_PVs['Motor_SampleX'].put(float(variableDict['SampleXOut']), wait=True)
    if False == wait_pv(global_PVs['Motor_SampleX'], float(variableDict['SampleXOut']), 60):
        print('Motor_SampleX did not move out properly')
        print (global_PVs['Motor_SampleX'].get())
        print('\r\n\r\n')
    print('  *** horizontal move_sample_out: Done!')


def open_shutters(global_PVs, variableDict):
    print(' ')
    print('  *** open_shutters')
    if TESTING:
        print('  *** WARNING: testing mode - shutters are deactivted during the scans !!!!')
    else:
        if variableDict['Station'] == '2-BM-A':
        # Use Shutter A
            if ShutterAisFast:
                global_PVs['ShutterA_Open'].put(1, wait=True)
                wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Open_Value)
                time.sleep(3)                
                global_PVs['Fast_Shutter'].put(1, wait=True)
                time.sleep(1)
                print('  *** open_shutter fast: Done!')
            else:
                global_PVs['ShutterA_Open'].put(1, wait=True)
                wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Open_Value)
                time.sleep(3)
                print('  *** open_shutter A: Done!')
        elif variableDict['Station'] == '2-BM-B':
            global_PVs['ShutterB_Open'].put(1, wait=True)
            wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Open_Value)
            print('  *** open_shutter B: Done!')
 

def close_shutters(global_PVs, variableDict):
    print(' ')
    print('  *** close_shutters')
    if TESTING:
        print('  *** WARNING: testing mode - shutters are deactivted during the scans !!!!')
    else:
        if variableDict['Station'] == '2-BM-A':
            if ShutterAisFast:
                global_PVs['Fast_Shutter'].put(0, wait=True)
                time.sleep(1)
                print('  *** close_shutter fast: Done!')
            else:
                global_PVs['ShutterA_Close'].put(1, wait=True)
                wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
                print('  *** close_shutter A: Done!')
        elif variableDict['Station'] == '2-BM-B':
            global_PVs['ShutterB_Close'].put(1, wait=True)
            wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Close_Value)
            print('  *** close_shutter B: Done!')


def add_theta(global_PVs, variableDict, theta_arr):
    print(' ')
    print('  *** add_theta')
    
    fullname = global_PVs['HDF1_FullFileName_RBV'].get(as_string=True)
    try:
        hdf_f = h5py.File(fullname, mode='a')
        if theta_arr is not None:
            theta_ds = hdf_f.create_dataset('/exchange/theta', (len(theta_arr),))
            theta_ds[:] = theta_arr[:]
        hdf_f.close()
        print('  *** add_theta: Done!')
    except:
        traceback.print_exc(file=sys.stdout)
        print('  *** add_theta: Failed accessing:', fullname)

def setPSO(global_PVs, variableDict):

    acclTime = 1.0 * variableDict['SlewSpeed']/variableDict['AcclRot']
    scanDelta = ((float(variableDict['SampleRotEnd']) - float(variableDict['SampleRotStart']))) / ((float(variableDict['Projections'])) * float(image_factor(global_PVs, variableDict)))

    print('  *** *** start_pos',float(variableDict['SampleRotStart']))
    print('  *** *** end pos', float(variableDict['SampleRotEnd']))

    global_PVs['Fly_StartPos'].put(float(variableDict['SampleRotStart']), wait=True)
    global_PVs['Fly_EndPos'].put(float(variableDict['SampleRotEnd']), wait=True)
    global_PVs['Fly_SlewSpeed'].put(variableDict['SlewSpeed'], wait=True)
    global_PVs['Fly_ScanDelta'].put(scanDelta, wait=True)
    time.sleep(3.0)
    calc_num_proj = global_PVs['Fly_Calc_Projections'].get()

    if calc_num_proj == None:
        print('  *** ***   *** *** Error getting fly calculated number of proj/APSshare/anaconda/x86_64/binections!')
        calc_num_proj = global_PVs['Fly_Calc_Projections'].get()
        print ("##############", calc_num_proj, variableDict['Projections'])
    if calc_num_proj != int(variableDict['Projections']):
        print('  *** ***  *** *** Updating number of projections from:', variableDict['Projections'], ' to: ', int(calc_num_proj))
        variableDict['Projections'] = int(calc_num_proj)
    print('  *** *** Number of projections: ', int(variableDict['Projections']))
    print('  *** *** Fly calc triggers: ', int(calc_num_proj))
    global_PVs['Fly_ScanControl'].put('Standard')

    print(' ')
    print('  *** Taxi before starting capture')
    global_PVs['Fly_Taxi'].put(1, wait=True)
    wait_pv(global_PVs['Fly_Taxi'], 0)
    print('  *** Taxi before starting capture: Done!')


def calc_blur_pixel(global_PVs, variableDict):
    """
    Calculate the blur error (pixel units) due to a rotary stage fly scan motion durng the exposure.
    
    Parameters
    ----------
    variableDict['ExposureTime']: float
        Detector exposure time
    variableDict['CCD_Readout'] : float
        Detector read out time
    variableDict[''roiSizeX''] : int
        Detector X size
    variableDict['SampleRotEnd'] : float
        Tomographic scan angle end
    variableDict['SampleRotStart'] : float
        Tomographic scan angle start
    variableDict[''Projections'] : int
        Numember of projections

    Returns
    -------
    float
        Blur error in pixel. For good quality reconstruction this should be < 0.2 pixel.
    """

    angular_range =  variableDict['SampleRotEnd'] -  variableDict['SampleRotStart']
    angular_step = angular_range/variableDict['Projections']
    scan_time = variableDict['Projections'] * (variableDict['ExposureTime'] + variableDict['CCD_Readout'])
    rot_speed = angular_range / scan_time
    frame_rate = variableDict['Projections'] / scan_time
    blur_delta = variableDict['ExposureTime'] * rot_speed
 
   
    mid_detector = global_PVs['Cam1_MaxSizeX_RBV'].get() / 2.0
    blur_pixel = mid_detector * (1 - np.cos(blur_delta * np.pi /180.))

    print(' ')
    print('  *** Calc blur pixel')
    print("  *** *** Total # of proj: ", variableDict['Projections'])
    print("  *** *** Exposure Time: ", variableDict['ExposureTime'], "s")
    print("  *** *** Readout Time: ", variableDict['CCD_Readout'], "s")
    print("  *** *** Angular Range: ", angular_range, "degrees")
    print("  *** *** Camera X size: ", global_PVs['Cam1_SizeX'].get())
    print(' ')
    print("  *** *** *** *** Angular Step: ", angular_step, "degrees")   
    print("  *** *** *** *** Scan Time: ", scan_time ,"s") 
    print("  *** *** *** *** Rot Speed: ", rot_speed, "degrees/s")
    print("  *** *** *** *** Frame Rate: ", frame_rate, "fps")
    print("  *** *** *** *** Max Blur: ", blur_pixel, "pixels")
    print('  *** Calc blur pixel: Done!')
    
    return blur_pixel, rot_speed, scan_time
