import os
import sys
import shutil
import pathlib
import argparse
import configparser

from collections import OrderedDict

from tomo2bm import log
from tomo2bm import util
from tomo2bm import __version__

home = os.path.expanduser("~")
LOGS_HOME = os.path.join(home, 'logs')
CONFIG_FILE_NAME = os.path.join(home, 'tomo2bm.conf')
# LOGS_HOME = os.path.join(str(pathlib.Path.home()), 'logs')
# CONFIG_FILE_NAME = os.path.join(str(pathlib.Path.home()), 'tomo2bm.conf')

SECTIONS = OrderedDict()

SECTIONS['general'] = {
    'config': {
        'default': CONFIG_FILE_NAME,
        'type': str,
        'help': "File name of configuration file",
        'metavar': 'FILE'},
    'logs-home': {
        'default': LOGS_HOME,
        'type': str,
        'help': "Log file directory",
        'metavar': 'FILE'},
    'verbose': {
        'default': False,
        'help': 'Verbose output',
        'action': 'store_true'}
        }

SECTIONS['experiment-info'] = {
    'experiment-year-month': {
        'default': None,
        'type': str,
        'help': "Experiment Year Month"},
    'user-last-name': {
        'default': None,
        'type': str,
        'help': " "},
    'user-email': {
        'default': None,
        'type': str,
        'help': " "},
    'user-badge': {
        'default': None,
        'type': str,
        'help': " "},
    'proposal-number': {
        'type': str,
        'default': None,
        'help': " "},
    'proposal-title': {
        'default': None,
        'type': str,
        'help': " "},
    'user-institution': {
        'default': None,
        'type': str,
        'help': " "},
    'user-info-update':{
        'default': None,
        'type': str,
        'help': " "},
        }

SECTIONS['detector'] = {
    'camera-ioc-prefix':{
        'choices': ['2bmbSP1:', '2bmbPG3:', '2bmbSP1:'],
        'default': '2bmbSP1:',
        'type': str,
        'help': "FLIR: 2bmbSP1:, PointGrey: 2bmbPG3:, Gbe: 2bmbSP1:"},
    'ccd-readout': {
        'choices': [0.006, 0.01],
        'default': 0.01,
        'type': float,
        'help': "8bit: 0.006; 16-bit: 0.01"},
    'exposure-time': {
        'default': 0.1,
        'type': float,
        'help': " "},
    'lens-magnification': {
        'default': 0,
        'type': float,
        'help': " "},
    'scintillator-type': {
        'default': None,
        'type': str,
        'help': " "},
    'scintillator-thickness':{       
        'default': 0,
        'type': float,
        'help': " "},
    'recursive-filter':{
        'default': False,
        'action': 'store_true',
        'help': " "},
    'recursive-filter-n-images':{
        'choices': [1, 2, 4],
        'default': 1,
        'type': util.positive_int,
        'help': " "},
    'file-write-mode': {
     'default': 'Stream',
        'type': str,
        'help': " "},
     }

SECTIONS['beamline'] = {
    'station': {
        'default': '2-BM-A',
        'type': str,
        'choices': ['2-BM-A', '2-BM-B'],
        'help': " "},
   'filters': {
        'default': None,
        'type': str,
        'help': " "},
    }

SECTIONS['sample'] = {
    'sample-name': {
        'default': None,
        'type': str,
        'help': " "},
    'sample-description': {
        'default': None,
        'type': str,
        'help': " "},
    'sample-detector-distance': {
        'default': 1,
        'type': float,
        'help': " "},
    'file-name': {
        'default': None,
        'type': str,
        'help': " "},
    'file-path': {
        'default': None,
        'type': str,
        'help': " "},
    }

SECTIONS['scan'] = {
    'scan-type': {
        'choices': ['standard', 'vertical', 'mosaic'],
        'default': 'standard',
        'type': str,
        'help': " "},
    'num-projections': {
        'type': util.positive_int,
        'default': 1500,
        'help': " "},
    'num-white-images': {
        'type': util.positive_int,
        'default': 20,
        'help': " "},
    'num-dark-images': {
        'type': util.positive_int,
        'default': 20,
        'help': " "},
    'white-field-motion': {
        'choices': ['horizontal', 'vertical'],
        'default': 'horizontal',
        'type': str,
        'help': " "},
    'sample-in-position': {
        'default': 0,
        'type': float,
        'help': "Sample position during data collection"},
    'sample-out-position': {
        'default': 1,
        'type': float,
        'help': "Sample position for white field images"},
    'sample-in-out': {
        'default': 'horizontal',
        'choices': ['horizontal', 'vertical'],
        'help': "which stage is used to take the white field"},
    'sample-move-freeze': {
        'default': False,
        'action': 'store_true',
        'help': "True: to freeze sample motion during white field data collection"},
    'sample-rotation-start': {
        'default': 0,
        'type': float,
        'help': " "},
    'sample-rotation-end': {
        'default': 180,
        'type': float,
        'help': " "},
    'vertical-scan-start': {
        'default': 0,
        'type': float,
        'help': " "},
    'vertical-scan-end': {
        'default': 1,
        'type': float,
        'help': " "},
    'vertical-scan-step-size': {
        'default': 1,
        'type': float,
        'help': " "},
    'horizontal-scan-start': {
        'default': 0,
        'type': float,
        'help': " "},
    'horizontal-scan-end': {
        'default': 1,
        'type': float,
        'help': " "},
    'horizontal-scan-step-size': {
        'default': 1,
        'type': float,
        'help': " "},
    'sleep-time': {
        'default': 0,
        'type': float,
        'help': "wait time (s) between each data collection"},
    'sleep-steps': {
        'type': util.positive_int,
        'default': 1,
        'help': " "},
    }
                                          
SECTIONS['furnace'] = {                 # True: moves the furnace  to FurnaceYOut position to take white field: 
    'use-furnace': {                    #       Note: this flag is active ONLY when both 1. and 2. are met:
        'default': False,               #           1. SampleMoveEnabled = True
        'action': 'store_true',         #           2. SampleInOutVertical = False  
        'help': " "},
    'furnace-in-position': {
        'default': 0,
        'type': float,
        'help': " "},
    'furnace-out-position': {
        'default': 48,
        'type': float,
        'help': " "},
    }

SECTIONS['file-transfer'] = {
    'remote-analysis-dir': {
        'default':  'tomo@mona3:/local/data/',
        'type': str,
        'help': " "},
    'remote-data-transfer ': {
        'default': False,
        'action': 'store_true',
        'help': " "},
    }

SECTIONS['stage-settings'] = {
    'accl_rot': {
        'default':  1.0,
        'type': float,
        'help': " "},
    'slew_speed': {
        'default':  1.0,
        'type': float,
        'help': " "}, 
    }

SCAN_PARAMS = ('experiment-info', 'detector', 'beamline', 'sample', 'scan', 'furnace', 'file-transfer', 'stage-settings')

NICE_NAMES = ('general', 'experiment info', 'detector', 'beam line', 'sample', 'scan', 'furnace', 'file transfer', 'stage settings')


def get_config_name():
    """Get the command line --config option."""
    name = CONFIG_FILE_NAME
    for i, arg in enumerate(sys.argv):
        if arg.startswith('--config'):
            if arg == '--config':
                return sys.argv[i + 1]
            else:
                name = sys.argv[i].split('--config')[1]
                if name[0] == '=':
                    name = name[1:]
                return name

    return name


def parse_known_args(parser, subparser=False):
    """
    Parse arguments from file and then override by the ones specified on the
    command line. Use *parser* for parsing and is *subparser* is True take into
    account that there is a value on the command line specifying the subparser.
    """
    if len(sys.argv) > 1:
        subparser_value = [sys.argv[1]] if subparser else []
        config_values = config_to_list(config_name=get_config_name())
        values = subparser_value + config_values + sys.argv[1:]
        #print(subparser_value, config_values, values)
    else:
        values = ""

    return parser.parse_known_args(values)[0]


def config_to_list(config_name=CONFIG_FILE_NAME):
    """
    Read arguments from config file and convert them to a list of keys and
    values as sys.argv does when they are specified on the command line.
    *config_name* is the file name of the config file.
    """
    result = []
    config = configparser.ConfigParser()

    if not config.read([config_name]):
        return []

    for section in SECTIONS:
        for name, opts in ((n, o) for n, o in SECTIONS[section].items() if config.has_option(section, n)):
            value = config.get(section, name)

            if value is not '' and value != 'None':
                action = opts.get('action', None)

                if action == 'store_true' and value == 'True':
                    # Only the key is on the command line for this action
                    result.append('--{}'.format(name))

                if not action == 'store_true':
                    if opts.get('nargs', None) == '+':
                        result.append('--{}'.format(name))
                        result.extend((v.strip() for v in value.split(',')))
                    else:
                        result.append('--{}={}'.format(name, value))

    return result
   

class Params(object):
    def __init__(self, sections=()):
        self.sections = sections + ('general', )

    def add_parser_args(self, parser):
        for section in self.sections:
            for name in sorted(SECTIONS[section]):
                opts = SECTIONS[section][name]
                parser.add_argument('--{}'.format(name), **opts)

    def add_arguments(self, parser):
        self.add_parser_args(parser)
        return parser

    def get_defaults(self):
        parser = argparse.ArgumentParser()
        self.add_arguments(parser)

        return parser.parse_args('')


def write(config_file, args=None, sections=None):
    """
    Write *config_file* with values from *args* if they are specified,
    otherwise use the defaults. If *sections* are specified, write values from
    *args* only to those sections, use the defaults on the remaining ones.
    """
    config = configparser.ConfigParser()
    for section in SECTIONS:
        config.add_section(section)
        for name, opts in SECTIONS[section].items():
            if args and sections and section in sections and hasattr(args, name.replace('-', '_')):
                value = getattr(args, name.replace('-', '_'))
                if isinstance(value, list):
                    # print(type(value), value)
                    value = ', '.join(value)
            else:
                value = opts['default'] if opts['default'] is not None else ''

            prefix = '# ' if value is '' else ''

            if name != 'config':
                config.set(section, prefix + name, str(value))


    with open(config_file, 'w') as f:
        config.write(f)


def log_values(args):
    """Log all values set in the args namespace.

    Arguments are grouped according to their section and logged alphabetically
    using the DEBUG log level thus --verbose is required.
    """
    args = args.__dict__

    log.warning('tomo scan status start')
    for section, name in zip(SECTIONS, NICE_NAMES):
        entries = sorted((k for k in args.keys() if k.replace('_', '-') in SECTIONS[section]))

        # print('log_values', section, name, entries)
        if entries:
            log.info(name)

            for entry in entries:
                value = args[entry] if args[entry] is not None else "-"
                log.info("  {:<16} {}".format(entry, value))

    log.warning('tomo scan status end')


def update_config(args):
       # update tomo2bm.conf
        sections = SCAN_PARAMS
        write(args.config, args=args, sections=sections)

        # copy tomo2bm.conf to the raw data directory with a unique name (sample_name.conf)
        log_fname = args.file_path + os.sep + args.file_name + '.conf'
        try:
            shutil.copyfile(args.config, log_fname)
            log.info('  *** copied %s to %s ' % (args.config, log_fname))
        except:
            log.error('  *** attempt to copy %s to %s failed' % (args.config, log_fname))
            pass
        log.warning(' *** command to repeat the scan: tomo scan --config {:s}'.format(log_fname))
