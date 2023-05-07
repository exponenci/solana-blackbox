import logging


formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


class SAResult:
    def __init__(self, filename) -> None:
        # dump to filename result of runs (with values of x, y, etc)
        pass


class SALogger:
    def __init__(self) -> None:
        self.logger = setup_logger('SALogger', 'sa_logger.log') # different loggers for different methods?
