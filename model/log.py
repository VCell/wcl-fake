
import logging

def init_logging():
    LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s "
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=logging.DEBUG,
                        format=LOG_FORMAT,
                        datefmt = DATE_FORMAT ,
                        filename=r'log/main.log'
                        )
    logging.info('logging initialized')