'''
    DMM Lib for Sector 2-BM  to change energy
    
'''
from __future__ import print_function

from epics import PV
import numpy as np

import log_lib

TESTING = True


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



def yes_or_no(question):
    answer = str(raw_input(question + " (Y/N): ")).lower().strip()
    while not(answer == "y" or answer == "yes" or answer == "n" or answer == "no"):
        log_lib.warning("Input yes or no")
        answer = str(raw_input(question + "(Y/N): ")).lower().strip()
    if answer[0] == "y":
        return True
    else:
        return False

def close_shutters(energy_change_PVs):
    log_lib.info(' ')
    log_lib.info('  *** close_shutters')
    if TESTING:
        log_lib.warning('  *** testing mode - shutters are deactivated during the scans !!!!')
    else:
        energy_change_PVs['ShutterA_Close'].put(1, wait=True)
        wait_pv(energy_change_PVs['ShutterA_Move_Status'], ShutterA_Close_Value)
        log_lib.info('  *** close_shutter A: Done!')

def move_filter(filter, energy_change_PVs):
    log_lib.info(' ')
    log_lib.info('  *** moving filters')

    if TESTING:
        log_lib.warning('  *** testing mode. Set filter:  %s ' % filter)
    else:
        log_lib.info('  *** Set filter:  %s ' % filter)
        energy_change_PVs['Filter_Select'].put(filter, wait=True)

def move_mirror(Mirr_YAvg, Mirr_Ang, energy_change_PVs):
    log_lib.info(' ')
    log_lib.info('  *** moving mirror')

    if TESTING:
        log_lib.warning('  *** testing mode. Mirr_YAvg %s mm' % Mirr_YAvg)
        log_lib.warning('  *** testing mode. Mirr_Ang %s rad' % Mirr_Ang)
    else:
        log_lib.info('Mirr_YAvg %s mm' % Mirr_YAvg)
        energy_change_PVs['Mirr_YAvg'].put(Mirr_YAvg, wait=True)
        time.sleep(1) 
        log_lib.info('Mirr_Ang %s rad' % Mirr_Ang)
        energy_change_PVs['Mirr_Ang'].put(Mirr_Ang, wait=True)
        time.sleep(1) 

def move_DMM_X(DMM_USX, DMM_DSX, energy_change_PVs):
    log_lib.info(' ')
    log_lib.info('  *** moving DMM_X')

    if TESTING:
        log_lib.warning('  *** testing mode. DMM_USX %s mm' % DMM_USX)
        log_lib.warning('  *** testing mode. DMM_DSX %s mm' % DMM_DSX)
    else:
        log_lib.info('     *** DMM_USX %s mm' % DMM_USX)
        energy_change_PVs['DMM_USX'].put(DMM_USX, wait=False)
        log_lib.info('     *** DMM_DSX %s mm' % DMM_DSX)
        energy_change_PVs['DMM_DSX'].put(DMM_DSX, wait=True)
        time.sleep(3)                

def move_DMM_Y(DMM_USY_OB, DMM_USY_IB, DMM_DSY, energy_change_PVs):

    log_lib.info(' ')
    log_lib.info('  *** moving DMM_Y')

    if TESTING:
        log_lib.warning('  *** testing mode. DMM_USY_OB %s mm' % DMM_USY_OB) 
        log_lib.warning('  *** testing mode. DMM_USY_IB %s mm' % DMM_USY_IB)    
        log_lib.warning('  *** testing mode. DMM_DSY %s mm' % DMM_DSY)        
    else:
        log_lib.info('     *** DMM_USY_OB %s mm' % DMM_USY_OB) 
        energy_change_PVs['DMM_USY_OB'].put(DMM_USY_OB, wait=False)
        log_lib.info('     *** DMM_USY_IB %s mm' % DMM_USY_IB)    
        energy_change_PVs['DMM_USY_IB'].put(DMM_USY_IB, wait=False)
        log_lib.info('     *** DMM_DSY %s mm' % DMM_DSY)        
        energy_change_PVs['DMM_DSY'].put(DMM_DSY, wait=True)
        time.sleep(3) 
 
def move_xia_slits_Y(XIASlitY, energy_change_PVs):
    log_lib.info(' ')
    log_lib.info('  *** moving XIA Slits Y')

    if TESTING:
        log_lib.warning('  *** testing mode. Moving XIA Slits Y %s mm' % XIASlitY) 
    else:
        log_lib.info('  *** Moving XIA Slits Y %s mm' % XIASlitY) 
        energy_change_PVs['XIASlitY'].put(XIASlitY, wait=True)

def move_slits_center(Slit1Hcenter, energy_change_PVs):
    log_lib.info(' ')
    log_lib.info('  *** moving XIA Slit center')

    if TESTING:
        log_lib.warning('  *** testing mode. Moving XIA Slit center %s mm' % Slit1Hcenter) 
    else:
        log_lib.info('  *** Moving XIA Slit center %s mm' % Slit1Hcenter) 
        energy_change_PVs['Slit1Hcenter'].put(Slit1Hcenter, wait=True)


def move_DMM_M2Y(M2Y, energy_change_PVs):    
    log_lib.info(' ')
    log_lib.info('  *** moving DMM_M2Y')

    if TESTING:
        log_lib.warning('  *** testing mode. Moving DMM_M2Y %s mm' % M2Y) 
    else:
        log_lib.info('  *** Moving DMM_M2Y %s mm' % M2Y) 
        energy_change_PVs['M2Y'].put(M2Y, wait=True, timeout=1000.0)

def move_DMM_arms(USArm, DSArm, energy_change_PVs):
    log_lib.info(' ')
    log_lib.info('  *** moving DMM_arms')

    if TESTING:
        log_lib.warning('  *** testing mode. Moving DMM USArm %s mm' % USArm) 
        log_lib.warning('  *** testing mode. Moving DMM DSArm %s mm' % DSArm) 
    else:    
        log_lib.info('  *** Moving DMM USArm %s mm' % USArm) 
        energy_change_PVs['USArm'].put(USArm, wait=False, timeout=1000.0)
        log_lib.info('  *** Moving DMM DSArm %s mm' % DSArm) 
        energy_change_PVs['DSArm'].put(DSArm, wait=True, timeout=1000.0)
        time.sleep(3)


def init_energy_change_PVs():

    energy_change_PVs = {}

    # shutter pv's
    energy_change_PVs['ShutterA_Open'] = PV('2bma:A_shutter:open.VAL')
    energy_change_PVs['ShutterA_Close'] = PV('2bma:A_shutter:close.VAL')
    energy_change_PVs['ShutterA_Move_Status'] = PV('PA:02BM:STA_A_FES_OPEN_PL')
    energy_change_PVs['ShutterB_Open'] = PV('2bma:B_shutter:open.VAL')
    energy_change_PVs['ShutterB_Close'] = PV('2bma:B_shutter:close.VAL')
    energy_change_PVs['ShutterB_Move_Status'] = PV('PA:02BM:STA_B_SBS_OPEN_PL')


    energy_change_PVs['Filter_Select'] = PV('2bma:fltr1:select.VAL')
    energy_change_PVs['Mirr_Ang'] = PV('2bma:M1angl.VAL')
    energy_change_PVs['Mirr_YAvg'] = PV('2bma:M1avg.VAL')
    
    energy_change_PVs['DMM_USX'] = PV('2bma:m25.VAL')
    energy_change_PVs['DMM_DSX'] = PV('2bma:m28.VAL')
    energy_change_PVs['DMM_USY_OB'] = PV('2bma:m26.VAL')
    energy_change_PVs['DMM_USY_IB'] = PV('2bma:m27.VAL')
    energy_change_PVs['DMM_DSY'] = PV('2bma:m29.VAL')

    energy_change_PVs['USArm'] = PV('2bma:m30.VAL')
    energy_change_PVs['DSArm'] = PV('2bma:m31.VAL')
    energy_change_PVs['M2Y'] = PV('2bma:m32.VAL')
                                 
    energy_change_PVs['XIASlitY'] = PV('2bma:m7.VAL')
    energy_change_PVs['Slit1Hcenter'] = PV('2bma:Slit1Hcenter.VAL')
 
    return energy_change_PVs


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def change2white(energy_change_PVs):

    log_lib.info(' ')
    log_lib.info('  *** change to white  *** ')
    
    close_shutters(energy_change_PVs)
    move_filter(0, energy_change_PVs)
    move_mirror(-4, 0, energy_change_PVs)
    move_DMM_X(50, 50, energy_change_PVs)
    move_DMM_Y(-16, -16, -16, energy_change_PVs)    
    move_xia_slits_Y(-1.65, energy_change_PVs)

    log_lib.info(' ')
    log_lib.info('  *** change to white: Done!  *** ')
                    

def change2mono(energy_change_PVs):

    log_lib.info(' ')
    log_lib.info('  *** change to mono  *** ')

    close_shutters(energy_change_PVs)

    move_filter(0, energy_change_PVs)
    move_mirror(0, 2.657, energy_change_PVs)
    move_DMM_Y(-0.1, -0.1, -0.1, energy_change_PVs)    
    move_DMM_X(81.5, 81.5, energy_change_PVs)
    move_xia_slits_Y(30.35, energy_change_PVs)

    log_lib.info(' ')
    log_lib.info('  *** change to mono: Done!  *** ')
               

def change2pink(energy_change_PVs, angle=2.657):

    log_lib.info(' ')
    log_lib.info('  *** change to pink  *** ')

    Mirr_Ang_list = np.array([1.500,1.800,2.000,2.100,2.657])

    angle_calibrated = find_nearest(Mirr_Ang_list, angle)

    if angle is not angle_calibrated:
        log_lib.info('  *** Mirror angle entered is %s mrad, the closest tested angle is %s mrad' % (angle, angle_calibrated))
        log_lib.info('  *** Options are %s mrad' % (Mirr_Ang_list))
    else:
        log_lib.info('   *** Mirror angle is set at %s mrad' % angle_calibrated)   

    log_lib.info('   *** Move mirror to %s mrad ?' % angle_calibrated)   
    if yes_or_no('Yes or No'):

        Mirr_YAvg_list = np.array([-0.1,0.0,0.0,0.0,0.0])

        DMM_USY_OB_list = np.array([-10,-10,-10,-10,-10])
        DMM_USY_IB_list = np.array([-10,-10,-10,-10,-10])
        DMM_DSY_list = np.array([-10,-10,-10,-10,-10])

        DMM_USX_list = np.array([50,50,50,50,50])
        DMM_DSX_list = np.array([50,50,50,50,50])

        XIASlitY_list = np.array([8.75,11.75,13.75,14.75,18.75])    

        Slit1Hcenter_list = np.array([4.85,4.85,7.5,7.5,7.2])

        Filter_list = np.array([0,0,0,0,0])

        idx = np.where(Mirr_Ang_list==angle_calibrated)                
        if idx[0].size == 0:
            log_lib.error('  *** ERROR: there is no specified calibrated calibrate in the calibrated angle lookup table. please choose a calibrated angle.')
            return    0                            

        Mirr_Ang = Mirr_Ang_list[idx[0][0]] 
        Mirr_YAvg = Mirr_YAvg_list[idx[0][0]]

        DMM_USY_OB = DMM_USY_OB_list[idx[0][0]] 
        DMM_USY_IB = DMM_USY_IB_list[idx[0][0]]
        DMM_DSY = DMM_DSY_list[idx[0][0]]

        DMM_USX = DMM_USX_list[idx[0][0]]
        DMM_DSX = DMM_DSX_list[idx[0][0]]

        XIASlitY = XIASlitY_list[idx[0][0]]          
        Slit1Hcenter = Slit1Hcenter_list[idx[0][0]] 

        Filter = Filter_list[idx[0][0]]

        log_lib.info('  *** Angle is set at %s mrad' % angle_calibrated)                

        close_shutters(energy_change_PVs)

        move_filter(Filter, energy_change_PVs)
        move_mirror(Mirr_YAvg, Mirr_Ang, energy_change_PVs)
        move_DMM_X(DMM_USX, DMM_DSX, energy_change_PVs)
        move_DMM_Y(DMM_USY_OB, DMM_USY_IB, DMM_DSY, energy_change_PVs)    
        
        move_slits_center(Slit1Hcenter, energy_change_PVs)
        move_xia_slits_Y(XIASlitY, energy_change_PVs)
            
        log_lib.info(' ')
        log_lib.info('  *** change to pink: Done!  *** ')
        return angle_calibrated

    else:
        log_lib.info(' ')
        log_lib.warning('   *** Mirror angle not changed')


def change_energy(energy_change_PVs, energy = 24.9):

    log_lib.info(' ')
    log_lib.info(' *** Change Energy  *** ')

    caliEng_list = np.array([55.00, 50.00, 45.00, 40.00, 35.00, 31.00, 27.40, 24.90, 22.70, 21.10, 20.20, 18.90, 17.60, 16.80, 16.00, 15.00, 14.40])
    energy_calibrated = find_nearest(caliEng_list, energy)

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
    XIASlitY_list = np.array([21.45, 24.05, 25.05, 23.35, 26.35, 28.35, 29.35, 30.35, 31.35, 32.35, 33.35, 34.35, 34.35, 52.35, 53.35, 54.35, 51.35])    

    idx = np.where(caliEng_list==energy_calibrated)                
    if idx[0].size == 0:
        log_lib.info('     *** ERROR: there is no specified energy_calibrated in the energy_calibrated lookup table. please choose a calibrated energy_calibrated.')
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
    XIASlitY = XIASlitY_list[idx[0][0]]          

    if energy is not energy_calibrated:
        log_lib.warning('   *** Energy entered is %s keV, the closest calibrated energy is %s' % (energy, energy_calibrated))
        log_lib.info('   *** Options are %s keV' % (caliEng_list))
    else:
        log_lib.info('   *** Energy is set at %s keV' % energy_calibrated)   

    log_lib.info('   *** Move to %s keV ?' % energy_calibrated)   
    if yes_or_no('Yes or No'):
        change2mono(energy_change_PVs)                

        if energy < 20.0:
            Filter = 4
        else:                                
            Filter = 0
            
        move_filter(Filter, energy_change_PVs)
        move_mirror(Mirr_YAvg, Mirr_Ang, energy_change_PVs)
        move_DMM_Y(DMM_USY_OB, DMM_USY_IB, DMM_DSY, energy_change_PVs)    
        move_DMM_arms(USArm, DSArm, energy_change_PVs)
        move_DMM_M2Y(M2Y, energy_change_PVs)
        move_DMM_X(DMM_USX, DMM_DSX, energy_change_PVs)
        move_xia_slits_Y(XIASlitY, energy_change_PVs)

        log_lib.info(' ')
        log_lib.info('  *** Change Energy: Done!  *** ')

        return energy_calibrated
    else:
        log_lib.info(' ')
        log_lib.warning('   *** Energy not changed')


