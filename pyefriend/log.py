import os
import logging


LOG_LEVEL = os.getenv('PYEFRIEND__LOG_LEVEL')


def get_logger(name: str, log_level: int = logging.INFO, use_stream: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)

    # get log level
    log_level = logging.getLevelName(LOG_LEVEL or log_level)

    # set log level
    logger.setLevel(log_level)

    # create formatter
    formatter = logging.Formatter('[%(levelname)s]'
                                  '[%(name)s]'
                                  '[%(pathname)s - %(funcName)s, %(lineno)s] '
                                  '%(asctime)s: %(message)s')

    # stream handler
    if use_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


logger = get_logger('pyefriend')
