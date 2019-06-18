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

    # shutter PVs
    global_PVs['LoadVoltage'] = PV('2bmS1:D1Dmm_raw')
    global_PVs['LoadNewton'] = PV('2bmS1:D1Dmm_calc')
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

    lfname = logs_home + 'load_' + datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S") + '.log'
    log_lib.setup_logger(lfname)
   
    init_general_PVs(global_PVs, variableDict)
    try:
        while True:
            h5fname = global_PVs['HDF1_FullFileName_RBV'].get()
            h5fname_str = "".join([chr(item) for item in h5fname])
            log_lib.info('Load: %4.4f N (%4.4f V): %s' % (global_PVs['LoadNewton'].get(), global_PVs['LoadVoltage'].get(), h5fname_str))
            time.sleep(2)   
    except KeyboardInterrupt:
    
        print('interrupted!')
    
    
if __name__ == '__main__':
    main()
