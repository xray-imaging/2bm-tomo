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

from tomo2bm import log

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



# def update_variable_dict(variableDict):
#     argDic = {}
#     if len(sys.argv) > 1:
#         strArgv = sys.argv[1]
#         argDic = json.loads(strArgv)
#     # for k,v in argDic.items(): # python 3
#     for k,v in argDic.iteritems():
#         variableDict[k] = v


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
                    log.error('  *** ERROR: DROPPED IMAGES ***')
                    log.error('  *** wait_pv(%s, %d, %5.2f reached max timeout. Return False' % (pv.pvname, wait_val, max_timeout_sec))


                    return False
            time.sleep(.01)
        else:
            return True


def init_general_PVs(global_PVs, params):

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

    if params.station == '2-BM-A':
        log.info('*** Running in station A:')
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
        
    elif params.station == '2-BM-B':   
        log.info('*** Running in station B:')
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
        log.error('*** %s is not a valid station' % params.station)

    # detector pv's
    if ((params.camera_ioc_prefix == '2bmbPG3:') or (params.camera_ioc_prefix == '2bmbSP1:')): 
    
        # init Point Grey PV's
        # general PV's
        global_PVs['Cam1_SerialNumber'] = PV(params.camera_ioc_prefix + 'cam1:SerialNumber_RBV')
        global_PVs['Cam1_ImageMode'] = PV(params.camera_ioc_prefix + 'cam1:ImageMode')
        global_PVs['Cam1_ArrayCallbacks'] = PV(params.camera_ioc_prefix + 'cam1:ArrayCallbacks')
        global_PVs['Cam1_AcquirePeriod'] = PV(params.camera_ioc_prefix + 'cam1:AcquirePeriod')
        global_PVs['Cam1_TriggerMode'] = PV(params.camera_ioc_prefix + 'cam1:TriggerMode')
        global_PVs['Cam1_SoftwareTrigger'] = PV(params.camera_ioc_prefix + 'cam1:SoftwareTrigger')  ### ask Mark is this is exposed in the medm screen
        global_PVs['Cam1_AcquireTime'] = PV(params.camera_ioc_prefix + 'cam1:AcquireTime')
        global_PVs['Cam1_FrameType'] = PV(params.camera_ioc_prefix + 'cam1:FrameType')
        global_PVs['Cam1_NumImages'] = PV(params.camera_ioc_prefix + 'cam1:NumImages')
        global_PVs['Cam1_Acquire'] = PV(params.camera_ioc_prefix + 'cam1:Acquire')
        global_PVs['Cam1_AttributeFile'] = PV(params.camera_ioc_prefix + 'cam1:NDAttributesFile')
        global_PVs['Cam1_FrameTypeZRST'] = PV(params.camera_ioc_prefix + 'cam1:FrameType.ZRST')
        global_PVs['Cam1_FrameTypeONST'] = PV(params.camera_ioc_prefix + 'cam1:FrameType.ONST')
        global_PVs['Cam1_FrameTypeTWST'] = PV(params.camera_ioc_prefix + 'cam1:FrameType.TWST')
        global_PVs['Cam1_Display'] = PV(params.camera_ioc_prefix + 'image1:EnableCallbacks')

        global_PVs['Cam1_SizeX'] = PV(params.camera_ioc_prefix + 'cam1:SizeX')
        global_PVs['Cam1_SizeY'] = PV(params.camera_ioc_prefix + 'cam1:SizeY')
        global_PVs['Cam1_SizeX_RBV'] = PV(params.camera_ioc_prefix + 'cam1:SizeX_RBV')
        global_PVs['Cam1_SizeY_RBV'] = PV(params.camera_ioc_prefix + 'cam1:SizeY_RBV')
        global_PVs['Cam1_MaxSizeX_RBV'] = PV(params.camera_ioc_prefix + 'cam1:MaxSizeX_RBV')
        global_PVs['Cam1_MaxSizeY_RBV'] = PV(params.camera_ioc_prefix + 'cam1:MaxSizeY_RBV')
        global_PVs['Cam1PixelFormat_RBV'] = PV(params.camera_ioc_prefix + 'cam1:PixelFormat_RBV')

        global_PVs['Cam1_Image'] = PV(params.camera_ioc_prefix + 'image1:ArrayData')

        # hdf5 writer PV's
        global_PVs['HDF1_AutoSave'] = PV(params.camera_ioc_prefix + 'HDF1:AutoSave')
        global_PVs['HDF1_DeleteDriverFile'] = PV(params.camera_ioc_prefix + 'HDF1:DeleteDriverFile')
        global_PVs['HDF1_EnableCallbacks'] = PV(params.camera_ioc_prefix + 'HDF1:EnableCallbacks')
        global_PVs['HDF1_BlockingCallbacks'] = PV(params.camera_ioc_prefix + 'HDF1:BlockingCallbacks')
        global_PVs['HDF1_FileWriteMode'] = PV(params.camera_ioc_prefix + 'HDF1:FileWriteMode')
        global_PVs['HDF1_NumCapture'] = PV(params.camera_ioc_prefix + 'HDF1:NumCapture')
        global_PVs['HDF1_Capture'] = PV(params.camera_ioc_prefix + 'HDF1:Capture')
        global_PVs['HDF1_Capture_RBV'] = PV(params.camera_ioc_prefix + 'HDF1:Capture_RBV')
        global_PVs['HDF1_FileName'] = PV(params.camera_ioc_prefix + 'HDF1:FileName')
        global_PVs['HDF1_FullFileName_RBV'] = PV(params.camera_ioc_prefix + 'HDF1:FullFileName_RBV')
        global_PVs['HDF1_FileTemplate'] = PV(params.camera_ioc_prefix + 'HDF1:FileTemplate')
        global_PVs['HDF1_ArrayPort'] = PV(params.camera_ioc_prefix + 'HDF1:NDArrayPort')
        global_PVs['HDF1_FileNumber'] = PV(params.camera_ioc_prefix + 'HDF1:FileNumber')
        global_PVs['HDF1_XMLFileName'] = PV(params.camera_ioc_prefix + 'HDF1:XMLFileName')

        global_PVs['HDF1_QueueSize'] = PV(params.camera_ioc_prefix + 'HDF1:QueueSize')
        global_PVs['HDF1_QueueFree'] = PV(params.camera_ioc_prefix + 'HDF1:QueueFree')
                                                                      
        # proc1 PV's
        global_PVs['Image1_Callbacks'] = PV(params.camera_ioc_prefix + 'image1:EnableCallbacks')
        global_PVs['Proc1_Callbacks'] = PV(params.camera_ioc_prefix + 'Proc1:EnableCallbacks')
        global_PVs['Proc1_ArrayPort'] = PV(params.camera_ioc_prefix + 'Proc1:NDArrayPort')
        global_PVs['Proc1_Filter_Enable'] = PV(params.camera_ioc_prefix + 'Proc1:EnableFilter')
        global_PVs['Proc1_Filter_Type'] = PV(params.camera_ioc_prefix + 'Proc1:FilterType')
        global_PVs['Proc1_Num_Filter'] = PV(params.camera_ioc_prefix + 'Proc1:NumFilter')
        global_PVs['Proc1_Reset_Filter'] = PV(params.camera_ioc_prefix + 'Proc1:ResetFilter')
        global_PVs['Proc1_AutoReset_Filter'] = PV(params.camera_ioc_prefix + 'Proc1:AutoResetFilter')
        global_PVs['Proc1_Filter_Callbacks'] = PV(params.camera_ioc_prefix + 'Proc1:FilterCallbacks')       

        global_PVs['Proc1_Enable_Background'] = PV(params.camera_ioc_prefix + 'Proc1:EnableBackground')
        global_PVs['Proc1_Enable_FlatField'] = PV(params.camera_ioc_prefix + 'Proc1:EnableFlatField')
        global_PVs['Proc1_Enable_Offset_Scale'] = PV(params.camera_ioc_prefix + 'Proc1:EnableOffsetScale')
        global_PVs['Proc1_Enable_Low_Clip'] = PV(params.camera_ioc_prefix + 'Proc1:EnableLowClip')
        global_PVs['Proc1_Enable_High_Clip'] = PV(params.camera_ioc_prefix + 'Proc1:EnableHighClip')


    if (params.camera_ioc_prefix == '2bmbPG3:'):
        global_PVs['Cam1_FrameRateOnOff'] = PV(params.camera_ioc_prefix + 'cam1:FrameRateOnOff')

    elif (params.camera_ioc_prefix == '2bmbSP1:'):
        global_PVs['Cam1_AcquireTimeAuto'] = PV(params.camera_ioc_prefix + 'cam1:AcquireTimeAuto')
        global_PVs['Cam1_FrameRateOnOff'] = PV(params.camera_ioc_prefix + 'cam1:FrameRateEnable')

        global_PVs['Cam1_TriggerSource'] = PV(params.camera_ioc_prefix + 'cam1:TriggerSource')
        global_PVs['Cam1_TriggerOverlap'] = PV(params.camera_ioc_prefix + 'cam1:TriggerOverlap')
        global_PVs['Cam1_ExposureMode'] = PV(params.camera_ioc_prefix + 'cam1:ExposureMode')
        global_PVs['Cam1_TriggerSelector'] = PV(params.camera_ioc_prefix + 'cam1:TriggerSelector')
        global_PVs['Cam1_TriggerActivation'] = PV(params.camera_ioc_prefix + 'cam1:TriggerActivation')
    
    else:
        log.error('Detector %s is not defined' % params.camera_ioc_prefix)
        return            

    return global_PVs

def stop_scan(global_PVs, params):
        log.info(' ')
        log.error('  *** Stopping the scan: PLEASE WAIT')
        global_PVs['Motor_SampleRot_Stop'].put(1)
        global_PVs['HDF1_Capture'].put(0)
        wait_pv(global_PVs['HDF1_Capture'], 0)
        pgInit(global_PVs, params)
        log.error('  *** Stopping scan: Done!')
        ##pgInit(global_PVs, params)


def open_shutters(global_PVs, params):
    log.info(' ')
    log.info('  *** open_shutters')
    if TESTING:
        # Logger(variableDict['LogFileName']).info('\x1b[2;30;43m' + '  *** WARNING: testing mode - shutters are deactivated during the scans !!!!' + '\x1b[0m')
        log.warning('  *** testing mode - shutters are deactivated during the scans !!!!')
    else:
        if params.station == '2-BM-A':
        # Use Shutter A
            if ShutterAisFast:
                global_PVs['ShutterA_Open'].put(1, wait=True)
                wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Open_Value)
                time.sleep(3)                
                global_PVs['Fast_Shutter'].put(1, wait=True)
                time.sleep(1)
                log.info('  *** open_shutter fast: Done!')
            else:
                global_PVs['ShutterA_Open'].put(1, wait=True)
                wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Open_Value)
                time.sleep(3)
                log.info('  *** open_shutter A: Done!')
        elif params.station == '2-BM-B':
            global_PVs['ShutterB_Open'].put(1, wait=True)
            wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Open_Value)
            log.info('  *** open_shutter B: Done!')
 

def close_shutters(global_PVs, params):
    log.info(' ')
    log.info('  *** close_shutters')
    if TESTING:
        # Logger(variableDict['LogFileName']).info('\x1b[2;30;43m' + '  *** WARNING: testing mode - shutters are deactivated during the scans !!!!' + '\x1b[0m')
        log.warning('  *** testing mode - shutters are deactivated during the scans !!!!')
    else:
        if params.station == '2-BM-A':
            if ShutterAisFast:
                global_PVs['Fast_Shutter'].put(0, wait=True)
                time.sleep(1)
                log.info('  *** close_shutter fast: Done!')
            else:
                global_PVs['ShutterA_Close'].put(1, wait=True)
                wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
                log.info('  *** close_shutter A: Done!')
        elif params.station == '2-BM-B':
            global_PVs['ShutterB_Close'].put(1, wait=True)
            wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Close_Value)
            log.info('  *** close_shutter B: Done!')


def setPSO(global_PVs, params):

    acclTime = 1.0 * params.slew_speed/params.accl_rot
    scanDelta = abs(((float(params.sample_rotation_end) - float(params.sample_rotation_start))) / ((float(params.num_projections)) * float(image_factor(global_PVs, params))))

    log.info('  *** *** start_pos %f' % float(params.sample_rotation_start))
    log.info('  *** *** end pos %f' % float(params.sample_rotation_end))

    global_PVs['Fly_StartPos'].put(float(params.sample_rotation_start), wait=True)
    global_PVs['Fly_EndPos'].put(float(params.sample_rotation_end), wait=True)
    global_PVs['Fly_SlewSpeed'].put(params.slew_speed, wait=True)
    global_PVs['Fly_ScanDelta'].put(scanDelta, wait=True)
    time.sleep(3.0)

    calc_num_proj = global_PVs['Fly_Calc_Projections'].get()
    
    if calc_num_proj == None:
        log.error('  *** *** Error getting fly calculated number of projections!')
        calc_num_proj = global_PVs['Fly_Calc_Projections'].get()
        log.error('  *** *** Using %s instead of %s' % (calc_num_proj, params.num_projections))
    if calc_num_proj != int(params.num_projections):
        log.warning('  *** *** Changing number of projections from: %s to: %s' % (params.num_projections, int(calc_num_proj)))
        params.num_projections = int(calc_num_proj)
    log.info('  *** *** Number of projections: %d' % int(params.num_projections))
    log.info('  *** *** Fly calc triggers: %d' % int(calc_num_proj))
    global_PVs['Fly_ScanControl'].put('Standard')

    log.info(' ')
    log.info('  *** Taxi before starting capture')
    global_PVs['Fly_Taxi'].put(1, wait=True)
    wait_pv(global_PVs['Fly_Taxi'], 0)
    log.info('  *** Taxi before starting capture: Done!')

########################################################################

def pgInit(global_PVs, params):
    if (params.camera_ioc_prefix == '2bmbPG3:'):   
        log.info('  *** init Point Grey camera')
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
        log.info('  *** init Point Grey camera: Done!')
    elif (params.camera_ioc_prefix == '2bmbSP1:'):   
        log.info(' ')                
        log.info('  *** init FLIR camera')
        log.info('  *** *** set detector to idle')
        global_PVs['Cam1_Acquire'].put(DetectorIdle)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, 2)
        log.info('  *** *** set detector to idle:  Done')
        # global_PVs['Proc1_Filter_Callbacks'].put( 'Every array', wait=True) # commented out to test if crash (ValueError: invalid literal for int() with base 0: 'Single') still occurs
        time.sleep(2) 
        log.info('  *** *** set trigger mode to Off')
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)    # 
        log.info('  *** *** set trigger mode to Off: done')
        time.sleep(7) 
        log.info('  *** *** set image mode to single')
        global_PVs['Cam1_ImageMode'].put('Single', wait=True)   # here is where it crashes with (ValueError: invalid literal for int() with base 0: 'Single') Added 7 s delay before
        log.info('  *** *** set image mode to single: done')
        log.info('  *** *** set cam display to 1')
        global_PVs['Cam1_Display'].put(1)
        log.info('  *** *** set cam display to 1: done')
        log.info('  *** *** set cam acquire')
        global_PVs['Cam1_Acquire'].put(DetectorAcquire)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2) 
        log.info('  *** *** set cam acquire: done')
        if params.station == '2-BM-A':
            global_PVs['Cam1_AttributeFile'].put('flir2bmaDetectorAttributes.xml')
            global_PVs['HDF1_XMLFileName'].put('flir2bmaLayout.xml')           
        else: # Mona (B-station)
            global_PVs['Cam1_AttributeFile'].put('flir2bmbDetectorAttributes.xml', wait=True) 
            global_PVs['HDF1_XMLFileName'].put('flir2bmbLayout.xml', wait=True) 
        log.info('  *** init FLIR camera: Done!')


def pgSet(global_PVs, params, fname=None):

    # Set detectors
    if (params.camera_ioc_prefix == '2bmbPG3:'):   
        # setup Point Grey PV's
        log.info(' ')
        log.info('  *** setup Point Grey')

        # mona runf always in B with PG camera
        global_PVs['Cam1_AttributeFile'].put('monaDetectorAttributes.xml', wait=True) 
        global_PVs['HDF1_XMLFileName'].put('monaLayout.xml', wait=True) 

        global_PVs['Cam1_ImageMode'].put('Multiple')
        global_PVs['Cam1_ArrayCallbacks'].put('Enable')
        #global_PVs['Image1_Callbacks'].put('Enable')
        global_PVs['Cam1_AcquirePeriod'].put(float(params.exposure_time))
        global_PVs['Cam1_AcquireTime'].put(float(params.exposure_time))
        # if we are using external shutter then set the exposure time
        global_PVs['Cam1_FrameRateOnOff'].put(0)

        wait_time_sec = int(params.exposure_time) + 5
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
        log.info('  *** setup Point Grey: Done!')

    elif (params.camera_ioc_prefix == '2bmbSP1:'):
        # setup Point Grey PV's
        log.info(' ')
        log.info('  *** setup FLIR camera')

        if params.station == '2-BM-A':
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
        #global_PVs['Cam1_AcquirePeriod'].put(float(params.exposure_time))
        global_PVs['Cam1_FrameRateOnOff'].put(0)
        global_PVs['Cam1_AcquireTimeAuto'].put('Off')

        global_PVs['Cam1_AcquireTime'].put(float(params.exposure_time))
        # if we are using external shutter then set the exposure time

        wait_time_sec = int(params.exposure_time) + 5

        global_PVs['Cam1_TriggerMode'].put('On', wait=True)
        log.info('  *** setup FLIR camera: Done!')
    
    else:
        log.error('Detector %s is not defined' % params.camera_ioc_prefix)
        return
    if fname is not None:
        setup_hdf_writer(global_PVs, params, fname)

def setup_frame_type(global_PVs, params):
    global_PVs['Cam1_FrameTypeZRST'].put('/exchange/data')
    global_PVs['Cam1_FrameTypeONST'].put('/exchange/data_dark')
    global_PVs['Cam1_FrameTypeTWST'].put('/exchange/data_white')


def setup_hdf_writer(global_PVs, params, fname=None):

    if (params.camera_ioc_prefix == '2bmbPG3:') or (params.camera_ioc_prefix == '2bmbSP1:'):   
        # setup Point Grey hdf writer PV's
        log.info('  ')
        log.info('  *** setup hdf_writer')
        setup_frame_type(global_PVs, params)
        if params.recursive_filter == True:
            log.info('    *** Recursive Filter Enabled')
            global_PVs['Proc1_Enable_Background'].put('Disable', wait=True)
            global_PVs['Proc1_Enable_FlatField'].put('Disable', wait=True)
            global_PVs['Proc1_Enable_Offset_Scale'].put('Disable', wait=True)
            global_PVs['Proc1_Enable_Low_Clip'].put('Disable', wait=True)
            global_PVs['Proc1_Enable_High_Clip'].put('Disable', wait=True)

            global_PVs['Proc1_Callbacks'].put('Enable', wait=True)
            global_PVs['Proc1_Filter_Enable'].put('Enable', wait=True)
            global_PVs['HDF1_ArrayPort'].put('PROC1', wait=True)
            global_PVs['Proc1_Filter_Type'].put(Recursive_Filter_Type, wait=True)
            global_PVs['Proc1_Num_Filter'].put(int(params.recursive_filter_n_images), wait=True)
            global_PVs['Proc1_Reset_Filter'].put(1, wait=True)
            global_PVs['Proc1_AutoReset_Filter'].put('Yes', wait=True)
            global_PVs['Proc1_Filter_Callbacks'].put('Array N only', wait=True)
            log.info('    *** Recursive Filter Enabled: Done!')
        else:
            global_PVs['Proc1_Filter_Enable'].put('Disable')
            global_PVs['HDF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
        global_PVs['HDF1_AutoSave'].put('Yes')
        global_PVs['HDF1_DeleteDriverFile'].put('No')
        global_PVs['HDF1_EnableCallbacks'].put('Enable')
        global_PVs['HDF1_BlockingCallbacks'].put('No')

        # if (params.recursive_filter == False):
        #     params.recursive_filter_n_images = 1

        totalProj = ((int(params.num_projections / image_factor(global_PVs, params))) + int(params.num_dark_images) + \
                        int(params.num_white_images))

        global_PVs['HDF1_NumCapture'].put(totalProj)
        global_PVs['HDF1_FileWriteMode'].put(str(params.file_write_mode), wait=True)
        if fname is not None:
            global_PVs['HDF1_FileName'].put(str(fname), wait=True)
        global_PVs['HDF1_Capture'].put(1)
        wait_pv(global_PVs['HDF1_Capture'], 1)
        log.info('  *** setup hdf_writer: Done!')
    else:
        log.error('Detector %s is not defined' % params.camera_ioc_prefix)
        return


def image_factor(global_PVs, params):

    if (params.recursive_filter == False):
        factor = 1 
    else:
        factor = params.recursive_filter_n_images
    return int(factor)


def pgAcquisition(global_PVs, params):
    theta = []
    # Estimate the time needed for the flyscan
    flyscan_time_estimate = (float(params.num_projections) * (float(params.exposure_time) + \
                      float(params.ccd_readout)) ) + 30
    log.info(' ')
    log.info('  *** Fly Scan Time Estimate: %f minutes' % (flyscan_time_estimate/60.))

    global_PVs['Cam1_FrameType'].put(FrameTypeData, wait=True)
    time.sleep(2)    

    move_sample_in(global_PVs, params)
    
    # global_PVs['Cam1_AcquireTime'].put(float(params.exposure_time) )

    if (params.recursive_filter == False):
        params.recursive_filter_n_images = 1

    num_images = int(params.num_projections)  * image_factor(global_PVs, params)   
    global_PVs['Cam1_NumImages'].put(num_images, wait=True)


    # Set detectors
    if (params.camera_ioc_prefix == '2bmbPG3:'):   
        global_PVs['Cam1_TriggerMode'].put('Overlapped', wait=True)
    elif (params.camera_ioc_prefix == '2bmbSP1:'):
        global_PVs['Cam1_TriggerMode'].put('On', wait=True)

    # start acquiring
    global_PVs['Cam1_Acquire'].put(DetectorAcquire)
    wait_pv(global_PVs['Cam1_Acquire'], 1)

    log.info(' ')
    log.info('  *** Fly Scan: Start!')
    global_PVs['Fly_Run'].put(1, wait=True)
    # wait for acquire to finish 
    wait_pv(global_PVs['Fly_Run'], 0)

    # if the fly scan wait times out we should call done on the detector
#    if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, flyscan_time_estimate) == False:
    if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, 5) == False:
        global_PVs['Cam1_Acquire'].put(DetectorIdle)
        #  got error here once when missing 100s of frames: wait_pv( 2bmbSP1:cam1:Acquire 0 5 ) reached max timeout. Return False
    
    log.info('  *** Fly Scan: Done!')
    # Set trigger mode to internal for post dark and white
    if (params.camera_ioc_prefix == '2bmbPG3:'):   
        global_PVs['Cam1_TriggerMode'].put('Internal')
    elif (params.camera_ioc_prefix == '2bmbSP1:'):
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)


    theta = global_PVs['Theta_Array'].get(count=int(params.num_projections))
    if (image_factor(global_PVs, params) > 1):
        theta = np.mean(theta.reshape(-1, image_factor(global_PVs, params)), axis=1)
    
    return theta
            
#@@@@@@
# def move_sample_in(global_PVs, params):
#     log.info(' ')
#     log.info('  *** horizontal move_sample_out')
#     global_PVs['Motor_SampleX'].put(float(params.sample_x_out), wait=True)
#     if False == wait_pv(global_PVs['Motor_SampleX'], float(params.sample_x_out), 60):
#         log.error('Motor_SampleX did not move out properly')
#         log.error(global_PVs['Motor_SampleX'].get())
#     log.info('  *** horizontal move_sample_out: Done!')


# def move_sample_out(global_PVs, params):
#     log.info(' ')
#     log.info('  *** horizontal move_sample_out')
#     global_PVs['Motor_SampleX'].put(float(params.sample_x_out), wait=True)
#     if False == wait_pv(global_PVs['Motor_SampleX'], float(params.sample_x_out), 60):
#         log.error('Motor_SampleX did not move out properly')
#         log.error(global_PVs['Motor_SampleX'].get())
#     log.info('  *** horizontal move_sample_out: Done!')



def move_sample_out(global_PVs, params):
    log.info('      *** Sample out')
    if not (params.sample_move_freeze):
        if (params.sample_in_out_vertical):
            log.info('      *** *** Move Sample Out: Y')
            global_PVs['Motor_SampleY'].put(str(params.sample_out_position), wait=True, timeout=1000.0)                
            if wait_pv(global_PVs['Motor_SampleY'], float(params.sample_out_position), 60) == False:
                log.error('Motor_SampleY did not move in properly')
                log.error(global_PVs['Motor_SampleY'].get())
        else:
            if (params.use_furnace):
                log.info('      *** *** Move Furnace Out: Y')
                global_PVs['Motor_FurnaceY'].put(str(params.furnace_out_position), wait=True, timeout=1000.0)
                if wait_pv(global_PVs['Motor_FurnaceY'], float(params.furnace_out_position), 60) == False:
                    log.error('Motor_FurnaceY did not move in properly')
                    log.error(global_PVs['Motor_FurnaceY'].get())
            log.info('      *** *** Move Sample In: X')
            global_PVs['Motor_SampleX'].put(str(params.sample_out_position), wait=True, timeout=1000.0)
            if wait_pv(global_PVs['Motor_SampleX'], float(params.sample_out_position), 60) == False:
                log.error('Motor_SampleX did not move in properly')
                log.error(global_PVs['Motor_SampleX'].get())
    else:
        log.info('      *** *** Sample Stack is Frozen')


def move_sample_in(global_PVs, params):
    log.info('      *** Sample in')
    if not (params.sample_move_freeze):
        if (params.sample_in_out_vertical):
            log.info('      *** *** Move Sample In: Y')
            global_PVs['Motor_SampleY'].put(str(params.sample_in_position), wait=True, timeout=1000.0)                
            if wait_pv(global_PVs['Motor_SampleY'], float(params.sample_in_position), 60) == False:
                log.error('Motor_SampleY did not move in properly')
                log.error(global_PVs['Motor_SampleY'].get())
        else:
            log.info('      *** *** Move Sample In: X')
            global_PVs['Motor_SampleX'].put(str(params.sample_in_position), wait=True, timeout=1000.0)
            if wait_pv(global_PVs['Motor_SampleX'], float(params.sample_in_position), 60) == False:
                log.error('Motor_SampleX did not move in properly')
                log.error(global_PVs['Motor_SampleX'].get())
            if (params.use_furnace):
                log.info('      *** *** Move Furnace Out: Y')
                global_PVs['Motor_FurnaceY'].put(str(params.furnace_in_position), wait=True, timeout=1000.0)
                if wait_pv(global_PVs['Motor_FurnaceY'], float(params.furnace_in_position), 60) == False:
                    log.error('Motor_FurnaceY did not move in properly')
                    log.error(global_PVs['Motor_FurnaceY'].get())
    else:
        log.info('      *** *** Sample Stack is Frozen')


# def move_sample_in(global_PVs, params):
#     log.info(' ')
#     log.info('  *** horizontal move_sample_in')
#     global_PVs['Motor_SampleX'].put(float(params.sample_in_position), wait=True)
#     if wait_pv(global_PVs['Motor_SampleX'], float(params.sample_in_position), 60) == False:
#         log.error('Motor_SampleX did not move in properly')
#         log.error(global_PVs['Motor_SampleX'].get())
#     log.info('  *** horizontal move_sample_in: Done!')


def pgAcquireFlat(global_PVs, params):
    log.info('      *** White Fields')
    move_sample_out(global_PVs, params)
    
    global_PVs['Cam1_ImageMode'].put('Multiple')
    global_PVs['Cam1_FrameType'].put(FrameTypeWhite)             

    if (params.camera_ioc_prefix == '2bmbPG3:'):
        global_PVs['Cam1_TriggerMode'].put('Overlapped')
    elif (params.camera_ioc_prefix == '2bmbSP1:'):
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)
        
    # Set detectors
    if (params.camera_ioc_prefix == '2bmbPG3:'):   
        wait_time_sec = int(params.exposure_time) + 5
        global_PVs['Cam1_NumImages'].put(1)

        for i in range(int(params.num_white_images) * image_factor(global_PVs, params)):
            global_PVs['Cam1_Acquire'].put(DetectorAcquire)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)
            time.sleep(0.1)
            global_PVs['Cam1_SoftwareTrigger'].put(1, wait=True)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec)
            time.sleep(0.1)

    elif (params.camera_ioc_prefix == '2bmbSP1:'):
        wait_time_sec = float(params.num_white_images) * float(params.exposure_time) + 60.0
        global_PVs['Cam1_NumImages'].put(int(params.num_white_images))
        global_PVs['Cam1_Acquire'].put(DetectorAcquire, wait=True, timeout=5.0) # it was 1000.0

        # time.sleep(0.1)
        if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec) == False: # adjust wait time
            global_PVs['Cam1_Acquire'].put(DetectorIdle)
    
    move_sample_in(global_PVs, params)
    log.info('      *** White Fields: Done!')


def pgAcquireDark(global_PVs, params):
    log.info("      *** Dark Fields") 
    global_PVs['Cam1_ImageMode'].put('Multiple')
    global_PVs['Cam1_FrameType'].put(FrameTypeDark)             

    if (params.camera_ioc_prefix == '2bmbPG3:'):
        global_PVs['Cam1_TriggerMode'].put('Overlapped')
    elif (params.camera_ioc_prefix == '2bmbSP1:'):
        global_PVs['Cam1_TriggerMode'].put('Off', wait=True)
        
    # Set detectors
    if (params.camera_ioc_prefix == '2bmbPG3:'):   

        wait_time_sec = int(params.exposure_time) + 5
        global_PVs['Cam1_NumImages'].put(1)

        for i in range(int(params.num_dark_images) * image_factor(global_PVs, params)):
            global_PVs['Cam1_Acquire'].put(DetectorAcquire)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)
            time.sleep(0.1)
            global_PVs['Cam1_SoftwareTrigger'].put(1, wait=True)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec)
            time.sleep(0.1)
        wait_pv(global_PVs["HDF1_Capture_RBV"], 0, 600)

    elif (params.camera_ioc_prefix == '2bmbSP1:'):
        wait_time_sec = float(params.num_dark_images) * float(params.exposure_time) + 60.0
        global_PVs['Cam1_NumImages'].put(int(params.num_dark_images))
        #ver 2
        global_PVs['Cam1_Acquire'].put(DetectorAcquire, wait=True, timeout=5.0) # it was 1000.0
        # time.sleep(0.1)
        if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec) == False: # adjust wait time
            global_PVs['Cam1_Acquire'].put(DetectorIdle)

    log.info('      *** Dark Fields: Done!')
    log.info('  *** Acquisition: Done!')        





def checkclose_hdf(global_PVs, params):

    buffer_queue = global_PVs['HDF1_QueueSize'].get() - global_PVs['HDF1_QueueFree'].get()
    # wait_on_hdd = 10
    frate = 55.0
    wait_on_hdd = buffer_queue / frate + 10
    # wait_on_hdd = (global_PVs['HDF1_QueueSize'].get() - global_PVs['HDF1_QueueFree'].get()) / 55.0 + 10
    log.info('  *** Buffer Queue (frames): %d ' % buffer_queue)
    log.info('  *** Wait HDD (s): %f' % wait_on_hdd)
    if wait_pv(global_PVs["HDF1_Capture_RBV"], 0, wait_on_hdd) == False: # needs to wait for HDF plugin queue to dump to disk
        global_PVs["HDF1_Capture"].put(0)
        log.info('  *** File was not closed => forced to close')
        log.info('      *** before %d' % global_PVs["HDF1_Capture_RBV"].get())
        wait_pv(global_PVs["HDF1_Capture_RBV"], 0, 5) 
        log.info('      *** after %d' % global_PVs["HDF1_Capture_RBV"].get())
        if (global_PVs["HDF1_Capture_RBV"].get() == 1):
            log.error('  *** ERROR HDF FILE DID NOT CLOSE; add_theta will fail')


def add_theta(global_PVs, params, theta_arr):
    log.info(' ')
    log.info('  *** add_theta')
    
    fullname = global_PVs['HDF1_FullFileName_RBV'].get(as_string=True)
    try:
        hdf_f = h5py.File(fullname, mode='a')
        if theta_arr is not None:
            theta_ds = hdf_f.create_dataset('/exchange/theta', (len(theta_arr),))
            theta_ds[:] = theta_arr[:]
        hdf_f.close()
        log.info('  *** add_theta: Done!')
    except:
        traceback.print_exc(file=sys.stdout)
        log.info('  *** add_theta: Failed accessing: %s' % fullname)


#####################################################

def calc_blur_pixel(global_PVs, params):
    """
    Calculate the blur error (pixel units) due to a rotary stage fly scan motion durng the exposure.
    
    Parameters
    ----------
    params.exposure_time: float
        Detector exposure time
    params.ccd_readout : float
        Detector read out time
    variableDict[''roiSizeX''] : int
        Detector X size
    params.sample_rotation_end : float
        Tomographic scan angle end
    params.sample_rotation_start : float
        Tomographic scan angle start
    variableDict[''Projections'] : int
        Numember of projections

    Returns
    -------
    float
        Blur error in pixel. For good quality reconstruction this should be < 0.2 pixel.
    """

    angular_range =  params.sample_rotation_end -  params.sample_rotation_start
    angular_step = angular_range/params.num_projections
    scan_time = params.num_projections * (params.exposure_time + params.ccd_readout)
    rot_speed = angular_range / scan_time
    frame_rate = params.num_projections / scan_time
    blur_delta = params.exposure_time * rot_speed
 
   
    mid_detector = global_PVs['Cam1_MaxSizeX_RBV'].get() / 2.0
    blur_pixel = mid_detector * (1 - np.cos(blur_delta * np.pi /180.))

    log.info(' ')
    log.info('  *** Calc blur pixel')
    log.info("  *** *** Total # of proj: %s " % params.num_projections)
    log.info("  *** *** Exposure Time: %s s" % params.exposure_time)
    log.info("  *** *** Readout Time: %s s" % params.ccd_readout)
    log.info("  *** *** Angular Range: %s degrees" % angular_range)
    log.info("  *** *** Camera X size: %s " % global_PVs['Cam1_SizeX'].get())
    log.info(' ')
    log.info("  *** *** *** *** Angular Step: %f degrees" % angular_step)   
    log.info("  *** *** *** *** Scan Time: %f s" % scan_time) 
    log.info("  *** *** *** *** Rot Speed: %f degrees/s" % rot_speed)
    log.info("  *** *** *** *** Frame Rate: %f fps" % frame_rate)
    log.info("  *** *** *** *** Max Blur: %f pixels" % blur_pixel)
    log.info('  *** Calc blur pixel: Done!')
    
    return blur_pixel, rot_speed, scan_time

