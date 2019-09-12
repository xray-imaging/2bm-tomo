'''
    Tomo Lib for Sector 2-BM  using Point Grey Grasshooper3 or FLIR Oryx cameras
    
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
import logging
import numpy as np

import log_lib

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
    # for k,v in argDic.items(): # python 3
    for k,v in argDic.iteritems():
        variableDict[k] = v


def wait_pv(pv, wait_val, max_timeout_sec=-1):

    # wait on a pv to be a value until max_timeout (default forever)   
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
                    log_lib.error('  *** ERROR: DROPPED IMAGES ***')
                    log_lib.error('  *** wait_pv(%s, %d, %5.2f reached max timeout. Return False' % (pv.pvname, wait_val, max_timeout_sec))


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


    # Experimment Info
    global_PVs['Sample_Name'] = PV('2bmS1:ExpInfo:SampleName')

    global_PVs['User_Badge'] = PV('2bmS1:ExpInfo:UserBadge.VAL')
    global_PVs['User_Email'] = PV('2bmS1:ExpInfo:UserEmail.VAL')
    global_PVs['User_Institution'] = PV('2bmS1:ExpInfo:UserInstitution.VAL')
    global_PVs['Proposal_Number'] = PV('2bmS1:ExpInfo:ProposalNumber.VAL')
    global_PVs['Proposal_Title'] = PV('2bmS1:ExpInfo:ProposalTitle.VAL')
    global_PVs['Sample_Description'] = PV('2bmS1:ExpInfo:SampleDescription.VAL')
    global_PVs['User_Info_Update'] = PV('2bmS1:ExpInfo:UserInfoUpdate.VAL')
    global_PVs['Lens_Magnification'] = PV('2bmS1:ExpInfo:LensMagnification.VAL')
    global_PVs['Scintillator_Type'] = PV('2bmS1:ExpInfo:ScintillatorType.VAL')
    global_PVs['Filters'] = PV('2bmS1:ExpInfo:Filters.VAL')
    global_PVs['File_Name'] = PV('2bmS1:ExpInfo:FileName.VAL')
    global_PVs['Station'] = PV('2bmS1:ExpInfo:Station.VAL')
    global_PVs['Camera_IOC_Prefix'] = PV('2bmS1:ExpInfo:CameraIOCPrefix.VAL')
    global_PVs['Remote_Analysis_Dir'] = PV('2bmS1:ExpInfo:RemoteAnalysisDir.VAL')
    global_PVs['User_Last_Name'] = PV('2bmS1:ExpInfo:UserLastName.VAL')
    global_PVs['Experiment_Year_Month'] = PV('2bmS1:ExpInfo:ExperimentYearMonth.VAL')
    global_PVs['Use_Furnace'] = PV('2bmS1:ExpInfo:UseFurnace.VAL')
    global_PVs['White_Field_Motion'] = PV('2bmS1:ExpInfo:WhiteFieldMotion.VAL')
    global_PVs['Remote_Data_Trasfer'] = PV('2bmS1:ExpInfo:RemoteDataTrasfer.VAL')
    global_PVs['Scan_Type'] = PV('2bmS1:ExpInfo:ScanType.VAL')
    global_PVs['Num_Projections'] = PV('2bmS1:ExpInfo:NumProjections.VAL')
    global_PVs['Num_White_Images'] = PV('2bmS1:ExpInfo:NumWhiteImages.VAL')
    global_PVs['Num_Dark_Images'] = PV('2bmS1:ExpInfo:NumDarkImages.VAL')
    global_PVs['Scintillator_Thickness'] = PV('2bmS1:ExpInfo:ScintillatorThickness.VAL')
    global_PVs['Sample_Detector_Distance'] = PV('2bmS1:ExpInfo:SampleDetectorDistance.VAL')
    global_PVs['Sample_In_Position'] = PV('2bmS1:ExpInfo:SampleInPosition.VAL')
    global_PVs['Sample_Out_Position'] = PV('2bmS1:ExpInfo:SampleOutPosition.VAL')
    global_PVs['Sample_Rotation_Start'] = PV('2bmS1:ExpInfo:SampleRotationStart.VAL')
    global_PVs['Sample_Rotation_End'] = PV('2bmS1:ExpInfo:SampleRotationEnd.VAL')
    global_PVs['Furnace_In_Position'] = PV('2bmS1:ExpInfo:FurnaceInPosition.VAL')
    global_PVs['Furnace_Out_Position'] = PV('2bmS1:ExpInfo:FurnaceOutPosition.VAL')
    global_PVs['Sleep_Time'] = PV('2bmS1:ExpInfo:SleepTime.VAL')
    global_PVs['Vertical_Scan_Start'] = PV('2bmS1:ExpInfo:VerticalScanStart.VAL')
    global_PVs['Vertical_Scan_End'] = PV('2bmS1:ExpInfo:VerticalScanEnd.VAL')
    global_PVs['Vertical_Scan_Step_Size'] = PV('2bmS1:ExpInfo:VerticalScanStepSize.VAL')
    global_PVs['Horizontal_Scan_Start'] = PV('2bmS1:ExpInfo:HorizontalScanStart.VAL')
    global_PVs['Horizontal_Scan_End'] = PV('2bmS1:ExpInfo:HorizontalScanEnd.VAL')
    global_PVs['Horizontal_Scan_Step_Size'] = PV('2bmS1:ExpInfo:HorizontalScanStepSize.VAL')

    if variableDict['Station'] == '2-BM-A':
        log_lib.info('*** Running in station A:')
        # Set sample stack motor pv's:
        global_PVs['Motor_SampleX'] = PV('2bma:m49.VAL')
        global_PVs['Motor_SampleX_SET'] = PV('2bma:m49.SET')
        global_PVs['Motor_SampleY'] = PV('2bma:m20.VAL')
        global_PVs['Motor_SampleRot'] = PV('2bma:m82.VAL') # Aerotech ABR-250
        global_PVs['Motor_SampleRot_RBV'] = PV('2bma:m82.RBV') # Aerotech ABR-250
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
        global_PVs['Motor_Focus'] = PV('2bma:m41.VAL')
        global_PVs['Motor_Focus_Name'] = PV('2bma:m41.DESC')
        
    elif variableDict['Station'] == '2-BM-B':   
        log_lib.info('*** Running in station B:')
        # Sample stack motor pv's:
        global_PVs['Motor_SampleX'] = PV('2bmb:m63.VAL')
        global_PVs['Motor_SampleX_SET'] = PV('2bmb:m63.SET')
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
        log_lib.error('*** %s is not a valid station' % variableDict['Station'])

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
        log_lib.error('Detector %s is not defined' % variableDict['IOC_Prefix'])
        return            


def stop_scan(global_PVs, variableDict):
        log_lib.info(' ')
        log_lib.error('  *** Stopping the scan: PLEASE WAIT')
        global_PVs['Motor_SampleRot_Stop'].put(1)
        global_PVs['HDF1_Capture'].put(0)
        wait_pv(global_PVs['HDF1_Capture'], 0)
        pgInit(global_PVs, variableDict)
        log_lib.error('  *** Stopping scan: Done!')
        ##pgInit(global_PVs, variableDict)


def pgInit(global_PVs, variableDict):
    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):   
        log_lib.info('  *** init Point Grey camera')
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
        log_lib.info('  *** init Point Grey camera: Done!')
    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):   
        log_lib.info(' ')                
        log_lib.info('  *** init FLIR camera')
        log_lib.info('  *** *** set detector to idle')
        global_PVs['Cam1_Acquire'].put(DetectorIdle)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, 2)
        log_lib.info('  *** *** set detector to idle:  Done')
        # global_PVs['Proc1_Filter_Callbacks'].put( 'Every array', wait=True) # commented out to test if crash (ValueError: invalid literal for int() with base 0: 'Single') still occurs
        time.sleep(2) 
        log_lib.info('  *** *** set trigger mode to Off')
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)    # 
        log_lib.info('  *** *** set trigger mode to Off: done')
        time.sleep(7) 
        log_lib.info('  *** *** set image mode to single')
        global_PVs['Cam1_ImageMode'].put('Single', wait=True)   # here is where it crashes with (ValueError: invalid literal for int() with base 0: 'Single') Added 7 s delay before
        log_lib.info('  *** *** set image mode to single: done')
        log_lib.info('  *** *** set cam display to 1')
        global_PVs['Cam1_Display'].put(1)
        log_lib.info('  *** *** set cam display to 1: done')
        log_lib.info('  *** *** set cam acquire')
        global_PVs['Cam1_Acquire'].put(DetectorAcquire)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2) 
        log_lib.info('  *** *** set cam acquire: done')
        if variableDict['Station'] == '2-BM-A':
            global_PVs['Cam1_AttributeFile'].put('flir2bmaDetectorAttributes.xml')
            global_PVs['HDF1_XMLFileName'].put('flir2bmaLayout.xml')           
        else: # Mona (B-station)
            global_PVs['Cam1_AttributeFile'].put('flir2bmbDetectorAttributes.xml', wait=True) 
            global_PVs['HDF1_XMLFileName'].put('flir2bmbLayout.xml', wait=True) 
        log_lib.info('  *** init FLIR camera: Done!')


def pgSet(global_PVs, variableDict, fname=None):

    # Set detectors
    if (variableDict['IOC_Prefix'] == '2bmbPG3:'):   
        # setup Point Grey PV's
        log_lib.info(' ')
        log_lib.info('  *** setup Point Grey')

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
        log_lib.info('  *** setup Point Grey: Done!')

    elif (variableDict['IOC_Prefix'] == '2bmbSP1:'):
        # setup Point Grey PV's
        log_lib.info(' ')
        log_lib.info('  *** setup FLIR camera')

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
        log_lib.info('  *** setup FLIR camera: Done!')
    
    else:
        log_lib.error('Detector %s is not defined' % variableDict['IOC_Prefix'])
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
        log_lib.info('  ')
        log_lib.info('  *** setup hdf_writer')
        setup_frame_type(global_PVs, variableDict)
        if variableDict.has_key('Recursive_Filter_Enabled'):
            if variableDict['Recursive_Filter_Enabled'] == True:
                log_lib.info('    *** Recursive Filter Enabled')
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
                log_lib.info('    *** Recursive Filter Enabled: Done!')
            else:
                global_PVs['Proc1_Filter_Enable'].put('Disable')
                global_PVs['HDF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
        else:
            global_PVs['Proc1_Filter_Enable'].put('Disable')
            log_lib.info("1:done")
            global_PVs['HDF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
            log_lib.info("2:Done")
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
        log_lib.info('  *** setup hdf_writer: Done!')
    else:
        log_lib.error('Detector %s is not defined' % variableDict['IOC_Prefix'])
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
    log_lib.info(' ')
    log_lib.info('  *** Fly Scan Time Estimate: %f minutes' % (flyscan_time_estimate/60.))

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

    log_lib.info(' ')
    log_lib.info('  *** Fly Scan: Start!')
    global_PVs['Fly_Run'].put(1, wait=True)
    # wait for acquire to finish 
    wait_pv(global_PVs['Fly_Run'], 0)

    # if the fly scan wait times out we should call done on the detector
#    if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, flyscan_time_estimate) == False:
    if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, 5) == False:
        global_PVs['Cam1_Acquire'].put(DetectorIdle)
        #  got error here once when missing 100s of frames: wait_pv( 2bmbSP1:cam1:Acquire 0 5 ) reached max timeout. Return False
    
    log_lib.info('  *** Fly Scan: Done!')
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
    log_lib.info('      *** White Fields')
    if (variableDict['SampleMoveEnabled']):
        log_lib.info('      *** *** Move Sample Out')
        if (variableDict['SampleInOutVertical']):
            global_PVs['Motor_SampleY'].put(str(variableDict['SampleYOut']), wait=True, timeout=1000.0)                
        else:
            if (variableDict['UseFurnace']):
                global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYOut']), wait=True, timeout=1000.0)
            global_PVs['Motor_SampleX'].put(str(variableDict['SampleXOut']), wait=True, timeout=1000.0)
    else:
        log_lib.info('      *** *** Sample Stack is Frozen')

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
        global_PVs['Cam1_Acquire'].put(DetectorAcquire, wait=True, timeout=5.0) # it was 1000.0

        # time.sleep(0.1)
        if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec) == False: # adjust wait time
            global_PVs['Cam1_Acquire'].put(DetectorIdle)
    if (variableDict['SampleMoveEnabled']):
        log_lib.info('      *** *** Move Sample In')
        if (variableDict['SampleInOutVertical']):
            global_PVs['Motor_SampleY'].put(str(variableDict['SampleYIn']), wait=True, timeout=1000.0)                
        else:
            if (variableDict['UseFurnace']):
                global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYIn']), wait=True, timeout=1000.0)
            global_PVs['Motor_SampleX'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0)
    else:
        log_lib.info('      *** *** Sample Stack is Frozen')

    log_lib.info('      *** White Fields: Done!')


def checkclose_hdf(global_PVs, variableDict):

    buffer_queue = global_PVs['HDF1_QueueSize'].get() - global_PVs['HDF1_QueueFree'].get()
    # wait_on_hdd = 10
    frate = 55.0
    wait_on_hdd = buffer_queue / frate + 10
    # wait_on_hdd = (global_PVs['HDF1_QueueSize'].get() - global_PVs['HDF1_QueueFree'].get()) / 55.0 + 10
    log_lib.info('  *** Buffer Queue (frames): %d ' % buffer_queue)
    log_lib.info('  *** Wait HDD (s): %f' % wait_on_hdd)
    if wait_pv(global_PVs["HDF1_Capture_RBV"], 0, wait_on_hdd) == False: # needs to wait for HDF plugin queue to dump to disk
        global_PVs["HDF1_Capture"].put(0)
        log_lib.info('  *** File was not closed => forced to close')
        log_lib.info('      *** before %d' % global_PVs["HDF1_Capture_RBV"].get())
        wait_pv(global_PVs["HDF1_Capture_RBV"], 0, 5) 
        log_lib.info('      *** after %d' % global_PVs["HDF1_Capture_RBV"].get())
        if (global_PVs["HDF1_Capture_RBV"].get() == 1):
            log_lib.error('  *** ERROR HDF FILE DID NOT CLOSE; add_theta will fail')


def pgAcquireDark(global_PVs, variableDict):
    log_lib.info("      *** Dark Fields") 
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
        global_PVs['Cam1_Acquire'].put(DetectorAcquire, wait=True, timeout=5.0) # it was 1000.0
        # time.sleep(0.1)
        if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec) == False: # adjust wait time
            global_PVs['Cam1_Acquire'].put(DetectorIdle)

    log_lib.info('      *** Dark Fields: Done!')
    log_lib.info('  *** Acquisition: Done!')        


def move_sample_in(global_PVs, variableDict):
    log_lib.info(' ')
    log_lib.info('  *** horizontal move_sample_in')
    global_PVs['Motor_SampleX'].put(float(variableDict['SampleXIn']), wait=True)
    if wait_pv(global_PVs['Motor_SampleX'], float(variableDict['SampleXIn']), 60) == False:
        log_lib.error('Motor_SampleX did not move in properly')
        log_lib.error(global_PVs['Motor_SampleX'].get())
    log_lib.info('  *** horizontal move_sample_in: Done!')


def move_sample_out(global_PVs, variableDict):
    log_lib.info(' ')
    log_lib.info('  *** horizontal move_sample_out')
    global_PVs['Motor_SampleX'].put(float(variableDict['SampleXOut']), wait=True)
    if False == wait_pv(global_PVs['Motor_SampleX'], float(variableDict['SampleXOut']), 60):
        log_lib.error('Motor_SampleX did not move out properly')
        log_lib.error(global_PVs['Motor_SampleX'].get())
    log_lib.info('  *** horizontal move_sample_out: Done!')


def open_shutters(global_PVs, variableDict):
    log_lib.info(' ')
    log_lib.info('  *** open_shutters')
    if TESTING:
        # Logger(variableDict['LogFileName']).info('\x1b[2;30;43m' + '  *** WARNING: testing mode - shutters are deactivated during the scans !!!!' + '\x1b[0m')
        log_lib.warning('  *** testing mode - shutters are deactivated during the scans !!!!')
    else:
        if variableDict['Station'] == '2-BM-A':
        # Use Shutter A
            if ShutterAisFast:
                global_PVs['ShutterA_Open'].put(1, wait=True)
                wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Open_Value)
                time.sleep(3)                
                global_PVs['Fast_Shutter'].put(1, wait=True)
                time.sleep(1)
                log_lib.info('  *** open_shutter fast: Done!')
            else:
                global_PVs['ShutterA_Open'].put(1, wait=True)
                wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Open_Value)
                time.sleep(3)
                log_lib.info('  *** open_shutter A: Done!')
        elif variableDict['Station'] == '2-BM-B':
            global_PVs['ShutterB_Open'].put(1, wait=True)
            wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Open_Value)
            log_lib.info('  *** open_shutter B: Done!')
 

def close_shutters(global_PVs, variableDict):
    log_lib.info(' ')
    log_lib.info('  *** close_shutters')
    if TESTING:
        # Logger(variableDict['LogFileName']).info('\x1b[2;30;43m' + '  *** WARNING: testing mode - shutters are deactivated during the scans !!!!' + '\x1b[0m')
        log_lib.warning('  *** testing mode - shutters are deactivated during the scans !!!!')
    else:
        if variableDict['Station'] == '2-BM-A':
            if ShutterAisFast:
                global_PVs['Fast_Shutter'].put(0, wait=True)
                time.sleep(1)
                log_lib.info('  *** close_shutter fast: Done!')
            else:
                global_PVs['ShutterA_Close'].put(1, wait=True)
                wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
                log_lib.info('  *** close_shutter A: Done!')
        elif variableDict['Station'] == '2-BM-B':
            global_PVs['ShutterB_Close'].put(1, wait=True)
            wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Close_Value)
            log_lib.info('  *** close_shutter B: Done!')


def add_theta(global_PVs, variableDict, theta_arr):
    log_lib.info(' ')
    log_lib.info('  *** add_theta')
    
    fullname = global_PVs['HDF1_FullFileName_RBV'].get(as_string=True)
    try:
        hdf_f = h5py.File(fullname, mode='a')
        if theta_arr is not None:
            theta_ds = hdf_f.create_dataset('/exchange/theta', (len(theta_arr),))
            theta_ds[:] = theta_arr[:]
        hdf_f.close()
        log_lib.info('  *** add_theta: Done!')
    except:
        traceback.print_exc(file=sys.stdout)
        log_lib.info('  *** add_theta: Failed accessing:', fullname)

def setPSO(global_PVs, variableDict):

    acclTime = 1.0 * variableDict['SlewSpeed']/variableDict['AcclRot']
    scanDelta = abs(((float(variableDict['SampleRotEnd']) - float(variableDict['SampleRotStart']))) / ((float(variableDict['Projections'])) * float(image_factor(global_PVs, variableDict))))

    log_lib.info('  *** *** start_pos %f' % float(variableDict['SampleRotStart']))
    log_lib.info('  *** *** end pos %f' % float(variableDict['SampleRotEnd']))

    global_PVs['Fly_StartPos'].put(float(variableDict['SampleRotStart']), wait=True)
    global_PVs['Fly_EndPos'].put(float(variableDict['SampleRotEnd']), wait=True)
    global_PVs['Fly_SlewSpeed'].put(variableDict['SlewSpeed'], wait=True)
    global_PVs['Fly_ScanDelta'].put(scanDelta, wait=True)
    time.sleep(3.0)

    calc_num_proj = global_PVs['Fly_Calc_Projections'].get()
    
    if calc_num_proj == None:
        log_lib.error('  *** *** Error getting fly calculated number of projections!')
        calc_num_proj = global_PVs['Fly_Calc_Projections'].get()
        log_lib.error('  *** *** Using %s instead of %s' % (calc_num_proj, variableDict['Projections']))
    if calc_num_proj != int(variableDict['Projections']):
        log_lib.warning('  *** *** Changing number of projections from: %s to: %s' % (variableDict['Projections'], int(calc_num_proj)))
        variableDict['Projections'] = int(calc_num_proj)
    log_lib.info('  *** *** Number of projections: %d' % int(variableDict['Projections']))
    log_lib.info('  *** *** Fly calc triggers: %d' % int(calc_num_proj))
    global_PVs['Fly_ScanControl'].put('Standard')

    log_lib.info(' ')
    log_lib.info('  *** Taxi before starting capture')
    global_PVs['Fly_Taxi'].put(1, wait=True)
    wait_pv(global_PVs['Fly_Taxi'], 0)
    log_lib.info('  *** Taxi before starting capture: Done!')


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

    log_lib.info(' ')
    log_lib.info('  *** Calc blur pixel')
    log_lib.info("  *** *** Total # of proj: %s " % variableDict['Projections'])
    log_lib.info("  *** *** Exposure Time: %s s" % variableDict['ExposureTime'])
    log_lib.info("  *** *** Readout Time: %s s" % variableDict['CCD_Readout'])
    log_lib.info("  *** *** Angular Range: %s degrees" % angular_range)
    log_lib.info("  *** *** Camera X size: %s " % global_PVs['Cam1_SizeX'].get())
    log_lib.info(' ')
    log_lib.info("  *** *** *** *** Angular Step: %f degrees" % angular_step)   
    log_lib.info("  *** *** *** *** Scan Time: %f s" % scan_time) 
    log_lib.info("  *** *** *** *** Rot Speed: %f degrees/s" % rot_speed)
    log_lib.info("  *** *** *** *** Frame Rate: %f fps" % frame_rate)
    log_lib.info("  *** *** *** *** Max Blur: %f pixels" % blur_pixel)
    log_lib.info('  *** Calc blur pixel: Done!')
    
    return blur_pixel, rot_speed, scan_time


# def find_nearest(array, value):
#     array = np.asarray(array)
#     idx = (np.abs(array - value)).argmin()
#     return array[idx]


# def change2White():
#     log_lib.info(' ')
#     log_lib.info('  *** change2white')
#     log_lib.info('    *** closing A shutter')
#     global_PVs['ShutterA_Close'].put(1, wait=True)
#     wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
# # #    epics.caput(BL+":m33.VAL",107.8, wait=False, timeout=1000.0)                
#     # log_lib.info('    *** closing A shutter: Done!')

#     log_lib.info('    *** moving Filters')
#     global_PVs['Filters'].put(0, wait=True)
#     log_lib.info('    *** moving Mirror')
#     global_PVs['Mirr_Ang'].put(0, wait=True)
#     time.sleep(1) 
#     global_PVs['Mirr_YAvg'].put(-4, wait=True)
#     time.sleep(1) 
#     log_lib.info('    *** moving DMM X')                                          
#     global_PVs['DMM_USX'].put(50, wait=False)
#     global_PVs['DMM_DSX'].put(50, wait=True)
#     time.sleep(3)                
#     log_lib.info('    *** moving DMM Y')
#     global_PVs['DMM_USY_OB'].put(-16, wait=False)
#     global_PVs['DMM_USY_IB'].put(-16, wait=False)
#     global_PVs['DMM_DSY'].put(-16, wait=True)
#     time.sleep(3) 
                                 
# #     epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)    
#     log_lib.info('    *** moving XIA Slits')
#     global_PVs['XIASlit'].put(-1.65, wait=True)
#     log_lib.info('  *** change2white: Done!')
                    

# def change2Mono():
#     log_lib.info(' ')
#     log_lib.info('  *** change2mono')
#     log_lib.info('    *** closing shutter')
#     global_PVs['ShutterA_Close'].put(1, wait=True)
#     wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)

# # #    epics.caput(BL+":m33.VAL",121, wait=False, timeout=1000.0)                    
#     log_lib.info('    *** moving Filters')
#     global_PVs['Filters'].put(0, wait=True)
#     log_lib.info('    *** moving Mirror')
#     global_PVs['Mirr_YAvg'].put(0, wait=True)
#     time.sleep(1) 
#     global_PVs['Mirr_Ang'].put(2.657, wait=True)
#     time.sleep(1) 

#     log_lib.info('    *** moving DMM Y')
#     global_PVs['DMM_USY_OB'].put(-0.1, wait=False)
#     global_PVs['DMM_USY_IB'].put(-0.1, wait=False)
#     global_PVs['DMM_DSY'].put(-0.1, wait=True)
#     time.sleep(3) 
                                 
#     log_lib.info('    *** moving DMM X')                                          
#     global_PVs['DMM_USX'].put(81.5, wait=False)
#     global_PVs['DMM_DSX'].put(81.5, wait=True)
#     time.sleep(3)                
# #     epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)    
#     log_lib.info('    *** moving XIA Slits')
#     global_PVs['XIASlit'].put(30.35, wait=True)
#     log_lib.info('  *** change2mono: Done!')
               

# def change2Pink(ang=2.657):

#     Mirr_Ang_list = np.array([1.500,1.800,2.000,2.100,2.657])

#     angle_calibrated = find_nearest(Mirr_Ang_list, ang)
#     log_lib.info(' ')
#     log_lib.info('   *** Angle entered is %s rad, the closest calibrate angle is %s' % (ang, angle_calibrated))

#     Mirr_YAvg_list = np.array([-0.1,0.0,0.0,0.0,0.0])

#     DMM_USY_OB_list = np.array([-10,-10,-10,-10,-10])
#     DMM_USY_IB_list = np.array([-10,-10,-10,-10,-10])
#     DMM_DSY_list = np.array([-10,-10,-10,-10,-10])

#     DMM_USX_list = np.array([50,50,50,50,50])
#     DMM_DSX_list = np.array([50,50,50,50,50])

#     XIASlit_list = np.array([8.75,11.75,13.75,14.75,18.75])    

#     Slit1Hcenter_list = np.array([4.85,4.85,7.5,7.5,7.2])

#     Filter_list = np.array([0,0,0,0,0])

#     idx = np.where(Mirr_Ang_list==angle_calibrated)                
#     if idx[0].size == 0:
#         log_lib.info('     *** ERROR: there is no specified calibrated calibrate in the calibrated angle lookup table. please choose a calibrated angle.')
#         return    0                            

#     Mirr_Ang = Mirr_Ang_list[idx[0][0]] 
#     Mirr_YAvg = Mirr_YAvg_list[idx[0][0]]

#     DMM_USY_OB = DMM_USY_OB_list[idx[0][0]] 
#     DMM_USY_IB = DMM_USY_IB_list[idx[0][0]]
#     DMM_DSY = DMM_DSY_list[idx[0][0]]

#     DMM_USX = DMM_USX_list[idx[0][0]]
#     DMM_DSX = DMM_DSX_list[idx[0][0]]

#     XIASlit = XIASlit_list[idx[0][0]]          
#     Slit1Hcenter = Slit1Hcenter_list[idx[0][0]] 

#     Filter = Filter_list[idx[0][0]]

#     log_lib.info('   *** Angle is set at %s rad' % angle_calibrated)                
#     log_lib.info('     *** Moving Stages ...')                

#     log_lib.info('     *** Filter %s ' % Filter)
#     log_lib.info('     *** Mirr_YAvg %s mm' % Mirr_YAvg)
#     log_lib.info('     *** Mirr_Ang %s rad' % Mirr_Ang)
    
#     log_lib.info('     *** DMM_USX %s mm' % DMM_USX)
#     log_lib.info('     *** DMM_DSX %s mm' % DMM_DSX)

#     log_lib.info('     *** DMM_USY_OB %s mm' % DMM_USY_OB) 
#     log_lib.info('     *** DMM_USY_IB %s mm' % DMM_USY_IB)
#     log_lib.info('     *** DMM_DSY %s mm' % DMM_DSY)

#     log_lib.info('     *** Slit1Hcenter %s mm' % Slit1Hcenter)          
#     log_lib.info('     *** XIASlit %s mm' % XIASlit)          

#     log_lib.info(' ')
#     log_lib.info('  *** change2pink')
# #    log_lib.info('    *** closing shutter')
# #    global_PVs['ShutterA_Close'].put(1, wait=True)
# #    wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
# #    log_lib.info('    *** moving Filters')
# #    global_PVs['Filters'].put(Filter, wait=True)
# #    log_lib.info('    *** moving Mirror')
# #    global_PVs['Mirr_YAvg'].put(Mirr_YAvg, wait=True)
# #    time.sleep(1) 
# #    global_PVs['Mirr_Ang'].put(Mirr_YAvg, wait=True)
# #    time.sleep(1) 
# #    log_lib.info('    *** moving DMM X')                                          
# #    global_PVs['DMM_USX'].put(DMM_USX, wait=False)
# #    global_PVs['DMM_DSX'].put(DMM_DSX, wait=True)
# #    time.sleep(3)                
# #    log_lib.info('    *** moving DMM Y')
# #    global_PVs['DMM_USY_OB'].put(DMM_USY_OB, wait=False)
# #    global_PVs['DMM_USY_IB'].put(DMM_USY_IB, wait=False)
# #    global_PVs['DMM_DSY'].put(DMM_DSY, wait=True)
# #    time.sleep(3) 
# #         epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)    
# #    log_lib.info('    *** moving XIA Slits')
# #    global_PVs['XIASlit'].put(XIASlit, wait=True)
#     log_lib.info('  *** change2pink: Done!')


# def setEnergy(energy = 24.9):

#     caliEng_list = np.array([55.00, 50.00, 45.00, 40.00, 35.00, 31.00, 27.40, 24.90, 22.70, 21.10, 20.20, 18.90, 17.60, 16.80, 16.00, 15.00, 14.40])

#     energy_calibrated = find_nearest(caliEng_list, energy)
#     log_lib.info(' ')
#     log_lib.info('   *** Energy entered is %s keV, the closest calibrate energy is %s' % (energy, energy_calibrated))

#     Mirr_Ang_list = np.array([1.200,1.500,1.500,1.500,2.000,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657])
#     Mirr_YAvg_list = np.array([-0.2,-0.2,-0.2,-0.2,-0.2,0.0,0.0,-0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])

#     DMM_USY_OB_list = np.array([-5.1,-5.1,-5.1,-5.1,-3.8,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1])
#     DMM_USY_IB_list = np.array([-5.1,-5.1,-5.1,-5.1,-3.8,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1])  
#     DMM_DSY_list = np.array([-5.1,-5.1,-5.1,-5.1,-3.7,-0.1,-0.1,-0.2,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1]) 

#     USArm_list =   np.array([0.95,  1.00,  1.05,  1.10,  1.25,  1.10,  1.15,  1.20,  1.25,  1.30,  1.35,  1.40,  1.45,  1.50,  1.55,  1.60,  1.65])    
#     DSArm_list =  np.array([ 0.973, 1.022, 1.072, 1.124, 1.2745,1.121, 1.169, 1.2235,1.271, 1.3225,1.373, 1.4165,1.472, 1.5165,1.568, 1.6195,1.67])

#     M2Y_list =     np.array([11.63, 12.58, 13.38, 13.93, 15.57, 12.07, 13.71, 14.37, 15.57, 15.67, 17.04, 17.67, 18.89, 19.47, 20.57, 21.27, 22.27]) 
#     DMM_USX_list = np.array([27.5,27.5,27.5,27.5,27.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5])
#     DMM_DSX_list = np.array([27.5,27.5,27.5,27.5,27.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5])
#     XIASlit_list = np.array([21.45, 24.05, 25.05, 23.35, 26.35, 28.35, 29.35, 30.35, 31.35, 32.35, 33.35, 34.35, 34.35, 52.35, 53.35, 54.35, 51.35])    
    
#     idx = np.where(caliEng_list==energy_calibrated)                
#     if idx[0].size == 0:
#         log_lib.info('     *** ERROR: there is no specified energy_calibrated in the energy_calibrated lookup table. please choose a calibrated energy_calibrated.')
#         return    0                            

#     Mirr_Ang = Mirr_Ang_list[idx[0][0]] 
#     Mirr_YAvg = Mirr_YAvg_list[idx[0][0]]

#     DMM_USY_OB = DMM_USY_OB_list[idx[0][0]] 
#     DMM_USY_IB = DMM_USY_IB_list[idx[0][0]]
#     DMM_DSY = DMM_DSY_list[idx[0][0]]

#     USArm = USArm_list[idx[0][0]]                
#     DSArm = DSArm_list[idx[0][0]]

#     M2Y = M2Y_list[idx[0][0]]
#     DMM_USX = DMM_USX_list[idx[0][0]]
#     DMM_DSX = DMM_DSX_list[idx[0][0]]
#     XIASlit = XIASlit_list[idx[0][0]]          

#     log_lib.info('   *** Energy is set at %s keV' % energy_calibrated)                
#     log_lib.info('      *** Moving Stages ...')                


#     log_lib.info('      *** Mirr_Ang %s rad' % Mirr_Ang)
#     log_lib.info('      *** Mirr_YAvg %s mm' % Mirr_YAvg)
    
#     log_lib.info('      *** DMM_USY_OB %s mm' % DMM_USY_OB) 
#     log_lib.info('      *** DMM_USY_IB %s mm' % DMM_USY_IB)
#     log_lib.info('      *** DMM_DSY %s mm' % DMM_DSY)

#     log_lib.info('      *** USArm %s deg' % USArm)              
#     log_lib.info('      *** DSArm %s deg' % DSArm)

#     log_lib.info('      *** M2Y %s mm' % M2Y)
#     log_lib.info('      *** DMM_USX %s mm' % DMM_USX)
#     log_lib.info('      *** DMM_DSX %s mm' % DMM_DSX)
#     log_lib.info('      *** XIASlit %s mm' % XIASlit)          

#     log_lib.info(' ')
#     log_lib.info('  *** setEnergy')
#     # log_lib.info('    *** closing shutter')
#     # global_PVs['ShutterA_Close'].put(1, wait=True)
#     # wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
#     # change2Mono()                
#     # log_lib.info('    *** moving filter)
#     # if energy < 20.0:
#     #     global_PVs['Filters'].put(4, wait=True, timeout=1000.0)
#     # else:                                
#     #     global_PVs['Filters'].put(0, wait=True, timeout=1000.0)

#     # log_lib.info('    *** moving Mirror')
#     # global_PVs['Mirr_Ang'].put(Mirr_Ang, wait=False, timeout=1000.0) 
#     # global_PVs['Mirr_YAvg'].put(Mirr_YAvg, wait=False, timeout=1000.0) 
#     # log_lib.info('    *** moving DMM Y')
#     # global_PVs['DMM_USY_OB'].put(DMM_USY_OB, wait=False, timeout=1000.0) 
#     # global_PVs['DMM_USY_IB'].put(DMM_USY_IB, wait=False, timeout=1000.0) 
#     # global_PVs['DMM_DSY'].put(DMM_DSY, wait=False, timeout=1000.0) 

#     # log_lib.info('    *** moving DMM US/DS Arms')
#     # global_PVs['USArm'].put(USArm, wait=False, timeout=1000.0)
#     # global_PVs['DSArm'].put(DSArm, wait=True, timeout=1000.0)
#     # time.sleep(3)
#     # log_lib.info('    *** moving DMM M2Y')
#     # global_PVs['M2Y'].put(M2Y, wait=True, timeout=1000.0)
#     # log_lib.info('    *** moving DMM X')
#     # global_PVs['DMM_USX'].put(DMM_USX, wait=False, timeout=1000.0)
#     # global_PVs['DMM_DSX'].put(DMM_DSX, wait=True, timeout=1000.0)
#     # global_PVs['XIASlit'].put(XIASlit, wait=True, timeout=1000.0)             
#     log_lib.info('  *** setEnergy: Done!')
#     return energy_calibrated
 

