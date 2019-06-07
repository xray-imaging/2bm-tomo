'''
    Data Management Lib for Sector 2-BM internal data transfer
    
'''
from __future__ import print_function

import sys
import json
import time
from epics import PV
import h5py
import shutil
import os
import imp
import traceback
import math
import signal
import logging
import numpy as np
import pathlib
from paramiko import SSHClient
from scp import SCPClient

import log_lib


def scp(global_PVs, variableDict):
    log_lib.Logger(variableDict['LogFileName']).info('  *** start scp')
    fname_origin = global_PVs['HDF1_FullFileName_RBV'].get(as_string=True)
    fname_destination = '/local/data/2019-06/test/'
    log_lib.Logger(variableDict['LogFileName']).info('  *** *** origin: %s' % fname_origin)
    log_lib.Logger(variableDict['LogFileName']).info('  *** *** destination: %s' % fname_destination)
    os.system("scp " + fname_origin + " tomo@handyn:" +  fname_destination + '&')
    log_lib.Logger(variableDict['LogFileName']).info('  *** start scp: Done!')

    
