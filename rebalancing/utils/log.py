import logging

from rebalancing.config import Config


def get_logger(name: str = 're-balancing',
               log_level: int = None,
               use_stream: bool = True,
               use_file: bool = True,
               path: str = None):
    # get log format
    log_format = Config.get('core', 'LOG_FORMAT')

    # get or create logger
    logger = logging.getLogger(name)

    # set log level
    if log_level is None:
        log_level = logging.INFO
    logger.setLevel(log_level)

    # delete all handlers
    remove_logger(logger=logger)

    # create formatter
    formatter = logging.Formatter(log_format,
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # stream handler
    if use_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if use_file:
        if not path:
            path = 'process.log'
        file_handler = logging.FileHandler(path, mode="w", encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def remove_logger(logger_name: str = None, logger: logging.Logger = None):
    if logger_name is not None:
        logger = logging.getLogger(logger_name)

    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
