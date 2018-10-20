import time
import epics

def setPSO(slewSpeed, scanDelta, acclTime,angStart=0, angEnd=180, PSO="2bmb:PSOFly1",rotStage="2bma:m82"):
    print(' ')
    print('  *** Set PSO')
    epics.caput(PSO+":startPos.VAL",str(angStart), wait=True, timeout=1000.0)                
    epics.caput(PSO+":endPos.VAL",str(angEnd), wait=True, timeout=1000.0)
    epics.caput(rotStage+".VELO",str(slewSpeed), wait=True, timeout=1000.0)
    epics.caput(PSO+":slewSpeed.VAL",str(slewSpeed), wait=True, timeout=1000.0)
    epics.caput(rotStage+".ACCL",str(acclTime), wait=True, timeout=1000.0)
    epics.caput(PSO+":scanDelta.VAL",str(scanDelta), wait=True, timeout=1000.0)    
    print('  *** Set PSO: Done!')


def initEdge(samInPos=0, samStage=None, rotStage=None):
    print(' ')
    print('  *** Init PCO')
    camPrefix = "PCOIOC3"                            
    shutter = "2bma:A_shutter"
    if samStage is None:
        samStage = "2bma:m49"  
    if rotStage is None:              
        rotStage = "2bma:m82"   
    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
    epics.caput(camPrefix+":HDF1:EnableCallbacks.VAL",1, wait=True, timeout=1000.0)   
    epics.caput(camPrefix+":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0) 
    epics.caput(camPrefix+":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_is_frame_rate_mode.VAL",0, wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":cam1:AcquireTime.VAL",0.2, wait=True, timeout=1000.0)
    epics.caput(camPrefix+":image1:EnableCallbacks.VAL","Enable", wait=True, timeout=1000.0)
    epics.caput(rotStage+".STOP",1, wait=True, timeout=1000.0)
    epics.caput(rotStage+".SET","Set", wait=True, timeout=1000.0) 
    epics.caput(rotStage+".VAL",epics.caget(rotStage+".VAL")%360.0, wait=True, timeout=1000.0) 
    epics.caput(rotStage+".SET","Use", wait=True, timeout=1000.0) 
    epics.caput(rotStage+".VELO","30", wait=True, timeout=1000.0)    
    epics.caput(rotStage+".ACCL","3", wait=True, timeout=1000.0)                
    epics.caput(rotStage+".VAL","0", wait=True, timeout=1000.0)
    if samInPos is not None:
        epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)  
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)               
    print('  *** Init PCO: Done!')


def edgeSet(numImage, exposureTime, frate,PSO = "2bmb:PSOFly1"):    
    print(' ')
    print('  *** Set PCO')
    camPrefix = "PCOIOC3"
    epics.caput(camPrefix+":cam1:pco_is_frame_rate_mode.VAL","DelayExp", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:AcquirePeriod.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_set_frame_rate.VAL",str(frate+1), wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_set_frame_rate.VAL",str(frate), wait=True, timeout=1000.0)                    
    epics.caput(camPrefix+":HDF1:AutoIncrement.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":HDF1:NumCapture.VAL",str(numImage), wait=True, timeout=1000.0)                
    epics.caput(camPrefix+":HDF1:NumCapture_RBV.VAL",str(numImage), wait=True, timeout=1000.0)  
    epics.caput(camPrefix+":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                

##    epics.caput(camPrefix+":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
##    epics.caput(camPrefix+":HDF1:FileName.VAL",filename, wait=True, timeout=1000.0)    

    epics.caput(camPrefix+":HDF1:FileTemplate.VAL","%s%s_%4.4d.hdf", wait=True, timeout=1000.0)                
    epics.caput(camPrefix+":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(camPrefix+":cam1:NumImages.VAL",str(numImage), wait=True, timeout=1000.0)                                
    epics.caput(camPrefix+":cam1:ImageMode.VAL","Multiple", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:AcquireTime.VAL",str(exposureTime), wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Soft/Ext", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)            
    print('  *** Set PCO: Done!')


def edgeTest(camScanSpeed,camShutterMode,roiSizeX=2560,roiSizeY=2160):
    camPrefix = "PCOIOC3"
    print(' ')
    print('  *** Testing PCO camera')
    epics.caput(camPrefix+":cam1:ArrayCallbacks.VAL","Enable", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:ImageMode.VAL","Multiple", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_global_shutter.VAL",camShutterMode, wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL",camScanSpeed, wait=True, timeout=1000.0)                
    epics.caput(camPrefix+":cam1:AcquireTime.VAL","0.001000", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)     
    print('  *** Testing PCO camera: Done!')

def edgeAcquisition(samInPos, samStage, numProjPerSweep, shutter, clShutter=1, PSO="2bma:PSOFly2", rotStage="2bma:m82"):
    print(' ')
    print('  *** Acquisition')
    print('      *** Projections')
    camPrefix = "PCOIOC3"    

##    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)                
    epics.caput(camPrefix+":cam1:FrameType.VAL",'0', wait=True, timeout=1000.0)     
    print("Type Projections: ", epics.caget(camPrefix+":cam1:FrameType.VAL"))
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)
    
    rotCurrPos = epics.caget(rotStage + ".VAL")
    epics.caput(rotStage + ".SET",str(1), wait=True, timeout=1000.0)       
    epics.caput(rotStage + ".VAL",str(1.0*rotCurrPos%360.0), wait=True, timeout=1000.0) 
    epics.caput(rotStage + ".SET",str(0), wait=True, timeout=1000.0)  
    
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)   
                 
    epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
    epics.caput(PSO+":fly.VAL","Fly", wait=True, timeout=1000.0) 

##    if epics.caget(PSO+":fly.VAL") == 0 & clShutter == 1:               
##        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)  
        
    rotCurrPos = epics.caget(rotStage + ".VAL")
    epics.caput(rotStage + ".SET",str(1), wait=True, timeout=1000.0)       
    epics.caput(rotStage + ".VAL",str(1.0*rotCurrPos%360.0), wait=True, timeout=1000.0) 
    epics.caput(rotStage + ".SET",str(0), wait=True, timeout=1000.0) 
             
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    time.sleep(1)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)   
    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:NumImagesCounter_RBV.VAL")):      
        time.sleep(1)                    
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)             
    print('      *** Projections: Done!')


def edgeAcquireFlat(samInPos,samOutPos,samStage,rotStage, shutter, PSO = "2bma:PSOFly2"):    
    print('      *** White Fields')
    camPrefix = "PCOIOC3"
    epics.caput(samStage+".VAL",str(samOutPos), wait=True, timeout=1000.0)                
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                

##    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)

    time.sleep(5)
    epics.caput(camPrefix+":cam1:FrameType.VAL",'2', wait=True, timeout=1000.0)     
    print("Type White: ", epics.caget(camPrefix+":cam1:FrameType.VAL"))
    epics.caput(camPrefix+":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)   
    
    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)   
    epics.caput(camPrefix+":cam1:TriggerMode","Internal", wait=True, timeout=1000.0)            
    time.sleep(5)            
    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)  
    
##    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)

    time.sleep(5)            
    epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)                    
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)             


def edgeAcquireDark(samInPos,samStage,rotStage, shutter, PSO = "2bma:PSOFly2"):    
    print("      *** Dark Fields")
    camPrefix = "PCOIOC3"    
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)

##    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)

    time.sleep(5)
            
    epics.caput(camPrefix+":cam1:FrameType.VAL",'1', wait=True, timeout=1000.0)             
    print("Type Dark: ", epics.caget(camPrefix+":cam1:FrameType.VAL"))
    
    epics.caput(camPrefix+":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)

    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)            

##    epics.caput(camPrefix+":cam1:TriggerMode","Internal", wait=True, timeout=1000.0)            

    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)
        
    epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    print('      *** Dark Fileds: Done!')
    print('  *** Acquisition: Done!')

def init_general_PVs(global_PVs, variableDict):

    # shutter pv's
    global_PVs['ShutterA_Open'] = PV('2bma:A_shutter:open.VAL')
    global_PVs['ShutterA_Close'] = PV('2bma:A_shutter:close.VAL')
    global_PVs['ShutterA_Move_Status'] = PV('PA:02BM:STA_A_FES_OPEN_PL')
    global_PVs['ShutterB_Open'] = PV('2bma:B_shutter:open.VAL')
    global_PVs['ShutterB_Close'] = PV('2bma:B_shutter:close.VAL')
    global_PVs['ShutterB_Move_Status'] = PV('PA:02BM:STA_B_SBS_OPEN_PL')

    if STATION == '2-BM-A':
            print('*** Running in station A:')
            # Set sample stack motor pv's:
            global_PVs['Motor_SampleX'] = PV('2bma:m49.VAL')
            global_PVs['Motor_SampleY'] = PV('2bma:m20.VAL')
            global_PVs['Motor_SampleRot'] = PV('2bma:m82.VAL')  
            global_PVs['Motor_SampleRot_Stop'] = PV('2bma:m82.STOP') # Aerotech ABR-250
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
            global_PVs['Fly_Calc_Projections'] = PV('2bma:PSOFly2:numTriggers')
            global_PVs['Theta_Array'] = PV('2bma:PSOFly2:motorPos.AVAL')

        
 
