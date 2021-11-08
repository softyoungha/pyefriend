import logging


def get_logger(name: str, log_level: int = None, use_stream: bool = True):
    logger = logging.getLogger(name)

    if log_level is None:
        log_level = logging.INFO

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
