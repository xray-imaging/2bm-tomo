import time
import epics
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *


global variableDict

variableDict = {'PreDarkImages': 20,
        'PreWhiteImages': 20,
        'Projections': 1500,
        'PostDarkImages': 0,
        'PostWhiteImages': 0,
        'SampleXIn': 0.0,
        'SampleXOut': 5,
        'SampleStartPos': 0.0,
        'SampleEndPos': 180.0,
        'StartSleep_min': 0,
        'ExposureTime': 0.1,
        'ExposureTime_flat': 0.1,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': '2bmbPG3:', # other supported detectors: 'PCOIOC2:', 'PCOIOC3:', '2bmbSP1:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05
        }

global_PVs = {}


def EdgeMultiPosScan(exposureTime=0.1, slewSpeed=1, angStart=0, angEnd = 180,
                numProjPerSweep=1500,
                samInPos=0, samOutDist=4,
                roiSizeX = 2560, roiSizeY = 1240,
                posStep = 0, posNum = 1, 
                delay = 0, flatPerScan = 1, darkPerScan = 1,
                accl = 1, shutterMode=0, scanMode=0, clShutter=1, white_ang=90):                      
    """ Multiple poistion scans along vertical direction with edge camera
                
      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
              it assumes rotation axis is at image center at posInit.
    """
              
##### AHutch tomo configurations -- start
    if shutterMode == 0:
        camShutterMode = "Rolling"
    elif shutterMode == 1:
        camShutterMode = "Global"
    else:
        print "Wrong camera shutter mode! Quit ..."
        return False   
    if scanMode == 0:
        camScanSpeed = 'Normal'
    elif scanMode == 1:
        camScanSpeed = 'Fast'
    elif scanMode == 2:
        camScanSpeed = 'Fastest'
    else:
        print "Wrong camera scan mode! Quit ..."  
        return False                
                                  
    camPrefix = "PCOIOC3"                
    shutter = "2bma:A_shutter"          

    samStage = "2bma:m49"
    posStage = "2bma:m20"        
    rotStage = "2bma:m82"
    PSO = "2bma:PSOFly2"
                
    if samStage == '2bma:m49':                
        initEdge(samInPos = samInPos,samStage=samStage,rotStage=rotStage)      
    elif samStage == '2bma:m20':
        samInPos = epics.caget(samStage+".VAL")
        initEdge(samInPos = samInPos,samStage=samStage,rotStage=rotStage)  
    else:
        print "Please edit the script to define samInPos. Quit"
        exit()

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                

    posInit = epics.caget(posStage+".VAL")
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                

    print("Freme Rate:", frate)
    numImage = numProjPerSweep
    if clShutter==1:        
        numImage += 20
    elif clShutter==0:
        if flatPerScan == 1:
            numImage += 10
        if darkPerScan == 1: 
            numImage += 10
    else:
        print 'Wrong clShutter value. Quit!'
        exit()
    
    # test camera -- start
    edgeTest(camScanSpeed, camShutterMode, roiSizeX, roiSizeY)
                
    # sample scan -- start
    print "start sample scan ... "
    for ii in range(posNum):    
    # set scan parameters -- start 
        setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)            
        timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                 

        edgeSet(numImage, exposureTime, frate, PSO = PSO)
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                    
        time.sleep(3)                                                            
        edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
        print "scan at position #",ii+1," is done!"

        samOutPos = samInPos + samOutDist
        
        if flatPerScan == 1:
        # set for white field -- start                   
            print "Acquiring flat images ..."   
            epics.caput(rotStage+'.VAL',white_ang)                
            edgeAcquireFlat(samInPos,samOutPos,samStage,rotStage,shutter, PSO = PSO)       
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)  
            epics.caput(rotStage+'.VAL',0)               
            print "flat for position #", ii+1, " is done!"                
        # set for white field -- end                                            
                                
        if darkPerScan == 1:
            # set for dark field -- start
            print "Acquiring dark images ..."                
            edgeAcquireDark(samInPos,samStage,rotStage,shutter, PSO = PSO) 
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)             
            print "dark is done!"  
        if  posNum!=1 and darkPerScan!=0 and flatPerScan!=0 and ii!=(posNum-1):       
            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
        # set for dark field -- end
                                        
        epics.caput(posStage + ".VAL",str(posInit+(ii+1)*posStep), wait=True, timeout=1000.0)
        if ii != (posNum-1):
            time.sleep(delay)
                                          
    print "sample scan is done!"          
                                


    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
                         
    # sample scan -- end

    if clShutter==1:        
        if flatPerScan == 0:    
            # set for white field -- start                   
            print "Acquiring flat images ..."    
            epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
            time.sleep(3)
            epics.caput(rotStage+'.VAL',white_ang)  
            print   samInPos,samOutPos               
            edgeAcquireFlat(samInPos,samOutPos,samStage,rotStage,shutter, PSO = PSO) 
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0) 
            epics.caput(rotStage+'.VAL',0)   
    #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)         
            print "flat is done!"                
            # set for white field -- end
    
        if darkPerScan == 0:    
            # set for dark field -- start
            print "Acquiring dark images ..."                
            edgeAcquireDark(samInPos,samStage,rotStage,shutter, PSO = PSO) 
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)           
            print "dark is done!" 
            
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)      
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)      

    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix+":cam1:pcoedge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                                                                               
    # set for new scans -- end
    print "Scan finished!" 
    epics.caput(posStage + ".VAL",str(posInit), wait=True, timeout=1000.0)
    
def main():
    #EdgeMultiPosScan() 
    exposureTime = 0.1
    roiSizeX = 2560
    roiSizeY = 1240
    PSO = "2bma:PSOFly2"
    rotStage = "2bma:m82"
    samStage = '2bma:m49'
    samInPos = 0
    shutter = "2bma:A_shutter"      
    slewSpeed=1
    camPrefix = "PCOIOC3"                

    angStart=0
    angEnd = 18
    numProjPerSweep=150
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep

    accl = 1
    acclTime = 1.0*slewSpeed/accl
     
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                
    numImage = numProjPerSweep + 20

    samOutDist = 3
    samOutPos = samInPos + samOutDist

    epics.caput(camPrefix + ":cam1:FrameType.ZRST", "/exchange/data")
    epics.caput(camPrefix + ":cam1:FrameType.ONST", "/exchange/data_dark")
    epics.caput(camPrefix + ":cam1:FrameType.TWST", "/exchange/data_white")
             
    initEdge(samInPos,samStage,rotStage)      
    edgeTest('Normal', "Rolling", roiSizeX, roiSizeY)
    setPSO(slewSpeed, scanDelta, acclTime, angStart, angEnd, PSO, rotStage)
    edgeSet(numImage, exposureTime, frate, PSO = PSO)
    edgeAcquisition(samInPos, samStage, numProjPerSweep, shutter, PSO=PSO,rotStage=rotStage)
    edgeAcquireFlat(samInPos, samOutPos, samStage, rotStage, shutter, PSO) 
    edgeAcquireDark(samInPos, samStage, rotStage, shutter, PSO) 
    
if __name__ == '__main__':
    main()
