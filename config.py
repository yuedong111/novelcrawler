# -*- coding: utf-8 -*-
import logging
import logging.config
from logging.handlers import RotatingFileHandler

logging.config.fileConfig("logger.conf")
loggerinfo = logging.getLogger('root')
loggererror = logging.getLogger('chep')


