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
    log_lib.info('  *** start scp')
    fname_origin = global_PVs['HDF1_FullFileName_RBV'].get(as_string=True)
    p = pathlib.Path(fname_origin)

    fname_destination = variableDict['RemoteAnalyisDir'] + p.parts[-3] + '/' + p.parts[-2] + '/'

    log_lib.info('  *** *** origin: %s' % fname_origin)
    log_lib.info('  *** *** destination: %s' % fname_destination)

    err = os.system('scp -q ' + fname_origin + ' ' + fname_destination + '&')
    if (err == 0):
        log_lib.info('  *** start scp: Done!')
    else:
        log_lib.error('  *** scp error: check that destination directory exists at %s' % (fname_destination))
    
