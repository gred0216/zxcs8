from zxcs8 import *
import logging


def main():
    logger = set_log()
    logger.info('scrawler start')

    logger.info('scrawler stop')


def set_log():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

    # filehandler write to scrawler.log under current working directory
    fh = logging.FileHandler('scrawler.log', encoding='UTF-8')
    fh.setFormatter(formatter)

    # streamhandler only print out log warning or above
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.WARNING)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


if __name__ == '__main__':
    main()
