'''
    Tomo Scan Lib for Sector 2-BM
    
'''
from __future__ import print_function

import time
import sys
import numpy as np
import json

from epics import PV

TESTING = False

ShutterAisFast = True           # True: use m7 as shutter; False: use Front End Shutter

ShutterA_Open_Value = 1
ShutterA_Close_Value = 0
ShutterB_Open_Value = 1
ShutterB_Close_Value = 0

FrameTypeData = 0
FrameTypeDark = 1
FrameTypeWhite = 2


def update_variable_dict(variableDict):
    argDic = {}
    if len(sys.argv) > 1:
        strArgv = sys.argv[1]
        argDic = json.loads(strArgv)
    ##print('orig variable dict', variableDict)
    for k,v in argDic.iteritems():
        variableDict[k] = v
    ##print('new variable dict', variableDict)


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
                    #print('wait_pv(', pv.pvname, wait_val, max_timeout_sec, ') reached max timeout. Return False')
                    return False
            time.sleep(.01)
        else:
            return True


def dimaxTest(global_PVs, variableDict):

    print(' ')
    print('  *** Testing PCO Dimax camera')
    global_PVs['HDF1_EnableCallbacks'].put(1, wait=True, timeout=1000.0)  
    global_PVs['Cam1_NumImages'].put('10', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOLiveView'].put('Yes', wait=True, timeout=1000.0)

    global_PVs['Cam1_AcquireTime'].put('0.001000', wait=True, timeout=1000.0)

    global_PVs['Cam1_SizeX'].put(variableDict['roiSizeX'], wait=True, timeout=1000.0)
    global_PVs['Cam1_SizeY'].put(variableDict['roiSizeY'], wait=True, timeout=1000.0)

    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)    
    global_PVs['Cam1_Acquire'].put('Acquire', wait=False, timeout=1000.0)     # note on Acquire wait must be False
    time.sleep(3)
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)     

    print('  *** Testing PCO Dimax camera: done!')
    
    
def init_general_PVs(global_PVs, variableDict):

    # shutter PVs
    global_PVs['ShutterA_Open'] = PV('2bma:A_shutter:open.VAL')
    global_PVs['ShutterA_Close'] = PV('2bma:A_shutter:close.VAL')
    global_PVs['ShutterA_Move_Status'] = PV('PA:02BM:STA_A_FES_OPEN_PL')
    global_PVs['ShutterB_Open'] = PV('2bma:B_shutter:open.VAL')
    global_PVs['ShutterB_Close'] = PV('2bma:B_shutter:close.VAL')
    global_PVs['ShutterB_Move_Status'] = PV('PA:02BM:STA_B_SBS_OPEN_PL')


    # Filters
    global_PVs['Filters'] = PV('2bma:fltr1:select.VAL')

    # Mirror PVs
    global_PVs['Mirr_Ang'] = PV('2bma:M1angl.VAL')
    global_PVs['Mirr_YAvg'] = PV('2bma:M1avg.VAL')

    # DMM PV    
    global_PVs['DMM_USY_OB'] = PV('2bma:m26.VAL') 
    global_PVs['DMM_USY_IB'] = PV('2bma:m27.VAL')
    global_PVs['DMM_DSY'] = PV('2bma:m29.VAL')
    global_PVs['USArm'] = PV('2bma:m30.VAL')
    global_PVs['DSArm'] = PV('2bma:m31.VAL')
    global_PVs['M2Y'] = PV('2bma:m32.VAL')
    global_PVs['DMM_USX'] = PV('2bma:m25.VAL')
    global_PVs['DMM_DSX'] = PV('2bma:m28.VAL')
    
    # XIA Slits
    global_PVs['XIASlit'] = PV('2bma:m7.VAL')
    global_PVs['Slit1Hcenter'] = PV('2bma:Slit1Hcenter.VAL')


    if variableDict['Station'] == '2-BM-A':
        print('*** Running in station A:')
        # Set sample stack motor PVs:
        global_PVs['Motor_SampleX'] = PV('2bma:m49.VAL')
        global_PVs['Motor_SampleY'] = PV('2bma:m20.VAL')
        global_PVs['Motor_SampleRot'] = PV('2bma:m82.VAL') # Aerotech ABR-250
        global_PVs['Motor_SampleRot_Cnen'] = PV('2bma:m82.CNEN') 
        global_PVs['Motor_SampleRot_Accl'] = PV('2bma:m82.ACCL') 
        global_PVs['Motor_SampleRot_Stop'] = PV('2bma:m82.STOP') 
        global_PVs['Motor_SampleRot_Set'] = PV('2bma:m82.SET') 
        global_PVs['Motor_SampleRot_Velo'] = PV('2bma:m82.VELO') 
        global_PVs['Motor_Sample_Top_X'] = PV('2bma:m50.VAL')
        global_PVs['Motor_Sample_Top_Z'] = PV('2bma:m51.VAL') 
        global_PVs['Motor_Stress'] = PV('2bma:m58.VAL') 
        global_PVs['Motor_FurnaceY'] = PV('2bma:m55.VAL') 
        # Set FlyScan
        global_PVs['Fly_ScanDelta'] = PV('2bma:PSOFly2:scanDelta')
        global_PVs['Fly_StartPos'] = PV('2bma:PSOFly2:startPos')
        global_PVs['Fly_EndPos'] = PV('2bma:PSOFly2:endPos')
        global_PVs['Fly_SlewSpeed'] = PV('2bma:PSOFly2:slewSpeed')
        global_PVs['Fly_Taxi'] = PV('2bma:PSOFly2:taxi')
        global_PVs['Fly_Run'] = PV('2bma:PSOFly2:fly')
        global_PVs['Fly_ScanControl'] = PV('2bma:PSOFly2:scanControl')
        #    global_PVs['Fly_Calc_Projections'] = PV('2bma:PSOFly2:numTriggers')
        #    global_PVs['Theta_Array'] = PV('2bma:PSOFly2:motorPos.AVAL')
        # Set FlyScan
        global_PVs['Fast_Shutter'] = PV('2bma:m23.VAL')

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
        global_PVs['Motor_Sample_Top_X'] = PV('2bmb:m76.VAL') 
        global_PVs['Motor_Sample_Top_Z'] = PV('2bmb:m77.VAL')

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

    else:
        print('*** %s is not a valid station' % variableDict['Station'])

    global_PVs['Cam1_Model'] = PV(variableDict['IOC_Prefix'] + 'cam1:Model_RBV')
    global_PVs['Cam1_Acquire'] = PV(variableDict['IOC_Prefix'] + 'cam1:Acquire')   
    global_PVs['Cam1_AcquirePeriod'] = PV(variableDict['IOC_Prefix'] + 'cam1:AcquirePeriod')
    global_PVs['Cam1_AcquireTime'] = PV(variableDict['IOC_Prefix'] + 'cam1:AcquireTime')
    global_PVs['Cam1_ImageMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:ImageMode')
    global_PVs['Cam1_NumImagesCounter_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:NumImagesCounter_RBV')   
    global_PVs['Cam1_PCOEdgeFastscan'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_edge_fastscan')
    global_PVs['Cam1_PCOTriggerMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_trigger_mode')
    global_PVs['Cam1_PCOIsFrameRateMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_is_frame_rate_mode')   
    global_PVs['Cam1_PCOSetFrameRate'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_set_frame_rate')
    global_PVs['Cam1_PCOReady2Acquire'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_ready2acquire')
    global_PVs['Cam1_PCOGlobalShutter'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_global_shutter')

    global_PVs['Cam1_PCOLiveView'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_live_view')
    global_PVs['Cam1_PCOImgs2Dump'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_imgs2dump') 
    global_PVs['Cam1_PCOImgs2Dump_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_imgs2dump_RBV')           
    global_PVs['Cam1_PCOCancelDump'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_cancel_dump')
    global_PVs['Cam1_PCONumImgsSeg0_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_num_imgs_seg0_RBV')
    global_PVs['Cam1_PCOMaxImgsSeg0_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_max_imgs_seg0_RBV')
    global_PVs['Cam1_PCODumpCameraMemory'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_dump_camera_memory')
    global_PVs['Cam1_PCODumpCounter'] = PV(variableDict['IOC_Prefix'] + 'cam1:pco_dump_counter')  

    global_PVs['Cam1_MaxSizeX'] = PV(variableDict['IOC_Prefix'] + 'cam1:MaxSizeX_RBV')
    global_PVs['Cam1_MaxSizeY'] = PV(variableDict['IOC_Prefix'] + 'cam1:MaxSizeY_RBV')

    global_PVs['Cam1_SizeX_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeX_RBV')
    global_PVs['Cam1_SizeY_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeY_RBV')

    global_PVs['Cam1_SizeX'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeX')
    global_PVs['Cam1_SizeY'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeY')

    global_PVs['Cam1_NumImages'] = PV(variableDict['IOC_Prefix'] + 'cam1:NumImages')     
    global_PVs['Cam1_ArrayCallbacks'] = PV(variableDict['IOC_Prefix'] + 'cam1:ArrayCallbacks')
    global_PVs['Cam1_TriggerMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:TriggerMode')           
    global_PVs['Cam1_DetectorState_RBV'] = PV(variableDict['IOC_Prefix'] + 'cam1:DetectorState_RBV')

    global_PVs['Cam1_FrameType'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType')    
    global_PVs['Cam1_FrameTypeZRST'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType.ZRST')
    global_PVs['Cam1_FrameTypeONST'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType.ONST')
    global_PVs['Cam1_FrameTypeTWST'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType.TWST')

    global_PVs['Cam1_NDAttributesFile'] = PV(variableDict['IOC_Prefix'] + 'cam1:NDAttributesFile')

    global_PVs['HDF1_AutoSave'] = PV(variableDict['IOC_Prefix'] + 'HDF1:AutoSave')
    global_PVs['HDF1_AutoIncrement'] = PV(variableDict['IOC_Prefix'] + 'HDF1:AutoIncrement')
    global_PVs['HDF1_EnableCallbacks'] = PV(variableDict['IOC_Prefix'] + 'HDF1:EnableCallbacks')  
    global_PVs['HDF1_Capture'] = PV(variableDict['IOC_Prefix'] + 'HDF1:Capture')       
    global_PVs['HDF1_NumCapture'] = PV(variableDict['IOC_Prefix'] + 'HDF1:NumCapture')       
    global_PVs['HDF1_NumCapture_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:NumCapture_RBV') 
    global_PVs['HDF1_NumCaptured_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:NumCaptured_RBV')
    global_PVs['HDF1_FileName'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileName')   
    global_PVs['HDF1_FileNumber'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileNumber')   
    global_PVs['HDF1_FilePath'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FilePath')
    global_PVs['HDF1_FileTemplate'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileTemplate')       
    global_PVs['HDF1_FileWriteMode'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileWriteMode')
    global_PVs['HDF1_FullFileName_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FullFileName_RBV')
    global_PVs['HDF1_XMLFileName'] = PV(variableDict['IOC_Prefix'] + 'HDF1:XMLFileName')               
    global_PVs['HDF1_XMLFileName_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:XMLFileName_RBV')        
    global_PVs['Image1_EnableCallbacks'] = PV(variableDict['IOC_Prefix'] + 'image1:EnableCallbacks')


def setPSO(global_PVs, variableDict):
    print(' ')
    print('  *** Set PSO')

    acclTime = 1.0 * variableDict['SlewSpeed']/variableDict['AcclRot']
    scanDelta = 1.0*(variableDict['SampleRotEnd'] - variableDict['SampleRotStart'])/variableDict['Projections']

    global_PVs['Fly_StartPos'].put(str(variableDict['SampleRotStart']), wait=True, timeout=1000.0)                
    global_PVs['Fly_EndPos'].put(str(variableDict['SampleRotEnd']), wait=True, timeout=1000.0)
    global_PVs['Motor_SampleRot_Velo'].put(str(variableDict['SlewSpeed']), wait=True, timeout=1000.0)
    global_PVs['Fly_SlewSpeed'].put(str(variableDict['SlewSpeed']), wait=True, timeout=1000.0)
    global_PVs['Motor_SampleRot_Accl'].put(str(acclTime), wait=True, timeout=1000.0)
    global_PVs['Fly_ScanDelta'].put(str(scanDelta), wait=True, timeout=1000.0)    
    print('  *** Set PSO: Done!')


def dimaxInit(global_PVs, variableDict):
    print(' ')
    print('  *** Init PCO Dimax')                        

    global_PVs['HDF1_EnableCallbacks'].put('Enable', wait=True, timeout=1000.0)  
    global_PVs['Cam1_ArrayCallbacks'].put('Enable', wait=True, timeout=1000.0)  
    
    global_PVs['Cam1_PCOCancelDump'].put('1', wait=True, timeout=1000.0)                    
    global_PVs['HDF1_Capture'].put('Done', wait=True, timeout=1000.0) 
    global_PVs['HDF1_NumCaptured_RBV'].put('0', wait=True, timeout=1000.0)    

    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)    
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOLiveView'].put('Yes', wait=True, timeout=1000.0)    
    
    print('  *** Init PCO Dimax: Done!')                        
      

def dimaxAcquisition(global_PVs, variableDict):
    print(' ')
    print('  *** Acquisition')
    print('      *** Projections')

    global_PVs['Cam1_FrameType'].put(FrameTypeData, wait=True, timeout=1000.0) 
    time.sleep(1)
    global_PVs['Cam1_PCODumpCounter'].put(str(0), wait=True, timeout=1000.0)     
    time.sleep(1)

    if (variableDict['SampleInOutVertical']):
        global_PVs['Motor_SampleY'].put(str(variableDict['SampleYIn']), wait=True, timeout=1000.0)
    else:
        global_PVs['Motor_SampleX'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0)
        if (variableDict['UseFurnace']):
            global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYIn']), wait=True, timeout=1000.0)

    # print('          *** Wait (s) %s ' % str(variableDict['StartSleep_s']))   
    # time.sleep(variableDict['StartSleep_s']) 

    global_PVs['Motor_SampleRot_Velo'].put('50.00000', wait=True, timeout=1000.0)
    global_PVs['Motor_SampleRot'].put('0.00000', wait=False, timeout=1000.0)   

    open_shutters(global_PVs, variableDict)
    global_PVs['Fly_Taxi'].put('Taxi', wait=True, timeout=1000.0)
    global_PVs['Fly_Run'].put('Fly', wait=True, timeout=1000.0) 
    close_shutters(global_PVs, variableDict)

##    if epics.caget(PSO+":fly.VAL") == 0 & clShutter == 1:               
##        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0) 

    # rotCurrPos = global_PVs['Motor_SampleRot'].get()

    # global_PVs['Motor_SampleRot_Set'].put(str(1), wait=True, timeout=1000.0)       
    # global_PVs['Motor_SampleRot'].put(str(1.0*rotCurrPos%360.0), wait=True, timeout=1000.0) 
    # global_PVs['Motor_SampleRot_Set'].put(str(0), wait=True, timeout=1000.0)  

    # global_PVs['Motor_SampleRot_Velo'].put("50.00000", wait=True, timeout=1000.0)
    # global_PVs['Motor_SampleRot_Accl'].put('1.00000', wait=True, timeout=1000.0)                
    # global_PVs['Motor_SampleRot'].put("0.00000", wait=False, timeout=1000.0)   
    
    rotary_to_start_position(global_PVs, variableDict)

    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)    
    time.sleep(1)

    # fast shutter for radiation sensitive samples
##    global_PVs['Fast_Shutter'].put('0', wait=True, timeout=1000.0)   
    dimaxDump(global_PVs, variableDict)                                
    while (global_PVs['HDF1_NumCaptured_RBV'].get() != global_PVs['Cam1_PCOImgs2Dump_RBV'].get()):   
        #print(global_PVs['HDF1_NumCaptured_RBV'].get(), global_PVs['Cam1_PCOImgs2Dump_RBV'].get())
        time.sleep(1)                    
    print('          *** PCO Dimax dump: Done!')   
    global_PVs['HDF1_Capture'].put('Done',wait=True,timeout=1000.0)
    print('      *** Projections: Done!')


def dimaxAcquireFlat(global_PVs, variableDict): 

    print('      *** White Fields')

    global_PVs['Fly_ScanControl'].put('Standard', wait=True, timeout=1000.0)                

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
                

    time.sleep(1)
    global_PVs['HDF1_NumCapture'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)
    global_PVs['HDF1_NumCapture_RBV'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)                
    global_PVs['HDF1_AutoSave'].put('Yes', wait=True, timeout=1000.0)
    global_PVs['HDF1_FileWriteMode'].put('Stream', wait=True, timeout=1000.0)
    global_PVs['HDF1_Capture'].put('Capture', wait=False, timeout=1000.0)

    global_PVs['Cam1_FrameType'].put(FrameTypeWhite, wait=True, timeout=1000.0)     
    time.sleep(1) 
    global_PVs['Cam1_NumImages'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)   
    global_PVs['Cam1_PCOReady2Acquire'].put('0', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)   

    open_shutters(global_PVs, variableDict)
    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)  
    close_shutters(global_PVs, variableDict)

    global_PVs['Cam1_PCOImgs2Dump'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)    
    global_PVs['Cam1_PCOImgs2Dump_RBV'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)                
    global_PVs['Cam1_PCODumpCameraMemory'].put(1, wait=True, timeout=1000.0)
    time.sleep(10)     
    # if (variableDict['SampleInOutVertical']):
    #     global_PVs['Motor_SampleY'].put(str(variableDict['SampleYIn']), wait=True, timeout=1000.0)                
    # else:
    #     global_PVs['Motor_SampleX'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0)                
    #     if (variableDict['UseFurnace']):
    #         global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYIn']), wait=True, timeout=1000.0)

    lobal_PVs['HDF1_Capture'].put('Done',wait=True,timeout=1000.0)
    print('      *** White Fields: Done!')


def dimaxAcquireDark(global_PVs, variableDict): 
    print("      *** Dark Fields") 

    global_PVs['Fly_ScanControl'].put('Standard', wait=True, timeout=1000.0)                
    global_PVs['HDF1_NumCapture'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)
    global_PVs['HDF1_NumCapture_RBV'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)                
##    global_PVs['HDF1_FilePath'].put(filepath, wait=True, timeout=1000.0)
    global_PVs['HDF1_AutoSave'].put('Yes', wait=True, timeout=1000.0)
    global_PVs['HDF1_FileWriteMode'].put('Stream', wait=True, timeout=1000.0)
    global_PVs['HDF1_Capture'].put('Capture', wait=False, timeout=1000.0)
    global_PVs['Cam1_FrameType'].put(FrameTypeDark, wait=True, timeout=1000.0)             
    global_PVs['Cam1_NumImages'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)            
    global_PVs['Cam1_PCOReady2Acquire'].put('0', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)   

    close_shutters(global_PVs, variableDict)
    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)  
    
    global_PVs['Cam1_PCOImgs2Dump'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)    
    global_PVs['Cam1_PCOImgs2Dump_RBV'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)                
    global_PVs['Cam1_PCODumpCameraMemory'].put(1, wait=True, timeout=1000.0)
    time.sleep(10)
    global_PVs['HDF1_Capture'].put('Done',wait=True,timeout=1000.0)
    print('      *** Dark Fields: Done!')
    print('  *** Acquisition: Done!')        

                
def dimaxSet(global_PVs, variableDict, fname):

    print(' ')
    print('  *** Set PCO Dimax')

    set_frame_type(global_PVs, variableDict)

    numImage = variableDict['Projections']

    frate = int(1.0*numImage/(1.0*(variableDict['SampleRotEnd'] - variableDict['SampleRotStart'])/variableDict['SlewSpeed']) + 20)

    global_PVs['Cam1_PCOLiveView'].put('No', wait=True, timeout=1000.0)             
    global_PVs['Cam1_NumImages'].put(str(numImage-0), wait=True, timeout=1000.0)                
    global_PVs['Cam1_PCONumImgsSeg0_RBV'].put('0', wait=True, timeout=1000.0)                    
    global_PVs['Cam1_PCOIsFrameRateMode'].put('DelayExp', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOSetFrameRate'].put(str(frate+.1), wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOSetFrameRate'].put(str(frate), wait=True, timeout=1000.0)                
    global_PVs['Cam1_AcquireTime'].put(str(variableDict['ExposureTime']), wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Soft/Ext', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOReady2Acquire'].put('0', wait=True, timeout=1000.0)
    global_PVs['Cam1_Acquire'].put('Acquire', wait=False, timeout=1000.0)
    global_PVs['HDF1_AutoIncrement'].put('Yes', wait=True, timeout=1000.0) 
    global_PVs['HDF1_NumCaptured_RBV'].put('0', wait=True, timeout=1000.0)                  

    ### from the edge set
    global_PVs['HDF1_FileTemplate'].put('%s%s_%4.4d.h5', wait=True, timeout=1000.0)                
    global_PVs['HDF1_NumCapture'].put(str(numImage), wait=True, timeout=1000.0)                
    global_PVs['HDF1_NumCapture_RBV'].put(str(numImage), wait=True, timeout=1000.0)  
    global_PVs['HDF1_NumCaptured_RBV'].put('0', wait=True, timeout=1000.0)                
    ### from the edge set
    
    if fname is not None:
        global_PVs['HDF1_FileName'].put(fname)

    print('  *** Set PCO Dimax: Done!')
#    time.sleep(2)    
    #    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(numImage), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    


def dimaxSet2D(global_PVs, variableDict, fname):

    print(' ')
    print('  *** Set PCO Dimax 2D')

    set_frame_type(global_PVs, variableDict)

    numImage = variableDict['Projections'] + variableDict['NumDarkImages'] + variableDict['NumWhiteImages']

    frate = 1.0 / variableDict['ExposureTime'] 
    
    global_PVs['Cam1_PCOLiveView'].put('No', wait=True, timeout=1000.0)             
    global_PVs['Cam1_NumImages'].put(str(numImage), wait=True, timeout=1000.0)                
    global_PVs['Cam1_PCONumImgsSeg0_RBV'].put('0', wait=True, timeout=1000.0)                    
    global_PVs['Cam1_PCOIsFrameRateMode'].put('DelayExp', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOSetFrameRate'].put(str(frate+.1), wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOSetFrameRate'].put(str(frate), wait=True, timeout=1000.0)                
    global_PVs['Cam1_AcquireTime'].put(str(variableDict['ExposureTime']), wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOReady2Acquire'].put('0', wait=True, timeout=1000.0)
    global_PVs['Cam1_Acquire'].put('Acquire', wait=False, timeout=1000.0)
    global_PVs['HDF1_AutoIncrement'].put('Yes', wait=True, timeout=1000.0) 
    global_PVs['HDF1_NumCaptured_RBV'].put('0', wait=True, timeout=1000.0)                  

    ### from the edge set
    global_PVs['HDF1_FileTemplate'].put('%s%s_%4.4d.h5', wait=True, timeout=1000.0)                
    global_PVs['HDF1_NumCapture'].put(str(numImage), wait=True, timeout=1000.0)                
    global_PVs['HDF1_NumCapture_RBV'].put(str(numImage), wait=True, timeout=1000.0)  
    global_PVs['HDF1_NumCaptured_RBV'].put('0', wait=True, timeout=1000.0)                
    ### from the edge set
    
    if fname is not None:
        global_PVs['HDF1_FileName'].put(fname)

    print('  *** Set PCO Dimax 2D: Done!')
#    time.sleep(2)    
    #    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(numImage), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    


def dimaxAcquisition2D(global_PVs, variableDict):

    open_shutters(global_PVs, variableDict)

    print(' ')
    print('  *** Acquisition')
    print('      *** Projections')

    global_PVs['Cam1_FrameType'].put(FrameTypeData, wait=True, timeout=1000.0) 
    time.sleep(1)
    global_PVs['Cam1_PCODumpCounter'].put(str(0), wait=True, timeout=1000.0)     
    time.sleep(1)

    if (variableDict['SampleMoveEnabled']):
        if (variableDict['SampleInOutVertical']):
            global_PVs['Motor_SampleY'].put(str(variableDict['SampleYIn']), wait=True, timeout=1000.0)                
        else:
            global_PVs['Motor_SampleX'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0) 
            if (variableDict['UseFurnace']):
                global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYIn']), wait=True, timeout=1000.0)

    # print('          *** Wait (s)', str(variableDict['StartSleep_s']))   
    # time.sleep(variableDict['StartSleep_s']) 

    frate = 1.0 / variableDict['ExposureTime']                        
    
    global_PVs['Cam1_NumImages'].put(str(variableDict['Projections']), wait=True, timeout=1000.0)                
    global_PVs['Cam1_PCONumImgsSeg0_RBV'].put('0', wait=True, timeout=1000.0)                    
    global_PVs['Cam1_PCOIsFrameRateMode'].put('FrateExp', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOSetFrameRate'].put(str(frate), wait=True, timeout=1000.0)
    global_PVs['Cam1_AcquireTime'].put(str(variableDict['ExposureTime']), wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOReady2Acquire'].put('0', wait=True, timeout=1000.0)
    while (global_PVs['Cam1_PCONumImgsSeg0_RBV'].get() != global_PVs['Cam1_PCOMaxImgsSeg0_RBV'].get()):    
        time.sleep(1)        
    print('      *** Projections: Done!')

    close_shutters(global_PVs, variableDict)

    dimaxDump(global_PVs, variableDict)                                
    while (global_PVs['HDF1_NumCaptured_RBV'].get() != global_PVs['Cam1_PCOImgs2Dump_RBV'].get()):   
        time.sleep(1)                    
    print('          *** PCO Dimax dump: Done!')   
    #global_PVs['HDF1_Capture'].put('Done',wait=True,timeout=1000.0)


def dimaxAcquireFlat2D(global_PVs, variableDict): 

    print('      *** White Fields')

    # global_PVs['Fly_ScanControl'].put('Standard', wait=True, timeout=1000.0)                

    if (variableDict['SampleMoveEnabled']):
        if (variableDict['SampleInOutVertical']):
            global_PVs['Motor_SampleY'].put(str(variableDict['SampleYOut']), wait=True, timeout=1000.0)                
        else:
            if (variableDict['UseFurnace']):
                global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYOut']), wait=True, timeout=1000.0)
            global_PVs['Motor_SampleX'].put(str(variableDict['SampleXOut']), wait=True, timeout=1000.0)

    time.sleep(1)
    # global_PVs['HDF1_NumCapture'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)
    # global_PVs['HDF1_NumCapture_RBV'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)                
    # global_PVs['HDF1_AutoSave'].put('Yes', wait=True, timeout=1000.0)
    # global_PVs['HDF1_FileWriteMode'].put('Stream', wait=True, timeout=1000.0)
    # global_PVs['HDF1_Capture'].put('Capture', wait=False, timeout=1000.0)

    global_PVs['Cam1_FrameType'].put(FrameTypeWhite, wait=True, timeout=1000.0)     
    time.sleep(1) 
    global_PVs['Cam1_NumImages'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)   
    global_PVs['Cam1_PCOReady2Acquire'].put('0', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)   

    open_shutters(global_PVs, variableDict)
    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)  

    global_PVs['Cam1_PCOImgs2Dump'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)    
    global_PVs['Cam1_PCOImgs2Dump_RBV'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)                
    global_PVs['Cam1_PCODumpCameraMemory'].put(1, wait=True, timeout=1000.0)
    time.sleep(10)

    # if (variableDict['SampleInOutVertical']):
    #     global_PVs['Motor_SampleY'].put(str(variableDict['SampleYIn']), wait=True, timeout=1000.0) 
    # else:
    #     global_PVs['Motor_SampleX'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0) 
    #     if (variableDict['UseFurnace']):
    #         global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYIn']), wait=True, timeout=1000.0)
                 
#    global_PVs['HDF1_Capture'].put('Done',wait=True,timeout=1000.0)
    print('      *** White Fields: Done!')


def dimaxAcquireDark2D(global_PVs, variableDict): 
    print("      *** Dark Fields") 

    # global_PVs['Fly_ScanControl'].put('Standard', wait=True, timeout=1000.0)                
    # global_PVs['HDF1_NumCapture'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)
    # global_PVs['HDF1_NumCapture_RBV'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)                
    # global_PVs['HDF1_AutoSave'].put('Yes', wait=True, timeout=1000.0)
    # global_PVs['HDF1_FileWriteMode'].put('Stream', wait=True, timeout=1000.0)
    # global_PVs['HDF1_Capture'].put('Capture', wait=False, timeout=1000.0)

    global_PVs['Cam1_FrameType'].put(FrameTypeDark, wait=True, timeout=1000.0)             
    time.sleep(1) 
    global_PVs['Cam1_NumImages'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)            
    global_PVs['Cam1_PCOReady2Acquire'].put('0', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)   

    close_shutters(global_PVs, variableDict)
    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)  
    
    global_PVs['Cam1_PCOImgs2Dump'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)    
    global_PVs['Cam1_PCOImgs2Dump_RBV'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)                
    global_PVs['Cam1_PCODumpCameraMemory'].put(1, wait=True, timeout=1000.0)
    time.sleep(10)
#    global_PVs['HDF1_Capture'].put('Done',wait=True,timeout=1000.0)
    print('      *** Dark Fields: Done!')
    print('  *** Acquisition: Done!')        


def dimaxDump(global_PVs, variableDict):
    print(' ')
    print('          *** PCO Dimax dump')                        
    global_PVs['HDF1_NumCapture'].put(str(global_PVs['Cam1_PCOMaxImgsSeg0_RBV'].get()), wait=True, timeout=1000.0)    
    
    global_PVs['HDF1_NumCapture_RBV'].put(str(global_PVs['Cam1_PCOMaxImgsSeg0_RBV'].get()), wait=True, timeout=1000.0)
    global_PVs['HDF1_AutoSave'].put('Yes', wait=True, timeout=1000.0)
    global_PVs['HDF1_FileWriteMode'].put('Stream', wait=True, timeout=1000.0)

    time.sleep(5)
    global_PVs['HDF1_Capture'].put('Capture', wait=False, timeout=1000.0) 
    global_PVs['HDF1_Capture'].put('Capture', wait=False, timeout=1000.0)  
    time.sleep(5)     
    global_PVs['Cam1_PCODumpCameraMemory'].put(1, wait=True, timeout=1000.0)                                
#    while epics.caget(camPrefix + ":HDF1:Capture_RBV.VAL") != 'Capturing':
#         epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)   
#         time.sleep(1)                     
    
def rotary_to_start_position(global_PVs, variableDict):


    if(global_PVs['Motor_SampleRot'].get() == variableDict['SampleRotStart']):
        print(' ')
        print('  *** Rotary already at the start position')                        
        return
    else:    
        print(' ')
        print('  *** Homing the rotary stage')                        

        global_PVs['Motor_SampleRot_Stop'].put(1, wait=True, timeout=1000.0)
        global_PVs['Motor_SampleRot_Set'].put('Set', wait=True, timeout=1000.0) 
        global_PVs['Motor_SampleRot'].put(1.0*global_PVs['Motor_SampleRot'].get()%360.0, wait=True, timeout=1000.0)
        global_PVs['Motor_SampleRot_Set'].put('Use', wait=True, timeout=1000.0) 

        global_PVs['Motor_SampleRot_Velo'].put('30', wait=True, timeout=1000.0)    
        global_PVs['Motor_SampleRot_Accl'].put('3', wait=True, timeout=1000.0)                
        global_PVs['Motor_SampleRot'].put(str(variableDict['SampleRotStart']), wait=True, timeout=1000.0)
        print('  *** Homing the rotary stage: Done!')                        

   
def edgeInit(global_PVs, variableDict):
    print(' ')
    print('  *** Init PCO Edge')                        
    global_PVs['HDF1_EnableCallbacks'].put(1, wait=True, timeout=1000.0)   
    global_PVs['HDF1_Capture'].put('Done', wait=True, timeout=1000.0) 
    global_PVs['HDF1_NumCaptured_RBV'].put('0', wait=True, timeout=1000.0)    

# not working yet ...
#    if global_PVs['HDF1_XMLFileName_RBV'].get(as_string=True) is not 'PCOLayout.xml':        
#        global_PVs['HDF1_XMLFileName'].put('PCOLayout.xml', wait=True, timeout=1000.0)                 
#    if global_PVs['Cam1_NDAttributesFile'].get(as_string=True) is not 'PCODetectorAttributes.xml':        
#        global_PVs['Cam1_NDAttributesFile'].put('PCODetectorAttributes.xml', wait=True, timeout=1000.0)                 


    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)    
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)
    global_PVs['Cam1_ImageMode'].put('Continuous', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOEdgeFastscan'].put('Normal', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOIsFrameRateMode'].put(0, wait=True, timeout=1000.0)    
    global_PVs['Cam1_AcquireTime'].put(0.2, wait=True, timeout=1000.0)
    global_PVs['Image1_EnableCallbacks'].put('Enable', wait=True, timeout=1000.0)
    
    print('  *** Init PCO Edge: Done!')


def edgeTest(global_PVs, variableDict):
    print(' ')
    print('  *** Testing PCO Edge camera')
    global_PVs['Cam1_ArrayCallbacks'].put('Enable', wait=True, timeout=1000.0)
    global_PVs['Cam1_NumImages'].put('10', wait=True, timeout=1000.0)
    global_PVs['Cam1_ImageMode'].put('Multiple', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOGlobalShutter'].put('Rolling', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOEdgeFastscan'].put('Normal', wait=True, timeout=1000.0)                
    global_PVs['Cam1_AcquireTime'].put("0.001000", wait=True, timeout=1000.0)
    global_PVs['Cam1_SizeX'].put(variableDict['roiSizeX'], wait=True, timeout=1000.0)
    global_PVs['Cam1_SizeY'].put(variableDict['roiSizeY'], wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)    
    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)     
    print('  *** Testing PCO Edge camera: Done!')


def edgeSet(global_PVs, variableDict, fname):    
    print(' ')
    print('  *** Set PCO Edge')

    set_frame_type(global_PVs, variableDict)

    numImage = variableDict['Projections'] + variableDict['NumDarkImages'] + variableDict['NumWhiteImages']   

    frate =  int(1.0*variableDict['Projections']/(1.0*(variableDict['SampleRotEnd'] - \
             variableDict['SampleRotStart'])/variableDict['SlewSpeed']) + 5)
             
    global_PVs['Cam1_PCOIsFrameRateMode'].put('DelayExp', wait=True, timeout=1000.0)
    global_PVs['Cam1_AcquirePeriod'].put('0', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOSetFrameRate'].put(str(frate+1), wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOSetFrameRate'].put(str(frate), wait=True, timeout=1000.0)                    
    global_PVs['HDF1_AutoIncrement'].put('Yes', wait=True, timeout=1000.0)
    global_PVs['HDF1_NumCapture'].put(str(numImage), wait=True, timeout=1000.0)                
    global_PVs['HDF1_NumCapture_RBV'].put(str(numImage), wait=True, timeout=1000.0)  
    global_PVs['HDF1_NumCaptured_RBV'].put('0', wait=True, timeout=1000.0)                

    if fname is not None:
        global_PVs['HDF1_FileName'].put(fname)

    global_PVs['HDF1_FileTemplate'].put('%s%s_%4.4d.h5', wait=True, timeout=1000.0)                
    global_PVs['HDF1_AutoSave'].put('Yes', wait=True, timeout=1000.0)
    global_PVs['HDF1_FileWriteMode'].put('Stream', wait=True, timeout=1000.0)
    global_PVs['HDF1_Capture'].put('Capture', wait=False, timeout=1000.0)
    global_PVs['Cam1_NumImages'].put(str(numImage), wait=True, timeout=1000.0)                                
    global_PVs['Cam1_ImageMode'].put('Multiple', wait=True, timeout=1000.0)
    global_PVs['Cam1_AcquireTime'].put(str(variableDict['ExposureTime']), wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Soft/Ext', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOReady2Acquire'].put('0', wait=True, timeout=1000.0)
    global_PVs['Cam1_Acquire'].put('Acquire', wait=False, timeout=1000.0)            
    print('  *** Set PCO Edge: Done!')


def edgeAcquisition(global_PVs, variableDict):

    rotary_to_start_position(global_PVs, variableDict)                 

    print(' ')
    print('  *** Acquisition')
    print('      *** Projections')

    global_PVs['Cam1_FrameType'].put(FrameTypeData, wait=True, timeout=1000.0) 
    time.sleep(2)    

    if (variableDict['SampleInOutVertical']):
        global_PVs['Motor_SampleY'].put(str(variableDict['SampleYIn']), wait=True, timeout=1000.0)                    
    else:
        global_PVs['Motor_SampleX'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0) 
        if (variableDict['UseFurnace']):
            global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYIn']), wait=True, timeout=1000.0)

    # print('          *** Wait (s): ', str(variableDict['StartSleep_s']))   
    # time.sleep(variableDict['StartSleep_s']) 

    print('          *** Fly Scan')   
    global_PVs['Fly_Taxi'].put('Taxi', wait=True, timeout=1000.0)
    global_PVs['Fly_Run'].put('Fly', wait=True, timeout=1000.0) 
        
    # wait for hdf plugin to dump images to disk
    while (global_PVs['HDF1_NumCaptured_RBV'].get() != global_PVs['Cam1_NumImagesCounter_RBV'].get()):      
        time.sleep(1)                    
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)             
    print('      *** Projections: Done!')


def edgeAcquireFlat(global_PVs, variableDict):    
    print('      *** White Fields')
    if (variableDict['SampleMoveEnabled']):
        if (variableDict['SampleInOutVertical']):
            global_PVs['Motor_SampleY'].put(str(variableDict['SampleYOut']), wait=True, timeout=1000.0)                
        else:
            if (variableDict['UseFurnace']):
                global_PVs['Motor_FurnaceY'].put(str(variableDict['FurnaceYOut']), wait=True, timeout=1000.0)
            global_PVs['Motor_SampleX'].put(str(variableDict['SampleXOut']), wait=True, timeout=1000.0)
       
    global_PVs['Fly_ScanControl'].put('Standard', wait=True, timeout=1000.0)                
    global_PVs['Cam1_FrameType'].put(FrameTypeWhite, wait=True, timeout=1000.0)     
    time.sleep(2)    
    global_PVs['Cam1_NumImages'].put(str(variableDict['NumWhiteImages']), wait=True, timeout=1000.0)   
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)   
    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)  
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)

    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)             
    print('      *** White Fields: Done!')


def edgeAcquireDark(global_PVs, variableDict):    
    print("      *** Dark Fields") 
    global_PVs['Fly_ScanControl'].put('Standard', wait=True, timeout=1000.0)
    global_PVs['Cam1_FrameType'].put(FrameTypeDark, wait=True, timeout=1000.0)             

    global_PVs['Cam1_NumImages'].put(str(variableDict['NumDarkImages']), wait=True, timeout=1000.0)   
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)            

    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)       
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)    
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)
    print('      *** Dark Fields: Done!')

    rotary_to_start_position(global_PVs, variableDict)                 
    print(' ')
    print('  *** Acquisition: Done!')        

 

def set_frame_type(global_PVs, variableDict):
    global_PVs['Cam1_FrameTypeZRST'].put('/exchange/data')
    global_PVs['Cam1_FrameTypeONST'].put('/exchange/data_dark')
    global_PVs['Cam1_FrameTypeTWST'].put('/exchange/data_white')

    
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
    

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


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
 
   
    mid_detector = global_PVs['Cam1_MaxSizeX'].get() / 2.0
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
              
      
def change2White():
    print(' ')
    print('  *** change2white')
    print('    *** closing shutter')
    global_PVs['ShutterA_Close'].put(1, wait=True)
    wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
# #    epics.caput(BL+":m33.VAL",107.8, wait=False, timeout=1000.0)                



    print('    *** moving Filters')
    global_PVs['Filters'].put(0, wait=True)
    print('    *** moving Mirror')
    global_PVs['Mirr_Ang'].put(0, wait=True)
    time.sleep(1) 
    global_PVs['Mirr_YAvg'].put(-4, wait=True)
    time.sleep(1) 
    print('    *** moving DMM X')                                          
    global_PVs['DMM_USX'].put(50, wait=False)
    global_PVs['DMM_DSX'].put(50, wait=True)
    time.sleep(3)                
    print('    *** moving DMM Y')
    global_PVs['DMM_USY_OB'].put(-16, wait=False)
    global_PVs['DMM_USY_IB'].put(-16, wait=False)
    global_PVs['DMM_DSY'].put(-16, wait=True)
    time.sleep(3) 
                                 
#     epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)    
    print('    *** moving XIA Slits')
    global_PVs['XIASlit'].put(-1.65, wait=True)
    print('  *** change2white: Done!')
                    

def change2Mono():
    print(' ')
    print('  *** change2mono')
    print('    *** closing shutter')
    global_PVs['ShutterA_Close'].put(1, wait=True)
    wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)

# #    epics.caput(BL+":m33.VAL",121, wait=False, timeout=1000.0)                    
    print('    *** moving Filters')
    global_PVs['Filters'].put(0, wait=True)
    print('    *** moving Mirror')
    global_PVs['Mirr_YAvg'].put(0, wait=True)
    time.sleep(1) 
    global_PVs['Mirr_Ang'].put(2.657, wait=True)
    time.sleep(1) 

    print('    *** moving DMM Y')
    global_PVs['DMM_USY_OB'].put(-0.1, wait=False)
    global_PVs['DMM_USY_IB'].put(-0.1, wait=False)
    global_PVs['DMM_DSY'].put(-0.1, wait=True)
    time.sleep(3) 
                                 
    print('    *** moving DMM X')                                          
    global_PVs['DMM_USX'].put(81.5, wait=False)
    global_PVs['DMM_DSX'].put(81.5, wait=True)
    time.sleep(3)                
#     epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)    
    print('    *** moving XIA Slits')
    global_PVs['XIASlit'].put(30.35, wait=True)
    print('  *** change2mono: Done!')
               

def change2Pink(ang=2.657):

    Mirr_Ang_list = np.array([1.500,1.800,2.000,2.100,2.657])

    angle_calibrated = find_nearest(Mirr_Ang_list, ang)
    print(' ')
    print('   *** Angle entered is %s rad, the closest calibrate angle is %s' % (ang, angle_calibrated))

    Mirr_YAvg_list = np.array([-0.1,0.0,0.0,0.0,0.0])

    DMM_USY_OB_list = np.array([-10,-10,-10,-10,-10])
    DMM_USY_IB_list = np.array([-10,-10,-10,-10,-10])
    DMM_DSY_list = np.array([-10,-10,-10,-10,-10])

    DMM_USX_list = np.array([50,50,50,50,50])
    DMM_DSX_list = np.array([50,50,50,50,50])

    XIASlit_list = np.array([8.75,11.75,13.75,14.75,18.75])    

    Slit1Hcenter_list = np.array([4.85,4.85,7.5,7.5,7.2])

    Filter_list = np.array([0,0,0,0,0])

    idx = np.where(Mirr_Ang_list==angle_calibrated)                
    if idx[0].size == 0:
        print ('     *** ERROR: there is no specified calibrated calibrate in the calibrated angle lookup table. please choose a calibrated angle.')
        return    0                            

    Mirr_Ang = Mirr_Ang_list[idx[0][0]] 
    Mirr_YAvg = Mirr_YAvg_list[idx[0][0]]

    DMM_USY_OB = DMM_USY_OB_list[idx[0][0]] 
    DMM_USY_IB = DMM_USY_IB_list[idx[0][0]]
    DMM_DSY = DMM_DSY_list[idx[0][0]]

    DMM_USX = DMM_USX_list[idx[0][0]]
    DMM_DSX = DMM_DSX_list[idx[0][0]]

    XIASlit = XIASlit_list[idx[0][0]]          
    Slit1Hcenter = Slit1Hcenter_list[idx[0][0]] 

    Filter = Filter_list[idx[0][0]]

    print('   *** Angle is set at %s rad' % angle_calibrated)                
    print ('     *** Moving Stages ...')                

    print ('     *** Filter %s ' % Filter)
    print ('     *** Mirr_YAvg %s mm' % Mirr_YAvg)
    print ('     *** Mirr_Ang %s rad' % Mirr_Ang)
    
    print ('     *** DMM_USX %s mm' % DMM_USX)
    print ('     *** DMM_DSX %s mm' % DMM_DSX)

    print ('     *** DMM_USY_OB %s mm' % DMM_USY_OB) 
    print ('     *** DMM_USY_IB %s mm' % DMM_USY_IB)
    print ('     *** DMM_DSY %s mm' % DMM_DSY)

    print ('     *** Slit1Hcenter %s mm' % Slit1Hcenter)          
    print ('     *** XIASlit %s mm' % XIASlit)          

    print(' ')
    print('  *** change2pink')
#    print('    *** closing shutter')
#    global_PVs['ShutterA_Close'].put(1, wait=True)
#    wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
#    print('    *** moving Filters')
#    global_PVs['Filters'].put(Filter, wait=True)
#    print('    *** moving Mirror')
#    global_PVs['Mirr_YAvg'].put(Mirr_YAvg, wait=True)
#    time.sleep(1) 
#    global_PVs['Mirr_Ang'].put(Mirr_YAvg, wait=True)
#    time.sleep(1) 
#    print('    *** moving DMM X')                                          
#    global_PVs['DMM_USX'].put(DMM_USX, wait=False)
#    global_PVs['DMM_DSX'].put(DMM_DSX, wait=True)
#    time.sleep(3)                
#    print('    *** moving DMM Y')
#    global_PVs['DMM_USY_OB'].put(DMM_USY_OB, wait=False)
#    global_PVs['DMM_USY_IB'].put(DMM_USY_IB, wait=False)
#    global_PVs['DMM_DSY'].put(DMM_DSY, wait=True)
#    time.sleep(3) 
#         epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)    
#    print('    *** moving XIA Slits')
#    global_PVs['XIASlit'].put(XIASlit, wait=True)
    print('  *** change2pink: Done!')


def setEnergy(energy = 24.9):

    caliEng_list = np.array([55.00, 50.00, 45.00, 40.00, 35.00, 31.00, 27.40, 24.90, 22.70, 21.10, 20.20, 18.90, 17.60, 16.80, 16.00, 15.00, 14.40])

    energy_calibrated = find_nearest(caliEng_list, energy)
    print(' ')
    print('   *** Energy entered is %s keV, the closest calibrate energy is %s' % (energy, energy_calibrated))

    Mirr_Ang_list = np.array([1.200,1.500,1.500,1.500,2.000,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657])
    Mirr_YAvg_list = np.array([-0.2,-0.2,-0.2,-0.2,-0.2,0.0,0.0,-0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])

    DMM_USY_OB_list = np.array([-5.1,-5.1,-5.1,-5.1,-3.8,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1])
    DMM_USY_IB_list = np.array([-5.1,-5.1,-5.1,-5.1,-3.8,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1])  
    DMM_DSY_list = np.array([-5.1,-5.1,-5.1,-5.1,-3.7,-0.1,-0.1,-0.2,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1]) 

    USArm_list =   np.array([0.95,  1.00,  1.05,  1.10,  1.25,  1.10,  1.15,  1.20,  1.25,  1.30,  1.35,  1.40,  1.45,  1.50,  1.55,  1.60,  1.65])    
    DSArm_list =  np.array([ 0.973, 1.022, 1.072, 1.124, 1.2745,1.121, 1.169, 1.2235,1.271, 1.3225,1.373, 1.4165,1.472, 1.5165,1.568, 1.6195,1.67])

    M2Y_list =     np.array([11.63, 12.58, 13.38, 13.93, 15.57, 12.07, 13.71, 14.37, 15.57, 15.67, 17.04, 17.67, 18.89, 19.47, 20.57, 21.27, 22.27]) 
    DMM_USX_list = np.array([27.5,27.5,27.5,27.5,27.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5])
    DMM_DSX_list = np.array([27.5,27.5,27.5,27.5,27.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5])
    XIASlit_list = np.array([21.45, 24.05, 25.05, 23.35, 26.35, 28.35, 29.35, 30.35, 31.35, 32.35, 33.35, 34.35, 34.35, 52.35, 53.35, 54.35, 51.35])    
    
    idx = np.where(caliEng_list==energy_calibrated)                
    if idx[0].size == 0:
        print ('     *** ERROR: there is no specified energy_calibrated in the energy_calibrated lookup table. please choose a calibrated energy_calibrated.')
        return    0                            

    Mirr_Ang = Mirr_Ang_list[idx[0][0]] 
    Mirr_YAvg = Mirr_YAvg_list[idx[0][0]]

    DMM_USY_OB = DMM_USY_OB_list[idx[0][0]] 
    DMM_USY_IB = DMM_USY_IB_list[idx[0][0]]
    DMM_DSY = DMM_DSY_list[idx[0][0]]

    USArm = USArm_list[idx[0][0]]                
    DSArm = DSArm_list[idx[0][0]]

    M2Y = M2Y_list[idx[0][0]]
    DMM_USX = DMM_USX_list[idx[0][0]]
    DMM_DSX = DMM_DSX_list[idx[0][0]]
    XIASlit = XIASlit_list[idx[0][0]]          

    print('   *** Energy is set at %s keV' % energy_calibrated)                
    print('      *** Moving Stages ...')                


    print('      *** Mirr_Ang %s rad' % Mirr_Ang)
    print('      *** Mirr_YAvg %s mm' % Mirr_YAvg)
    
    print('      *** DMM_USY_OB %s mm' % DMM_USY_OB) 
    print('      *** DMM_USY_IB %s mm' % DMM_USY_IB)
    print('      *** DMM_DSY %s mm' % DMM_DSY)

    print('      *** USArm %s deg' % USArm)              
    print('      *** DSArm %s deg' % DSArm)

    print('      *** M2Y %s mm' % M2Y)
    print('      *** DMM_USX %s mm' % DMM_USX)
    print('      *** DMM_DSX %s mm' % DMM_DSX)
    print('      *** XIASlit %s mm' % XIASlit)          

    print(' ')
    print('  *** setEnergy')
    # print('    *** closing shutter')
    # global_PVs['ShutterA_Close'].put(1, wait=True)
    # wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
    # change2Mono()                
    # print('    *** moving filter)
    # if energy < 20.0:
    #     global_PVs['Filters'].put(4, wait=True, timeout=1000.0)
    # else:                                
    #     global_PVs['Filters'].put(0, wait=True, timeout=1000.0)

    # print('    *** moving Mirror')
    # global_PVs['Mirr_Ang'].put(Mirr_Ang, wait=False, timeout=1000.0) 
    # global_PVs['Mirr_YAvg'].put(Mirr_YAvg, wait=False, timeout=1000.0) 
    # print('    *** moving DMM Y')
    # global_PVs['DMM_USY_OB'].put(DMM_USY_OB, wait=False, timeout=1000.0) 
    # global_PVs['DMM_USY_IB'].put(DMM_USY_IB, wait=False, timeout=1000.0) 
    # global_PVs['DMM_DSY'].put(DMM_DSY, wait=False, timeout=1000.0) 

    # print('    *** moving DMM US/DS Arms')
    # global_PVs['USArm'].put(USArm, wait=False, timeout=1000.0)
    # global_PVs['DSArm'].put(DSArm, wait=True, timeout=1000.0)
    # time.sleep(3)
    # print('    *** moving DMM M2Y')
    # global_PVs['M2Y'].put(M2Y, wait=True, timeout=1000.0)
    # print('    *** moving DMM X')
    # global_PVs['DMM_USX'].put(DMM_USX, wait=False, timeout=1000.0)
    # global_PVs['DMM_DSX'].put(DMM_DSX, wait=True, timeout=1000.0)
    # global_PVs['XIASlit'].put(XIASlit, wait=True, timeout=1000.0)             
    print('  *** setEnergy: Done!')
    return energy_calibrated
 
