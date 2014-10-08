#! /usr/bin/env python
# coding=utf-8
"""
函数模块
"""
import time, os, inspect
from Log import *


def getNowTimeDiff(timeData):
    ''' 获取所传时间与现在事件的差值 '''
    try:
        return float(time.time()) - float(timeData)
    except Exception, ex:
        return 0


def getDiffTime(time1, time2):
    ''' 获取所传两个时间之间的差值 '''
    return float(time1) - float(time2)


def log(name, file_name):
    ''' 保存log到日志文件 '''
    logger = Log(name, file_name)
    return logger