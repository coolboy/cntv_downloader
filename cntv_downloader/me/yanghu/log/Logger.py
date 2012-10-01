# -*- coding: utf-8 -*-

'''
Created on Sep 18, 2012

@author: coolcute
'''

import logging

_logFilePath = 'log.log'

def setLogFilePath(filePath):
    _logFilePath = filePath

def createLogger(loggerName):
    logging.disable(logging.NOTSET)
    
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.INFO)
    
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # create console handler
    sh = logging.StreamHandler()
#    sh.setLevel(logging.WARN)
#    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    
    # create file handler
    fh = logging.FileHandler(_logFilePath, mode='a', encoding='utf-8')
#    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    
    # append handlers
    logger.addHandler(sh)
    logger.addHandler(fh)
    
    return logger