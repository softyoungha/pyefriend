import os
import logging


LOG_LEVEL = os.getenv('PYEFRIEND__LOG_LEVEL')


def get_logger(name: str = 'pyefriend',
               log_level: int = logging.INFO,
               use_stream: bool = True,
               use_file: bool = True,
               path: str = None) -> logging.Logger:
    logger = logging.getLogger(name)

    # get log level
    log_level = logging.getLevelName(LOG_LEVEL or log_level)

    # set log level
    logger.setLevel(log_level)

    # create formatter
    formatter = logging.Formatter('[%(levelname)s]'
                                  '%(asctime)s - '
                                  '%(name)s/%(filename)s/%(funcName)s, '
                                  '%(lineno)s: '
                                  '%(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # stream handler
    if use_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if use_file:
        if not path:
            path = 'process.log'
        file_handler = logging.FileHandler(path, mode="w")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = get_logger(use_file=False)
