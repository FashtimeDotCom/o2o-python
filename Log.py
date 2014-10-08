#! /usr/bin/env python
# coding=utf-8
import logging
import inspect
import os


class Log:
    def __init__(self, name, file_name):
        self.logger = logging.getLogger(name)
        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.join(os.path.dirname(this_file), 'log'))
        self.handler = logging.FileHandler(os.path.join(dirpath, file_name))
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        self.handler.setFormatter(formatter)

    def debug(self, msg):
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)
        self.logger.debug(msg)
        self.logger.removeHandler(self.handler)

    def error(self, msg):
        self.logger.setLevel(logging.ERROR)
        self.logger.addHandler(self.handler)
        self.logger.error(msg)
        self.logger.removeHandler(self.handler)

    def info(self, msg):
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)
        self.logger.info(msg)
        self.logger.removeHandler(self.handler)
    