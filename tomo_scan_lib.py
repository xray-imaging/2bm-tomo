'''
    Tomo Scan Lib for Sector 2-BM
    
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

ShutterA_Open_Value = 1
ShutterA_Close_Value = 0
ShutterB_Open_Value = 1
ShutterB_Close_Value = 0
FrameTypeData = 0
FrameTypeDark = 1
FrameTypeWhite = 2
DetectorIdle = 0
DetectorAcquire = 1
UseShutterA = 0
UseShutterB = 1
TOMO = False # True = station A in use; False = station B in use
EPSILON = 0.1
'''
TESTING_MODE = False

if TESTING_MODE == True:
    UseShutterA = 0
    UseShutterB = 0
'''
PG_Trigger_External_Trigger = 1 # Important for the Point Grey (continuous mode as clock issues)
Recursive_Filter_Type = 'RecursiveAve'

if UseShutterA == 0 and UseShutterB == 0:
    print('### WARNING: shutters are deactivted during the scans !!!!')


def update_variable_dict(variableDict):
    argDic = {}
    if len(sys.argv) > 1:
        strArgv = sys.argv[1]
        argDic = json.loads(strArgv)
    print ('orig variable dict', variableDict)
    for k,v in argDic.iteritems():
        variableDict[k] = v
    print ('new variable dict', variableDict)


#wait on a pv to be a value until max_timeout (default forever)
def wait_pv(pv, wait_val, max_timeout_sec=-1):
    print ('wait_pv(', pv.pvname, wait_val, max_timeout_sec, ')')
    #delay for pv to change
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
                    #print ('wait_pv(', pv.pvname, wait_val, max_timeout_sec, ') reached max timeout. Return False')
                    return False
            time.sleep(.01)
        else:
            return True


def init_general_PVs(global_PVs, variableDict):
    print ('init_PVs()')
    #init detector pv's
    global_PVs['Cam1_ImageMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:ImageMode')
    global_PVs['Cam1_ArrayCallbacks'] = PV(variableDict['IOC_Prefix'] + 'cam1:ArrayCallbacks')
    global_PVs['Cam1_AcquirePeriod'] = PV(variableDict['IOC_Prefix'] + 'cam1:AcquirePeriod')
    global_PVs['Cam1_FrameRate_on_off'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameRateOnOff')
    global_PVs['Cam1_FrameRate_val'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameRateValAbs')
    global_PVs['Cam1_TriggerMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:TriggerMode')
    global_PVs['Cam1_SoftGlueTrigger'] = PV('32idcTXM:SG3:BUFFER-2_IN_Signal')
    global_PVs['Cam1_SoftwareTrigger'] = PV(variableDict['IOC_Prefix'] + 'cam1:SoftwareTrigger')
    global_PVs['Cam1_AcquireTime'] = PV(variableDict['IOC_Prefix'] + 'cam1:AcquireTime')
    global_PVs['Cam1_FrameRateOnOff'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameRateOnOff')
    global_PVs['Cam1_FrameType'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType')
    global_PVs['Cam1_NumImages'] = PV(variableDict['IOC_Prefix'] + 'cam1:NumImages')
    global_PVs['Cam1_Acquire'] = PV(variableDict['IOC_Prefix'] + 'cam1:Acquire')
    global_PVs['Cam1_Display'] = PV(variableDict['IOC_Prefix'] + 'image1:EnableCallbacks')

    #hdf5 writer pv's
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
    global_PVs['HDF1_NextFile'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileNumber')

    #tiff writer pv's
    global_PVs['TIFF1_AutoSave'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:AutoSave')
    global_PVs['TIFF1_DeleteDriverFile'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:DeleteDriverFile')
    global_PVs['TIFF1_EnableCallbacks'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:EnableCallbacks')
    global_PVs['TIFF1_BlockingCallbacks'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:BlockingCallbacks')
    global_PVs['TIFF1_FileWriteMode'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:FileWriteMode')
    global_PVs['TIFF1_NumCapture'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:NumCapture')
    global_PVs['TIFF1_Capture'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:Capture')
    global_PVs['TIFF1_Capture_RBV'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:Capture_RBV')
    global_PVs['TIFF1_FileName'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:FileName')
    global_PVs['TIFF1_FullFileName_RBV'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:FullFileName_RBV')
    global_PVs['TIFF1_FileTemplate'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:FileTemplate')
    global_PVs['TIFF1_ArrayPort'] = PV(variableDict['IOC_Prefix'] + 'TIFF1:NDArrayPort')

    if TOMO: # Tomo (A-station)
            print('*** Running  in station A:')
            # Sample stack motor pv's:
            global_PVs['Motor_SampleX'] = PV('2bma:m49.VAL')
            global_PVs['Motor_SampleY'] = PV('2bma:m20.VAL')
            global_PVs['Motor_SampleRot'] = PV('2bma:m82.VAL') # 
            global_PVs['Motor_SampleRot_Stop'] = PV('2bma:m82.STOP') #
            global_PVs['Motor_Sample_Top_X'] = PV('2bma:m50.VAL')
            global_PVs['Motor_Sample_Top_X_RBV'] = PV('2bma:m50.RBV')
            global_PVs['Motor_Sample_Top_X_STATUS'] = PV('2bma:m50.MSTA') 
            global_PVs['Motor_Sample_Top_X_MIP'] = PV('2bma:m50.MIP') 
            global_PVs['Motor_Sample_Top_X_RETRY'] = PV('2bma:m50.RCNT')
            global_PVs['Motor_Sample_Top_Z'] = PV('2bma:m51.VAL') # Smaract XZ TXM set
#            global_PVs['Motor_X_Tile'] = PV('.VAL') # for mosaic script only
#            global_PVs['Motor_Y_Tile'] = PV('.VAL') # for mosaic script only

    else: # Mona (B-station)
            print('*** Running  in station B:')
            # Sample stack motor pv's:
            global_PVs['Motor_SampleX'] = PV('2bmb:m63.VAL')
            global_PVs['Motor_SampleY'] = PV('2bmb:m57.VAL') # for the micro-CT system
            global_PVs['Motor_SampleRot'] = PV('2bmb:m100.VAL') # Aerotech
            global_PVs['Motor_SampleRot_Stop'] = PV('2bmb:m100.STOP') # PI Micos air bearing rotary stage
#            global_PVs['Motor_SampleZ'] = PV('.VAL')
            global_PVs['Motor_Sample_Top_X'] = PV('2bmb:m76.VAL') # Smaract XZ micro-CT set
            global_PVs['Motor_Sample_Top_X_RBV'] = PV('2bmb:m76.RBV') # 
            global_PVs['Motor_Sample_Top_X_STATUS'] = PV('2bmb:m76.MSTA')
            global_PVs['Motor_Sample_Top_X_MIP'] = PV('2bmb:m76.MIP')
            global_PVs['Motor_Sample_Top_X_RETRY'] = PV('2bmb:m76.RCNT')
            global_PVs['Motor_Sample_Top_Z'] = PV('2bmb:m77.VAL') # Smaract XZ micro-CT set
#            global_PVs['Motor_X_Tile'] = PV('.VAL') # for mosaic script only
#            global_PVs['Motor_Y_Tile'] = PV('.VAL') # for mosaic script only

            # CCD motors:
            global_PVs['CCD_Motor'] = PV('.VAL')
     

    #shutter pv's
    global_PVs['ShutterA_Open'] = PV('2bma:A_shutter:open.VAL')
    global_PVs['ShutterA_Close'] = PV('2bma:A_shutter:close.VAL')
    global_PVs['ShutterA_Move_Status'] = PV('PA:02BM:STA_A_FES_OPEN_PL')
    global_PVs['ShutterB_Open'] = PV('2bma:B_shutter:open.VAL')
    global_PVs['ShutterB_Close'] = PV('2bma:B_shutter:close.VAL')
    global_PVs['ShutterB_Move_Status'] = PV('PA:02BM:STA_B_SBS_OPEN_PL')

    #fly macro
    global_PVs['FlyTriggerSelect'] = PV('2bmb:flyTriggerSelect')
    if TOMO: # for the PI Micos
            global_PVs['FlyTriggerSelect'].put(0, wait=True)
            global_PVs['Set_encoder_to_motor_RBV'] = PV('32idcTXM:eFly:setEncoderPos')
            global_PVs['Set_encoder_to_motor_RBV'].put(1, wait=True)
            global_PVs['Fly_ScanDelta'] = PV('32idcTXM:eFly:scanDelta')
            global_PVs['Fly_StartPos'] = PV('32idcTXM:eFly:startPos')
            global_PVs['Fly_EndPos'] = PV('32idcTXM:eFly:endPos')
            global_PVs['Fly_SlewSpeed'] = PV('32idcTXM:eFly:slewSpeed')
            global_PVs['Fly_Taxi'] = PV('32idcTXM:eFly:taxi')
            global_PVs['Fly_Run'] = PV('32idcTXM:eFly:fly')
            global_PVs['Fly_ScanControl'] = PV('32idcTXM:eFly:scanControl')
            global_PVs['Fly_Calc_Projections'] = PV('32idcTXM:eFly:calcNumTriggers')
            global_PVs['Fly_Set_Encoder_Pos'] = PV('32idcTXM:eFly:EncoderPos')
            global_PVs['Theta_Array'] = PV('32idcTXM:eFly:motorPos.AVAL')

    else: # Mona (B-station)
            global_PVs['FlyTriggerSelect'].put(1, wait=True)
            global_PVs['Fly_ScanDelta'] = PV('2bmb:PSOFly:scanDelta')
            global_PVs['Fly_StartPos'] = PV('2bmb:PSOFly:startPos')
            global_PVs['Fly_EndPos'] = PV('2bmb:PSOFly:endPos')
            global_PVs['Fly_SlewSpeed'] = PV('2bmb:PSOFly:slewSpeed')
            global_PVs['Fly_Taxi'] = PV('2bmb:PSOFly:taxi')
            global_PVs['Fly_Run'] = PV('2bmb:PSOFly:fly')
            global_PVs['Fly_ScanControl'] = PV('2bmb:PSOFly:scanControl')
            global_PVs['Fly_Calc_Projections'] = PV('2bmb:PSOFly:numTriggers')
            global_PVs['Theta_Array'] = PV('2bmb:PSOFly:motorPos.AVAL')
            global_PVs['Fly_Set_Encoder_Pos'] = PV('2bmb:eFly:EncoderPos')

    # theta controls
    global_PVs['Reset_Theta'] = PV('2bmb:SG_RdCntr:reset.PROC')
    global_PVs['Proc_Theta'] = PV('2bmb:SG_RdCntr:cVals.PROC')
    global_PVs['Theta_Cnt'] = PV('2bmb:SG_RdCntr:aSub.VALB')

    #init misc pv's
    global_PVs['Image1_Callbacks'] = PV(variableDict['IOC_Prefix'] + 'image1:EnableCallbacks')
    global_PVs['ExternShutterExposure'] = PV('2bmb:shutCam:tExpose')
    #global_PVs['ClearTheta'] = PV('2bmb:recPV:PV1_clear')
    global_PVs['ExternShutterDelay'] = PV('2bmb:shutCam:tDly')

    #init proc1 pv's
    global_PVs['Proc1_Callbacks'] = PV(variableDict['IOC_Prefix'] + 'Proc1:EnableCallbacks')
    global_PVs['Proc1_ArrayPort'] = PV(variableDict['IOC_Prefix'] + 'Proc1:NDArrayPort')
    global_PVs['Proc1_Filter_Enable'] = PV(variableDict['IOC_Prefix'] + 'Proc1:EnableFilter')
    global_PVs['Proc1_Filter_Type'] = PV(variableDict['IOC_Prefix'] + 'Proc1:FilterType')
    global_PVs['Proc1_Num_Filter'] = PV(variableDict['IOC_Prefix'] + 'Proc1:NumFilter')
    global_PVs['Proc1_Reset_Filter'] = PV(variableDict['IOC_Prefix'] + 'Proc1:ResetFilter')
    global_PVs['Proc1_AutoReset_Filter'] = PV(variableDict['IOC_Prefix'] + 'Proc1:AutoResetFilter')
    global_PVs['Proc1_Filter_Callbacks'] = PV(variableDict['IOC_Prefix'] + 'Proc1:FilterCallbacks')

    #interlaced
    global_PVs['Interlaced_PROC'] = PV('32idcTXM:iFly:interlaceFlySub.PROC')
    global_PVs['Interlaced_Theta_Arr'] = PV('32idcTXM:iFly:interlaceFlySub.VALC')
    global_PVs['Interlaced_Num_Cycles'] = PV('32idcTXM:iFly:interlaceFlySub.C')
    global_PVs['Interlaced_Num_Cycles_RBV'] = PV('32idcTXM:iFly:interlaceFlySub.VALH')
    global_PVs['Interlaced_Images_Per_Cycle'] = PV('32idcTXM:iFly:interlaceFlySub.A')
    global_PVs['Interlaced_Images_Per_Cycle_RBV'] = PV('32idcTXM:iFly:interlaceFlySub.VALF')
    global_PVs['Interlaced_Num_Sub_Cycles'] = PV('32idcTXM:iFly:interlaceFlySub.B')
    global_PVs['Interlaced_Num_Sub_Cycles_RBV'] = PV('32idcTXM:iFly:interlaceFlySub.VALG')


def stop_scan(global_PVs, variableDict):
    print ('Stop scan called!')
    global_PVs['Motor_SampleRot_Stop'].put(1)
    global_PVs['TIFF1_AutoSave'].put('No')
    global_PVs['TIFF1_Capture'].put(0)
    global_PVs['HDF1_Capture'].put(0)
    wait_pv(global_PVs['HDF1_Capture'], 0)
    reset_CCD(global_PVs, variableDict)
    reset_CCD(global_PVs, variableDict)
    #global_PVs['Cam1_SoftGlueTrigger'].put('1')
#    global_PVs['Fast_Shutter_Uniblitz'].put(1, wait=True) # Open the fast shutter #### FOR SUJI


def reset_CCD(global_PVs, variableDict):
    if 1: # Usual script
        global_PVs['Cam1_TriggerMode'].put('Internal', wait=True)    # 
        global_PVs['Cam1_TriggerMode'].put('Overlapped', wait=True)  # sequence Internal / Overlapped / internal because of CCD bug!!
        global_PVs['Cam1_TriggerMode'].put('Internal', wait=True)    #
        global_PVs['Proc1_Filter_Callbacks'].put( 'Every array' )
    #    global_PVs['HDF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
        global_PVs['Cam1_ImageMode'].put('Continuous', wait=True)
    #    global_PVs['Cam1_FrameRate_on_off'].put(1, wait=True) # force a slow frame rate for the display
    #    global_PVs['Cam1_FrameRate_val'].put(5, wait=True) # force a slow frame rate for the display --> 5 fps
        global_PVs['Cam1_Display'].put(1)
        global_PVs['Cam1_Acquire'].put(DetectorAcquire); wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)

    else:

        global_PVs['Cam1_NumImages'].put(100000000, wait=True)
        global_PVs['Cam1_AcquireTime'].put(1)
        global_PVs['Cam1_AcquirePeriod'].put(1)
        global_PVs['Cam1_Acquire'].put(DetectorAcquire) # Start acquiring state
        wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 1)

        # Start the fake streaming mode:
        streaming_mode = 1
        while streaming_mode:
            global_PVs['Cam1_SoftwareTrigger'].put(1) # push the software trigger button
            time.sleep(0.4)
            if global_PVs['Cam1_Acquire'].get() == 0: # checking acquiring still ON
                streaming_mode == 0

        

def setup_detector(global_PVs, variableDict):
    print(' ')
    print('  *** setup_detector')
    if variableDict.has_key('Display_live'):
        print ('** disable live display')
        global_PVs['Cam1_Display'].put( int( variableDict['Display_live'] ) )
    global_PVs['Cam1_ImageMode'].put('Multiple')
    global_PVs['Cam1_ArrayCallbacks'].put('Enable')
    #global_PVs['Image1_Callbacks'].put('Enable')
    global_PVs['Cam1_AcquirePeriod'].put(float(variableDict['ExposureTime']))
    global_PVs['Cam1_AcquireTime'].put(float(variableDict['ExposureTime']))
    # if we are using external shutter then set the exposure time
    global_PVs['Cam1_FrameRateOnOff'].put(0)
    if variableDict.has_key('ExternalShutter'):
        if int(variableDict['ExternalShutter']) == 1:
            global_PVs['ExternShutterExposure'].put(float(variableDict['ExposureTime']))
            global_PVs['ExternShutterDelay'].put(float(variableDict['Ext_ShutterOpenDelay']))
    # if software trigger capture two frames (issue with Point grey grasshopper)
    if PG_Trigger_External_Trigger == 1:
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
    else:
        global_PVs['Cam1_TriggerMode'].put('Internal')
    #global_PVs['ClearTheta'].put(1)
    print('  *** setup_detector: Done!')


def setup_writer(global_PVs, variableDict, filename=None):
    print ('setup_writer()')
    if variableDict.has_key('Recursive_Filter_Enabled'):
        if variableDict['Recursive_Filter_Enabled'] == 1:
#            global_PVs['Proc1_Callbacks'].put('Disable')
            global_PVs['Proc1_Callbacks'].put('Enable')
            global_PVs['Proc1_Filter_Enable'].put('Disable')
            global_PVs['HDF1_ArrayPort'].put('PROC1')
            global_PVs['Proc1_Filter_Type'].put( Recursive_Filter_Type )
            global_PVs['Proc1_Num_Filter'].put( int( variableDict['Recursive_Filter_N_Images'] ) )
            global_PVs['Proc1_Reset_Filter'].put( 1 )
            global_PVs['Proc1_AutoReset_Filter'].put( 'Yes' )
            global_PVs['Proc1_Filter_Callbacks'].put( 'Array N only' )
        else:
#            global_PVs['Proc1_Callbacks'].put('Disable')
            global_PVs['Proc1_Filter_Enable'].put('Disable')
            global_PVs['HDF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
    else:
#        global_PVs['Proc1_Callbacks'].put('Disable')
        global_PVs['Proc1_Filter_Enable'].put('Disable')
        global_PVs['HDF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
    global_PVs['HDF1_AutoSave'].put('Yes')
    global_PVs['HDF1_DeleteDriverFile'].put('No')
    global_PVs['HDF1_EnableCallbacks'].put('Enable')
    global_PVs['HDF1_BlockingCallbacks'].put('No')
    if variableDict.has_key('ProjectionsPerRot'):
        totalProj = int(variableDict['PreDarkImages']) + int(variableDict['PreWhiteImages']) + ( int(variableDict['Projections']) * int(variableDict['ProjectionsPerRot'])) + int(variableDict['PostDarkImages']) + int(variableDict['PostWhiteImages'])
    else:
        totalProj = int(variableDict['PreDarkImages']) + int(variableDict['PreWhiteImages']) + int(variableDict['Projections']) + int(variableDict['PostDarkImages']) + int(variableDict['PostWhiteImages'])
    global_PVs['HDF1_NumCapture'].put(totalProj)
    global_PVs['HDF1_FileWriteMode'].put(str(variableDict['FileWriteMode']), wait=True)
    if not filename == None:
        global_PVs['HDF1_FileName'].put(filename)
    global_PVs['HDF1_Capture'].put(1)
    wait_pv(global_PVs['HDF1_Capture'], 1)


def setup_tiff_writer(global_PVs, variableDict, filename=None):
    print('  ')
    print('  *** setup_writer')
    global_PVs['TIFF1_ArrayPort'].put(variableDict['TIFFNDArrayPort'], wait=True)
    if variableDict.has_key('Recursive_Filter_Enabled'):
        if variableDict['Recursive_Filter_Enabled'] == 1:
#            global_PVs['Proc1_Callbacks'].put('Disable')
            global_PVs['Proc1_Callbacks'].put('Enable')
            global_PVs['Proc1_Filter_Enable'].put('Disable')
            global_PVs['TIFF1_ArrayPort'].put('PROC1')
            global_PVs['Proc1_Filter_Type'].put( Recursive_Filter_Type )
            global_PVs['Proc1_Num_Filter'].put( int( variableDict['Recursive_Filter_N_Images'] ) )
            global_PVs['Proc1_Reset_Filter'].put( 1 )
            global_PVs['Proc1_AutoReset_Filter'].put( 'Yes' )
            global_PVs['Proc1_Filter_Callbacks'].put( 'Array N only' )
#        else:
##            global_PVs['Proc1_Callbacks'].put('Disable')
#            global_PVs['Proc1_Filter_Enable'].put('Disable')
#            global_PVs['TIFF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
#    else:
##        global_PVs['Proc1_Callbacks'].put('Disable')
#        global_PVs['Proc1_Filter_Enable'].put('Disable')
#        global_PVs['TIFF1_ArrayPort'].put(global_PVs['Proc1_ArrayPort'].get())
    global_PVs['TIFF1_AutoSave'].put('Yes')
    global_PVs['TIFF1_DeleteDriverFile'].put('No')
    global_PVs['TIFF1_EnableCallbacks'].put('Enable')
    global_PVs['TIFF1_BlockingCallbacks'].put('No')
    totalProj = int(variableDict['Projections'])
    global_PVs['TIFF1_NumCapture'].put(totalProj)
    global_PVs['TIFF1_FileWriteMode'].put(str(variableDict['FileWriteMode']), wait=True)
    if not filename == None:
        global_PVs['TIFF1_FileName'].put(filename)
    global_PVs['TIFF1_Capture'].put(1)
    wait_pv(global_PVs['TIFF1_Capture'], 1)
    print('  *** setup_writer: Done!')

def capture_multiple_projections(global_PVs, variableDict, num_proj, frame_type):
    print('capture_multiple_projections(', num_proj, frame_type, ')')
    wait_time_sec = int(variableDict['ExposureTime']) + 5
    global_PVs['Cam1_ImageMode'].put('Multiple')
    global_PVs['Cam1_FrameType'].put(frame_type)
    if PG_Trigger_External_Trigger == 1:
        print ('Using external trigger')
        #set external trigger mode
        global_PVs['Cam1_TriggerMode'].put('Overlapped')
        global_PVs['Cam1_NumImages'].put(1)
        for i in range(int(num_proj)):
            global_PVs['Cam1_Acquire'].put(DetectorAcquire)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorAcquire, 2)
            time.sleep(0.1)
            global_PVs['Cam1_SoftwareTrigger'].put(1, wait=True)
            time.sleep(0.1)
            wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec)
            time.sleep(0.1)
    else:
        global_PVs['Cam1_TriggerMode'].put('Internal', wait=True)
        global_PVs['Cam1_NumImages'].put(int(num_proj), wait=True)
        global_PVs['Cam1_Acquire'].put(DetectorAcquire)
        wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec)


def move_sample_in(global_PVs, variableDict):
    print(' ')
    print('  *** move_sample_in')
#    global_PVs['Motor_X_Tile'].put(float(variableDict['SampleXIn']), wait=True)
    global_PVs['Motor_SampleX'].put(float(variableDict['SampleXIn']), wait=True)
#    global_PVs['Motor_Sample_Top_X'].put(float(variableDict['SampleXIn']), wait=True)
    if False == wait_pv(global_PVs['Motor_SampleX'], float(variableDict['SampleXIn']), 60):
        print ('Motor_SampleX did not move in properly')
        print (global_PVs['Motor_SampleX'].get())
        print ('\r\n\r\n')
#    global_PVs['Motor_Sample_Top_Z'].put(float(variableDict['SampleZIn']), wait=True)
#    global_PVs['Motor_SampleY'].put(float(variableDict['SampleYIn']), wait=True)
#    global_PVs['Motor_SampleZ'].put(float(variableDict['SampleZIn']), wait=True)
#    global_PVs['Motor_SampleRot'].put(0, wait=True)
    print('  *** move_sample_in: Done!')


def move_sample_out(global_PVs, variableDict):
    print ('move_sample_out()')
#    global_PVs['Motor_SampleRot'].put(float(variableDict['SampleRotOut']), wait=True)
#    global_PVs['Motor_X_Tile'].put(float(variableDict['SampleXOut']), wait=True)
#    global_PVs['Motor_SampleX'].put(float(variableDict['SampleXOut']), wait=True)
    global_PVs['Motor_SampleX'].put(float(variableDict['SampleXOut']), wait=True)
    if False == wait_pv(global_PVs['Motor_SampleX'], float(variableDict['SampleXOut']), 60):
        print ('Motor_SampleX did not move out properly')
        print (global_PVs['Motor_SampleX'].get())
        print ('\r\n\r\n')
#        global_PVs['Motor_Sample_Top_Z'].put(float(variableDict['SampleZOut']), wait=True)
#    global_PVs['Motor_SampleY'].put(float(variableDict['SampleYOut']), wait=True)
#    global_PVs['Motor_SampleZ'].put(float(variableDict['SampleZOut']), wait=True)
#    global_PVs['Motor_SampleRot'].put(0, wait=True)

def open_shutters(global_PVs, variableDict):
    print(' ')
    print('  *** open_shutters')
    if UseShutterA > 0:
        global_PVs['ShutterA_Open'].put(1, wait=True)
        wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Open_Value)
        time.sleep(3)
    if UseShutterB > 0:
        global_PVs['ShutterB_Open'].put(1, wait=True)
        wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Open_Value)
    print('  *** open_shutters: Done!')


def close_shutters(global_PVs, variableDict):
    print ('close_shutters()')
    if UseShutterA > 0:
        global_PVs['ShutterA_Close'].put(1, wait=True)
        wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
    if UseShutterB > 0:
        global_PVs['ShutterB_Close'].put(1, wait=True)
        wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Close_Value)


def add_theta(global_PVs, variableDict, theta_arr):
    print ('add_theta()')
    fullname = global_PVs['HDF1_FullFileName_RBV'].get(as_string=True)
    try:
        hdf_f = h5py.File(fullname, mode='a')
        if theta_arr != None:
            theta_ds = hdf_f.create_dataset('/exchange/theta', (len(theta_arr),))
            theta_ds[:] = theta_arr[:]
        hdf_f.close()
    except:
        traceback.print_exc(file=sys.stdout)


def add_extra_hdf5(global_PVs, variableDict, theta_arr, interf_arrs):
    print ('add_extra_hdf5()')
    wait_pv(global_PVs['HDF1_Capture_RBV'], 0, 10.0)
    fullname = global_PVs['HDF1_FullFileName_RBV'].get(as_string=True)
    try:
        print ('Opening hdf5 file ',fullname)
        hdf_f = h5py.File(fullname, mode='a')
        theta_ds = hdf_f.create_dataset('/exchange/theta', (len(theta_arr),))
        theta_ds[:] = theta_arr[:]
        if variableDict.has_key('UseInterferometer') and int(variableDict['UseInterferometer']) > 0:
            interf_ds = hdf_f.create_dataset('/exchange/interferometer', (len(interf_arrs), len(interf_arrs[0])), dtype='f' )
            for i in range(len(interf_arrs)):
                if len(interf_arrs[i]) == len(interf_arrs[0]):
                    interf_ds[i,:] = interf_arrs[i][:]
        hdf_f.close()
    except:
        traceback.print_exc(file=sys.stdout)


def move_energy(global_PVs, variableDict): # TO BE TESTED!!!
     # Extract variables from variableDict:
    constant_mag = int(variableDict['constant_mag'])
    new_Energy = float(variableDict['new_Energy'])
    ZP_diameter = float(variableDict['ZP_diameter'])
    Offset = float(variableDict['Offset'])
    drn = float(variableDict['drn'])
    
    print ('move to a new energy:%3.3f' % new_Energy)
    energy_init = float(global_PVs['DCMputEnergy'].get())
#    energy_init = global_PVs['DCMputEnergy'].get() # energy before changin
    landa_init = 1240.0 / (energy_init * 1000.0)
    print ('landa_init: %3.3f' % landa_init)
    ZP_focal = ZP_diameter * drn / (1000.0 * landa_init)
    print ('ZP_focal: %3.3f' % ZP_focal)
    curr_CCD_location = float(global_PVs['CCD_Motor'].get())
    D_init = (curr_CCD_location + math.sqrt(curr_CCD_location * curr_CCD_location - 4.0 * curr_CCD_location * ZP_focal) ) / 2.0
    new_landa = 1240.0 / (new_Energy * 1000.0)
    ZP_focal = ZP_diameter * drn / (1000.0 * new_landa)
    
    if constant_mag: # CCD will move to maintain magnification during energy change
            Mag = (D_init - ZP_focal) / ZP_focal
            print ('mag', Mag)
            global_PVs['DCMmvt'].put(1)
        
            dist_ZP_ccd = Mag * ZP_focal + ZP_focal
            ZP_WD = dist_ZP_ccd * ZP_focal / (dist_ZP_ccd - ZP_focal)
            CCD_location = ZP_WD + dist_ZP_ccd
            print ('move ccd ', CCD_location)
            global_PVs['CCD_Motor'].put(CCD_location, wait=True)
            print ('move zp ', ZP_WD)
#            global_PVs['zone_plate_z'].put(ZP_WD, wait=True)
            global_PVs['zone_plate_2_z'].put(ZP_WD, wait=True)

    else: # no constant magnification, i.e. CCD will not move
            
            D_new = (curr_CCD_location + math.sqrt(curr_CCD_location * curr_CCD_location - 4.0 * curr_CCD_location * ZP_focal) ) / 2.0
            ZP_WD = D_new * ZP_focal / (D_new - ZP_focal)
            print ('move zp ', ZP_WD)
#            global_PVs['zone_plate_z'].put(ZP_WD, wait=True)
            global_PVs['zone_plate_2_z'].put(ZP_WD, wait=True)

    print('* Move the DCM to the new energy: %3.3f keV*') % new_Energy
    global_PVs['DCMputEnergy'].put(new_Energy, wait=True)

    print('* Move gap to the new energy: %3.3f keV*') % new_Energy
    global_PVs['GAPputEnergy'].put(new_Energy)
    wait_pv(global_PVs['EnergyWait'], 0)
    print('* Add the energy offset to the gap *')
    time.sleep(2)
    global_PVs['GAPputEnergy'].put(new_Energy + Offset)
    wait_pv(global_PVs['EnergyWait'], 0)
    time.sleep(2)
    global_PVs['DCMmvt'].put(1)
    

########################## Interlaced #########################
def bitreversed_decimal(dec_input, maxbits):
# Description: Compute bit-reversed value of a decimal number 
# Inputs:
# in - Decimal input whose bit-reversed value must be computed
# maxbits - Total number of bits in binary used to represent 'in' and 'out'.
# Ouputs:
# out - Bit-reversed value of 'in'.

    if maxbits == 0:
        bit_rev = 0
        return

#    dec_input = bin(dec_input, maxbits)
    dec_input = int(dec_input)
    maxbits = int(maxbits)
    
    dec_input = bin(dec_input)
    dec_input = dec_input[2:]
    if len(dec_input)<maxbits:
        dec_input = '0'*(maxbits-len(dec_input))+dec_input
#    bit_rev = '0'*maxbits
    bit_rev = str('')
    for i in range(0,maxbits):
#        print('  ** Loop #',i)
#        print('       maxbits: ', maxbits)
#        print('       dec_input', dec_input)
        bit_rev = bit_rev + dec_input[maxbits-1-i]
#        print('       bit_rev: ', bit_rev)
    
    bit_rev = int(bit_rev,2)

    return bit_rev
    

def gen_interlaced_views(N, K, N_p):
# Description: Generate interlaced view angles
# Formula: the_views[n] = [(n mod(N/K))K + Br(floor(nK/N) mod(K))]*pi/N;
#          mod denotes modulo, floor gives the lowest integer value, Br denotes bit-reversal 
# Input: 
# N - Total number of distinct view angles in a frame
# K - Number of interlaced sub-frames in each frame
# N_p - Total number of view angles (Note that angles repeat from frame to frame)
# Output:
# the_views - Interlaced view angles

    k = int(np.log2(K))
    L = N/K # Number of equi-spaced view angles in a sub-frame
    delta_theta = 180/N # Determines scaling of output
    
#    print(k, L, K)
    
    the_views = np.zeros((N_p))
    buf1 = np.zeros((N_p))
    buf2 = np.zeros((N_p))
    
    for i in range(0,N_p):
#        print('**** Main loop #', i)
        buf1[i] = np.mod(i,L)*K
        buf2[i] = bitreversed_decimal(np.mod(np.floor(i/L), K), k)
        the_views[i] = buf1[i] + buf2[i]
        the_views[i] = the_views[i]*delta_theta
    
    return the_views


## Example:
#N_theta = 16 # Total number of distinct view angles in a frame
#K = 4 # Number of interlaced sub-frames in each frame
#N_p = 32 # Total number of view angles (Note that angles repeat from frame to frame)

#the_views = gen_interlaced_views(N_theta, K, N_p)
#
#X = np.linspace(0,N_p-1)
##plt.plot(X, the_views, 'o'), plt.plot(the_views, 'ro'), plt.plot(the_views, 'b-'), plt.grid(), plt.xlabel('View index'), plt.ylabel('View angle (degrees)'), plt.title('Interlaced views'), plt.show()
########################## Interlaced #########################
