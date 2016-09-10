import logging
import Utils

def setup_custom_logger(name):
    logging.addLevelName(5, 'TRACE')
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.newline = print
    logger.addFilter(Utils.ColorizeFilter())
    logger.addHandler(handler)
    setattr(logger, 'trace', lambda *args: logger.log(5, *args))
    return logger
