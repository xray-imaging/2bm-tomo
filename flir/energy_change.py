import time
import epics
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

import libs.aps2bm_lib as aps2bm_lib
import libs.log_lib as log_lib


global variableDict

variableDict = {
        'Station': '2-BM-A',
        'IOC_Prefix': '2bmbSP1:',         # options: 1. PointGrey: '2bmbPG3:', 2. Gbe '2bmbSP1:' 
        # 'Projections': 1500,
        # 'NumDarkImages': 20,
        # 'NumWhiteImages': 20,
        # 'SampleXIn': 0.0,
        # 'SampleXOut': 5,
        # 'SampleStartPos': 0.0,
        # 'SampleEndPos': 180.0,
        # 'StartSleep_min': 0,
        # 'SlewSpeed': 1.0,
        # 'ExposureTime': 0.1,
        # 'ExposureTime_flat': 0.1,
        # 'ShutterOpenDelay': 0.00,
        # 'IOC_Prefix': 'PCOIOC3:', # options: 'PCOIOC2:', 'PCOIOC3:'
        # 'FileWriteMode': 'Stream',
        # 'CCD_Readout': 0.05,
        # 'AcclRot': 1.0,
        # 'EnergyPink': 2.657, # for now giver in mirror angle in rads
        # 'EnergyMono': 24.9
#        'camScanSpeed': 'Normal', # options: 'Normal', 'Fast', 'Fastest'
#        'camShutterMode': 'Rolling'# options: 'Rolling', 'Global''
        }

global_PVs = {}


def getVariableDict():
    global variableDict
    return variableDict

    
def main():
    # create logger
    # # python 3.5+ 
    # home = str(pathlib.Path.home())
    home = os.path.expanduser("~")
    logs_home = home + '/logs/'

    # make sure logs directory exists
    if not os.path.exists(logs_home):
        os.makedirs(logs_home)

    lfname = logs_home + 'energy.log'
    log_lib.setup_logger(lfname)

    aps2bm_lib.init_general_PVs(global_PVs, variableDict)
    angle_calibrated = aps2bm_lib.change2Pink()
    energy_calibrated = aps2bm_lib.setEnergy()
 
    
if __name__ == '__main__':
    main()
