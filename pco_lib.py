'''
    Tomo Scan Lib for Sector 2-BM
    
'''
from __future__ import print_function

import time
import sys
import numpy as np

from epics import PV

ShutterA_Open_Value = 1
ShutterA_Close_Value = 0
ShutterB_Open_Value = 1
ShutterB_Close_Value = 0

FrameTypeData = 0
FrameTypeDark = 1
FrameTypeWhite = 2

UseShutterA = True
UseShutterB = False

STATION = '2-BM-A' # or '2-BM-B'

TESTING_MODE = False

if TESTING_MODE == True:
    UseShutterA = False
    UseShutterB = False

if UseShutterA is False and UseShutterB is False:
    print('### WARNING: shutters are deactivted during the scans !!!!')

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


    if STATION == '2-BM-A':
            print('*** Running in station A:')
            # Set sample stack motor PVs:
            global_PVs['Motor_SampleX'] = PV('2bma:m49.VAL')
            global_PVs['Motor_SampleY'] = PV('2bma:m20.VAL')
            global_PVs['Motor_SampleRot'] = PV('2bma:m82.VAL') # Aerotech ABR-250
            global_PVs['Motor_SampleRot_Accl'] = PV('2bma:m82.ACCL') 
            global_PVs['Motor_SampleRot_Stop'] = PV('2bma:m82.STOP') 
            global_PVs['Motor_SampleRot_Set'] = PV('2bma:m82.SET') 
            global_PVs['Motor_SampleRot_Velo'] = PV('2bma:m82.VELO') 
            global_PVs['Motor_Sample_Top_X'] = PV('2bma:m50.VAL')
            global_PVs['Motor_Sample_Top_Z'] = PV('2bma:m51.VAL') 
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
    global_PVs['Cam1_SizeX'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeX')
    global_PVs['Cam1_SizeY'] = PV(variableDict['IOC_Prefix'] + 'cam1:SizeY')
    global_PVs['Cam1_NumImages'] = PV(variableDict['IOC_Prefix'] + 'cam1:NumImages')     
    global_PVs['Cam1_ArrayCallbacks'] = PV(variableDict['IOC_Prefix'] + 'cam1:ArrayCallbacks')
    global_PVs['Cam1_TriggerMode'] = PV(variableDict['IOC_Prefix'] + 'cam1:TriggerMode')           

    global_PVs['Cam1_FrameType'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType')    
    global_PVs['Cam1_FrameTypeZRST'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType.ZRST')
    global_PVs['Cam1_FrameTypeONST'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType.ONST')
    global_PVs['Cam1_FrameTypeTWST'] = PV(variableDict['IOC_Prefix'] + 'cam1:FrameType.TWST')

    global_PVs['HDF1_AutoSave'] = PV(variableDict['IOC_Prefix'] + 'HDF1:AutoSave')
    global_PVs['HDF1_AutoIncrement'] = PV(variableDict['IOC_Prefix'] + 'HDF1:AutoIncrement')
    global_PVs['HDF1_EnableCallbacks'] = PV(variableDict['IOC_Prefix'] + 'HDF1:EnableCallbacks')  
    global_PVs['HDF1_Capture'] = PV(variableDict['IOC_Prefix'] + 'HDF1:Capture')
    global_PVs['HDF1_NumCapture'] = PV(variableDict['IOC_Prefix'] + 'HDF1:NumCapture')       
    global_PVs['HDF1_NumCapture_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:NumCapture_RBV') 
    global_PVs['HDF1_NumCaptured_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:NumCaptured_RBV')
    global_PVs['HDF1_FileName'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileName')   
    global_PVs['HDF1_FilePath'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FilePath')
    global_PVs['HDF1_FileTemplate'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileTemplate')       
    global_PVs['HDF1_FileWriteMode'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FileWriteMode')
    global_PVs['HDF1_FullFileName_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FullFileName_RBV')
    global_PVs['Image1_EnableCallbacks'] = PV(variableDict['IOC_Prefix'] + 'image1:EnableCallbacks')



def setPSO(global_PVs, variableDict):
    print(' ')
    print('  *** Set PSO')

    acclTime = 1.0 * variableDict['SlewSpeed']/variableDict['AcclRot']
    scanDelta = 1.0*(variableDict['SampleEndPos'] - variableDict['SampleStartPos'])/variableDict['Projections']

    global_PVs['Fly_StartPos'].put(str(variableDict['SampleStartPos']), wait=True, timeout=1000.0)                
    global_PVs['Fly_EndPos'].put(str(variableDict['SampleEndPos']), wait=True, timeout=1000.0)
    global_PVs['Motor_SampleRot_Velo'].put(str(variableDict['SlewSpeed']), wait=True, timeout=1000.0)
    global_PVs['Fly_SlewSpeed'].put(str(variableDict['SlewSpeed']), wait=True, timeout=1000.0)
    global_PVs['Motor_SampleRot_Accl'].put(str(acclTime), wait=True, timeout=1000.0)
    global_PVs['Fly_ScanDelta'].put(str(scanDelta), wait=True, timeout=1000.0)    
    print('  *** Set PSO: Done!')


def edgeInit(global_PVs, variableDict):
    print(' ')
    print('  *** Init PCO')                        
    global_PVs['HDF1_EnableCallbacks'].put(1, wait=True, timeout=1000.0)   
    global_PVs['HDF1_Capture'].put('Done', wait=True, timeout=1000.0) 
    global_PVs['HDF1_NumCaptured_RBV'].put('0', wait=True, timeout=1000.0)    
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)    
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)
    global_PVs['Cam1_ImageMode'].put('Continuous', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOEdgeFastscan'].put('Normal', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOIsFrameRateMode'].put(0, wait=True, timeout=1000.0)    
    global_PVs['Cam1_AcquireTime'].put(0.2, wait=True, timeout=1000.0)
    global_PVs['Image1_EnableCallbacks'].put('Enable', wait=True, timeout=1000.0)
    global_PVs['Motor_SampleRot_Stop'].put(1, wait=True, timeout=1000.0)
    global_PVs['Motor_SampleRot_Set'].put('Set', wait=True, timeout=1000.0) 
    global_PVs['Motor_SampleRot'].put(global_PVs['Motor_SampleRot'].get()%360.0, wait=True, timeout=1000.0)

    global_PVs['Motor_SampleRot_Set'].put('Use', wait=True, timeout=1000.0) 
    global_PVs['Motor_SampleRot_Velo'].put('30', wait=True, timeout=1000.0)    
    global_PVs['Motor_SampleRot_Accl'].put('3', wait=True, timeout=1000.0)                
    global_PVs['Motor_SampleRot'].put('0', wait=True, timeout=1000.0)
    if variableDict['SampleXIn'] is not None:
        global_PVs['Motor_SampleRot'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0)  
    print('  *** Init PCO: Done!')


def edgeSet(global_PVs, variableDict, fname):    
    print(' ')
    print('  *** Set PCO')

    set_frame_type(global_PVs, variableDict)

    numImage = variableDict['PreDarkImages'] + \
        variableDict['PreWhiteImages'] + variableDict['Projections'] + \
        variableDict['PostDarkImages'] + variableDict['PostWhiteImages']   

    frate =  int(1.0*variableDict['Projections']/(1.0*(variableDict['SampleEndPos'] - \
             variableDict['SampleStartPos'])/variableDict['SlewSpeed']) + 5)
             
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

    global_PVs['HDF1_FileTemplate'].put('%s%s_%4.4d.hdf', wait=True, timeout=1000.0)                
    global_PVs['HDF1_AutoSave'].put('Yes', wait=True, timeout=1000.0)
    global_PVs['HDF1_FileWriteMode'].put('Stream', wait=True, timeout=1000.0)
    global_PVs['HDF1_Capture'].put('Capture', wait=False, timeout=1000.0)
    global_PVs['Cam1_NumImages'].put(str(numImage), wait=True, timeout=1000.0)                                
    global_PVs['Cam1_ImageMode'].put('Multiple', wait=True, timeout=1000.0)
    global_PVs['Cam1_AcquireTime'].put(str(variableDict['ExposureTime']), wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Soft/Ext', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOReady2Acquire'].put('0', wait=True, timeout=1000.0)
    global_PVs['Cam1_Acquire'].put('Acquire', wait=False, timeout=1000.0)            
    print('  *** Set PCO: Done!')


def edgeTest(global_PVs, variableDict):
    print(' ')
    print('  *** Testing PCO camera')
    global_PVs['Cam1_ArrayCallbacks'].put('Enable', wait=True, timeout=1000.0)
    global_PVs['Cam1_NumImages'].put('10', wait=True, timeout=1000.0)
    global_PVs['Cam1_ImageMode'].put('Multiple', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOGlobalShutter'].put('Rolling', wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOEdgeFastscan'].put('Normal', wait=True, timeout=1000.0)                
    global_PVs['Cam1_AcquireTime'].put("0.001000", wait=True, timeout=1000.0)
    global_PVs['Cam1_SizeX'].put(str(2560), wait=True, timeout=1000.0)
    global_PVs['Cam1_SizeY'].put(str(1240), wait=True, timeout=1000.0)
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)    
    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)     
    print('  *** Testing PCO camera: Done!')

def edgeAcquisition(global_PVs, variableDict):
    print(' ')
    print('  *** Acquisition')
    print('      *** Projections')

    global_PVs['Cam1_FrameType'].put(FrameTypeData, wait=True, timeout=1000.0) 
    time.sleep(1)    
    global_PVs['Motor_SampleRot'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0)
    
    rotCurrPos = global_PVs['Motor_SampleRot'].get()

    global_PVs['Motor_SampleRot_Set'].put(str(1), wait=True, timeout=1000.0)       
    global_PVs['Motor_SampleRot'].put(str(1.0*rotCurrPos%360.0), wait=True, timeout=1000.0) 
    global_PVs['Motor_SampleRot_Set'].put(str(0), wait=True, timeout=1000.0)  
    global_PVs['Motor_SampleRot_Velo'].put("50.00000", wait=True, timeout=1000.0)
    global_PVs['Motor_SampleRot'].put("0.00000", wait=False, timeout=1000.0)   
                 
    global_PVs['Fly_Taxi'].put('Taxi', wait=True, timeout=1000.0)
    global_PVs['Fly_Run'].put('Fly', wait=True, timeout=1000.0) 
        
    rotCurrPos = global_PVs['Motor_SampleRot'].get()
    global_PVs['Motor_SampleRot_Set'].put(str(1), wait=True, timeout=1000.0)       
    global_PVs['Motor_SampleRot'].put(str(1.0*rotCurrPos%360.0), wait=True, timeout=1000.0) 
    global_PVs['Motor_SampleRot_Set'].put(str(0), wait=True, timeout=1000.0) 
             
    global_PVs['Motor_SampleRot_Velo'].put("50.00000", wait=True, timeout=1000.0)
    time.sleep(1)
    global_PVs['Motor_SampleRot'].put("0.00000", wait=False, timeout=1000.0)   
    while (global_PVs['HDF1_NumCaptured_RBV'].get() != global_PVs['Cam1_NumImagesCounter_RBV'].get()):      
        time.sleep(1)                    
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)             
    print('      *** Projections: Done!')


def edgeAcquireFlat(global_PVs, variableDict):    
    print('      *** White Fields')
    global_PVs['Motor_SampleX'].put(str(variableDict['SampleXOut']), wait=True, timeout=1000.0)                
    global_PVs['Fly_ScanControl'].put('Standard', wait=True, timeout=1000.0)                

    global_PVs['Cam1_FrameType'].put(FrameTypeWhite, wait=True, timeout=1000.0)     
    time.sleep(1)    
    global_PVs['Cam1_NumImages'].put(str(variableDict['PostWhiteImages']), wait=True, timeout=1000.0)   
    
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)   
    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)  
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)
    global_PVs['Motor_SampleX'].put(str(variableDict['SampleXIn']), wait=True, timeout=1000.0)                    
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)             
    print('      *** White Fileds: Done!')


def edgeAcquireDark(global_PVs, variableDict):    
    print("      *** Dark Fields") 
    global_PVs['Fly_ScanControl'].put('Standard', wait=True, timeout=1000.0)
    global_PVs['Cam1_FrameType'].put(FrameTypeDark, wait=True, timeout=1000.0)             
    time.sleep(1)    

    global_PVs['Cam1_NumImages'].put(str(variableDict['PostDarkImages']), wait=True, timeout=1000.0)   
    global_PVs['Cam1_PCOTriggerMode'].put('Auto', wait=True, timeout=1000.0)            

    global_PVs['Cam1_Acquire'].put('Acquire', wait=True, timeout=1000.0)       
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)    
    global_PVs['Cam1_Acquire'].put('Done', wait=True, timeout=1000.0)
    print('      *** Dark Fileds: Done!')
    print('  *** Acquisition: Done!')        
 

def set_frame_type(global_PVs, variableDict):
    global_PVs['Cam1_FrameTypeZRST'].put('/exchange/data')
    global_PVs['Cam1_FrameTypeONST'].put('/exchange/data_dark')
    global_PVs['Cam1_FrameTypeTWST'].put('/exchange/data_white')

    
def open_shutters(global_PVs, variableDict):
    print(' ')
    print('  *** open_shutters')
    if UseShutterA is True:
        global_PVs['ShutterA_Open'].put(1, wait=True)
        wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Open_Value)
        time.sleep(3)
    if UseShutterB is True:
        global_PVs['ShutterB_Open'].put(1, wait=True)
        wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Open_Value)
    print('  *** open_shutters: Done!')


def close_shutters(global_PVs, variableDict):
    print(' ')
    print('  *** close_shutters')
    if UseShutterA is True:
        global_PVs['ShutterA_Close'].put(1, wait=True)
        wait_pv(global_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
    if UseShutterB is True:
        global_PVs['ShutterB_Close'].put(1, wait=True)
        wait_pv(global_PVs['ShutterB_Move_Status'], ShutterB_Close_Value)
    print('  *** close_shutters: Done!')
    

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

# def change2White():
#     shutter = "2bma:A_shutter"    
#     BL = '2bma'
#     epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
# #    epics.caput(BL+":m33.VAL",107.8, wait=False, timeout=1000.0)                
#     epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)                
#     epics.caput(BL+":M1angl.VAL",0, wait=True, timeout=1000.0)
#     time.sleep(1)                
#     epics.caput(BL+":M1avg.VAL",-4, wait=True, timeout=1000.0)
#     time.sleep(1)                
#     epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
#     epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
#     time.sleep(3)                
#     epics.caput(BL+":m26.VAL",-16, wait=False, timeout=1000.0)    
#     epics.caput(BL+":m27.VAL",-16, wait=False, timeout=1000.0)    
#     epics.caput(BL+":m29.VAL",-16, wait=True, timeout=1000.0)                
#     time.sleep(3)                
#     epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)
#     epics.caput(BL+":m7.VAL",-1.65, wait=True, timeout=1000.0)                
                

# def change2Mono():
#     shutter = "2bma:A_shutter"    
#     BL = '2bma'
#     epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
# #    epics.caput(BL+":m33.VAL",121, wait=False, timeout=1000.0)                    
#     epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
#     epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
#     time.sleep(1)                    
#     epics.caput(BL+":M1angl.VAL",2.657, wait=True, timeout=1000.0)
#     time.sleep(1)                                            
#     epics.caput(BL+":m26.VAL",-0.1, wait=False, timeout=1000.0)    
#     epics.caput(BL+":m27.VAL",-0.1, wait=False, timeout=1000.0)    
#     epics.caput(BL+":m29.VAL",-0.1, wait=True, timeout=1000.0)                
#     time.sleep(3)
#     epics.caput(BL+":m25.VAL",81.5, wait=False, timeout=1000.0)    
#     epics.caput(BL+":m28.VAL",81.5, wait=True, timeout=1000.0)
#     time.sleep(3)                
#     epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)    
#     epics.caput(BL+":m7.VAL",30.35, wait=True, timeout=1000.0)                
                
                
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


#         epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
#         epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
#         time.sleep(1)                    
#         epics.caput(BL+":M1angl.VAL",2.657, wait=True, timeout=1000.0)
#         time.sleep(1)
#         epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
#         epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
#         time.sleep(3)                                            
#         epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
#         time.sleep(3)                
#         epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)    
#         epics.caput(BL+":m7.VAL",18.75, wait=True, timeout=1000.0)


#     if ang == 2.657:
#         shutter = "2bma:A_shutter"    
#         BL = '2bma'
#         epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
#     #    epics.caput(BL+":m33.VAL",-70.1, wait=False, timeout=1000.0)     
#     #    epics.caput(BL+":m21.VAL",1306.0, wait=False, timeout=1000.0)                
#         epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
#         epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
#         time.sleep(1)                    
#         epics.caput(BL+":M1angl.VAL",2.657, wait=True, timeout=1000.0)
#         time.sleep(1)
#         epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
#         epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
#         time.sleep(3)                                            
#         epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
#         time.sleep(3)                
#         epics.caput(BL+":Slit1Hcenter.VAL",7.2, wait=True, timeout=1000.0)    
#         epics.caput(BL+":m7.VAL",18.75, wait=True, timeout=1000.0)
#     elif ang == 2.1:
#         shutter = "2bma:A_shutter"    
#         BL = '2bma'
#         epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
#     #    epics.caput(BL+":m33.VAL",-75.6, wait=False, timeout=1000.0) 
#     #    epics.caput(BL+":m21.VAL",1306.0, wait=False, timeout=1000.0)                    
#         epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
#         epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
#         time.sleep(1)                    
#         epics.caput(BL+":M1angl.VAL",2.1, wait=True, timeout=1000.0)
#         time.sleep(1)
#         epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
#         epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
#         time.sleep(3)                                            
#         epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
#         time.sleep(3)                
#         epics.caput(BL+":Slit1Hcenter.VAL",7.5, wait=True, timeout=1000.0)    
#         epics.caput(BL+":m7.VAL",14.75, wait=True, timeout=1000.0)         
#     elif ang == 2.0:
#         shutter = "2bma:A_shutter"    
#         BL = '2bma'
#         epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
#     #    epics.caput(BL+":m33.VAL",-75.6, wait=False, timeout=1000.0) 
#     #    epics.caput(BL+":m21.VAL",1306.0, wait=False, timeout=1000.0)                    
#         epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
#         epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
#         time.sleep(1)                    
#         epics.caput(BL+":M1angl.VAL",2.0, wait=True, timeout=1000.0)
#         time.sleep(1)
#         epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
#         epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
#         time.sleep(3)                                            
#         epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
#         time.sleep(3)                
#         epics.caput(BL+":Slit1Hcenter.VAL",7.5, wait=True, timeout=1000.0)    
#         epics.caput(BL+":m7.VAL",13.75, wait=True, timeout=1000.0) 
#     elif ang == 1.8:
#         shutter = "2bma:A_shutter"    
#         BL = '2bma'
#         epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
#     #    epics.caput(BL+":m33.VAL",-77.1, wait=False, timeout=1000.0)    
#     #    epics.caput(BL+":m21.VAL",1306.0, wait=False, timeout=1000.0)                 
#         epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
#         epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
#         time.sleep(1)                    
#         epics.caput(BL+":M1angl.VAL",1.8, wait=True, timeout=1000.0)
#         time.sleep(1)
#         epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
#         epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
#         time.sleep(3)                                            
#         epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
#         time.sleep(3)                
#         epics.caput(BL+":Slit1Hcenter.VAL",4.85, wait=True, timeout=1000.0)    
#         epics.caput(BL+":m7.VAL",11.75, wait=True, timeout=1000.0)   
#     elif ang == 1.5:
#         shutter = "2bma:A_shutter"    
#         BL = '2bma'
#         epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
#     #    epics.caput(BL+":m33.VAL",-79.8, wait=False, timeout=1000.0)    
#     #    epics.caput(BL+":m21.VAL",1306.0, wait=False, timeout=1000.0)                 
#         epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
#         epics.caput(BL+":M1avg.VAL",-0.1, wait=True, timeout=1000.0)
#         time.sleep(1)                    
#         epics.caput(BL+":M1angl.VAL",1.5, wait=True, timeout=1000.0)
#         time.sleep(1)
#         epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
#         epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
#         time.sleep(3)                                            
#         epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
#         epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
#         time.sleep(3)                
#         epics.caput(BL+":Slit1Hcenter.VAL",4.85, wait=True, timeout=1000.0)    
#         epics.caput(BL+":m7.VAL",8.75, wait=True, timeout=1000.0)               


def setEnergy(energy = 24.9):

    shutter = "2bma:A_shutter"    
    BL = '2bma'

    # epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    # change2Mono()                
    # if energy < 20.0:
    #     epics.caput(BL+":fltr1:select.VAL",4, wait=True, timeout=1000.0)
    # else:                                
    #     epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)

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

    # epics.caput(BL+":M1angl.VAL",Mirr_Ang, wait=False, timeout=1000.0) 
    # epics.caput(BL+":M1avg.VAL",Mirr_YAvg, wait=False, timeout=1000.0) 
    
    # epics.caput(BL+":m26.VAL",DMM_USY_OB, wait=False, timeout=1000.0) 
    # epics.caput(BL+":m27.VAL",DMM_USY_IB, wait=False, timeout=1000.0) 
    # epics.caput(BL+":m29.VAL",DMM_DSY, wait=False, timeout=1000.0) 
    # epics.caput(BL+":m30.VAL",USArm, wait=False, timeout=1000.0)    
    # epics.caput(BL+":m31.VAL",DSArm, wait=True, timeout=1000.0)
    # time.sleep(3)                                            
    # epics.caput(BL+":m32.VAL",M2Y, wait=True, timeout=1000.0)
    # epics.caput(BL+":m25.VAL",DMM_USX, wait=False, timeout=1000.0)
    # epics.caput(BL+":m28.VAL",DMM_DSX, wait=True, timeout=1000.0)
    # epics.caput(BL+":m7.VAL",XIASlit, wait=True, timeout=1000.0)                
    return energy_calibrated

