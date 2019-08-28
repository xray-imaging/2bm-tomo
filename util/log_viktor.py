#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Log PV in a file
    
'''
from __future__ import print_function

import os
import time
import numpy as np

from epics import PV
from datetime import datetime

import log_lib

variableDict = {
        'IOC_Prefix': '2bmbSP1:',         # options: 1. PointGrey: '2bmbPG3:', 2. Gbe '2bmbSP1:' 
        'Station': '2-BM-A'
        }

global_PVs = {}


def init_general_PVs(global_PVs, variableDict):

    # shutter PVs 2bma:D1Dmm_raw.VAL
    global_PVs['Temperature'] = PV('2bma:D1Dmm_raw')
    global_PVs['Voltage'] = PV('2bmS1:D1Dmm_raw')
    global_PVs['HDF1_FullFileName_RBV'] = PV(variableDict['IOC_Prefix'] + 'HDF1:FullFileName_RBV')


def main():

    # create logger
    # # python 3.5+ 
    # home = str(pathlib.Path.home())
    home = os.path.expanduser("~")
    logs_home = home + '/logs/'

    # make sure logs directory exists
    if not os.path.exists(logs_home):
        os.makedirs(logs_home)

    lfname = logs_home + 'viktor_' + datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S") + '.log'
    log_lib.setup_logger(lfname)
   
    init_general_PVs(global_PVs, variableDict)
    try:
        while True:
            h5fname = global_PVs['HDF1_FullFileName_RBV'].get()
            h5fname_str = "".join([chr(item) for item in h5fname])
            temp = global_PVs['Temperature'].get()
            pressure = global_PVs['Voltage'].get()*1500/4.8434 # to calibrate 
            log_lib.warning('Temperature: %4.4f C;  Pressure: %4.4f psi: %s' % (temp, pressure, h5fname_str))            
            time.sleep(5)   
    except KeyboardInterrupt:
    
        print('interrupted!')
    
    
if __name__ == '__main__':
    main()
