'''
    Data Management Lib for Sector 2-BM internal data transfer
    
'''
from __future__ import print_function

import os
import pathlib
from paramiko import SSHClient
from scp import SCPClient

import log_lib


def scp(global_PVs, variableDict):
    log_lib.Logger(variableDict['LogFileName']).info('  *** start scp')
    fname_origin = global_PVs['HDF1_FullFileName_RBV'].get(as_string=True)
    p = pathlib.Path(fname_origin)

    fname_destination = variableDict['RemoteAnalyisDir'] + p.parts[-3] + '/' + p.parts[-2] + '/'

    log_lib.Logger(variableDict['LogFileName']).info('  *** *** origin: %s' % fname_origin)
    log_lib.Logger(variableDict['LogFileName']).info('  *** *** destination: %s' % fname_destination)

    # os.system('scp ' + fname_origin + ' ' + fname_destination)
    os.system('scp ' + fname_origin + ' ' + fname_destination + '&')
    log_lib.Logger(variableDict['LogFileName']).info('  *** start scp: Done!')

    
