#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Log PV in a file
    
'''
from __future__ import print_function

import datetime
import time
import numpy as np


from epics import PV

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

    logfile = 'load'
    fname = logfile + '.txt'
   
    init_general_PVs(global_PVs, variableDict)
    try:
        with open(fname, 'a+') as f:
            while True:
                h5fname = global_PVs['HDF1_FullFileName_RBV'].get()
                h5fname_str = "".join([chr(item) for item in h5fname])
                f.write('%s; Load: %4.4f N (%4.4f V): %s\n' % (datetime.datetime.now().isoformat(), \
                        global_PVs['LoadNewton'].get(), global_PVs['LoadVoltage'].get(), h5fname_str))
                print('%s %s; Load: %4.4f N (%4.4f V)' % (h5fname_str, datetime.datetime.now().isoformat(), \
                        global_PVs['LoadNewton'].get(), global_PVs['LoadVoltage'].get()))
                time.sleep(2)   
    except KeyboardInterrupt:
    
        print('interrupted!')
    
    
if __name__ == '__main__':
    main()
