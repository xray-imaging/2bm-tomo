'''
    Epics PV definition for Sector 2-BM  
    
'''
import time

from epics import PV
from tomo2bm import log

TESTING = True

ShutterAisFast = True           # True: use m7 as shutter; False: use Front End Shutter

ShutterA_Open_Value = 1
ShutterA_Close_Value = 0
ShutterB_Open_Value = 1
ShutterB_Close_Value = 0

Recursive_Filter_Type = 'RecursiveAve'

EPSILON = 0.1


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
        global_PVs['HDF1_FilePath'] = PV(params.camera_ioc_prefix + 'HDF1:FilePath')
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

    user_info_update(global_PVs, params)

    return global_PVs


def user_info_update(global_PVs, params):

    params.proposal_title = global_PVs['Proposal_Title'].get(as_string=True)
    params.user_email = global_PVs['User_Email'].get(as_string=True)
    params.user_badge = global_PVs['User_Badge'].get(as_string=True)
    params.user_last_name = global_PVs['User_Last_Name'].get(as_string=True)
    params.proposal_number = global_PVs['Proposal_Number'].get(as_string=True)
    params.user_institution = global_PVs['User_Institution'].get(as_string=True)
    params.experiment_year_month = global_PVs['Experiment_Year_Month'].get(as_string=True)
    params.user_info_update = global_PVs['User_Info_Update'].get(as_string=True)



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
