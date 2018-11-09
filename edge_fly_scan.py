import time
import epics
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

from pco_lib import *


global variableDict

variableDict = {'PreDarkImages': 0,
        'PreWhiteImages': 0,
        'Projections': 1500,
        'PostDarkImages': 20,
        'PostWhiteImages': 20,
        'SampleXIn': 0.0,
        'SampleXOut': 5,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'StartSleep_min': 0,
        'SlewSpeed': 1.0,
        'ExposureTime': 0.1,
        'ShutterOpenDelay': 0.00,
        'IOC_Prefix': 'PCOIOC3:', # options: 1. DIMAX: 'PCOIOC2:', 2. EDGE: 'PCOIOC3:'
        'FileWriteMode': 'Stream',
        'CCD_Readout': 0.05,
        'AcclRot': 1.0,
        'EnergyPink': 2.657, # for now giver in mirror angle in rads
        'EnergyMono': 24.9,
        'Station': '2-BM-A'
#        'camScanSpeed': 'Normal', # options: 'Normal', 'Fast', 'Fastest'
#        'camShutterMode': 'Rolling'# options: 'Rolling', 'Global''
        }

global_PVs = {}


def getVariableDict():
    global variableDict
    return variableDict
    
def main():

    tic =  time.time()
    update_variable_dict(variableDict)
    init_general_PVs(global_PVs, variableDict)
    
    try: 
        model = global_PVs['Cam1_Model'].get()
        if model == None:
            print('*** The PCO Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
            print('  *** Failed!')
        else:
            print ('*** The %s is on' % (model))            # get sample file name
            edgeInit(global_PVs, variableDict)     
            edgeTest(global_PVs, variableDict)
            setPSO(global_PVs, variableDict)

            fname = global_PVs['HDF1_FileName'].get(as_string=True)
            print('  *** File name prefix: %s' % fname)
            edgeSet(global_PVs, variableDict, fname)

            open_shutters(global_PVs, variableDict)
            edgeAcquisition(global_PVs, variableDict)
            edgeAcquireFlat(global_PVs, variableDict) 
            close_shutters(global_PVs, variableDict)
            edgeAcquireDark(global_PVs, variableDict) 

            print(' ')
            print('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
            print('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
            print('  *** Done!')

    except  KeyError:
        print('  *** Some PV assignment failed!')
        pass

   
    
    
if __name__ == '__main__':
    main()


