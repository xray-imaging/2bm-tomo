import logging

class Logger(object):
    __GREEN = "\033[92m"
    __RED = '\033[91m'
    __YELLOW = '\033[33m'
    __ENDC = '\033[0m'

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.extra={'logger_name': name, 'endColor': self.__ENDC, 'color': self.__GREEN}

    def info(self, msg):
        self.extra['color'] = self.__GREEN
        self.logger.info(msg, extra=self.extra)

    def error(self, msg):
        self.extra['color'] = self.__RED
        self.logger.error(msg, extra=self.extra)

    def warning(self, msg):
        self.extra['color'] = self.__YELLOW
        self.logger.warning(msg, extra=self.extra)


def setup_logger(log_name, stream_to_console=True):
    logger = logging.getLogger(log_name)
    fHandler = logging.FileHandler(log_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(color)s  %(message)s %(endColor)s")
    fHandler.setFormatter(formatter)
    logger.addHandler(fHandler)
    if stream_to_console:
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(color)s  %(message)s %(endColor)s")
        ch.setFormatter(formatter)
        # ch.setLevel(logging.WARNING)
        logger.addHandler(ch)
    
    return logger, fHandler