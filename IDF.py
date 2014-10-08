#! /usr/bin/env python
# coding=utf-8
"""
IDF程序调用
"""
from Scan import *
from TagCheck import *
from Var import *
from Socket import *
from Monitor import *


def run():
    '''不断运行Socket、Monitor、Scan和TagCheck模块'''
    ProcessList = ['Socket', 'Monitor', 'Scan', 'TagCheck']
    ps = []
    multiprocessing.freeze_support()
    # 开启各个模块进程
    for i in range(0, len(ProcessList)):
        ps.append(eval(ProcessList[i])())
        ps[i].start()

    while True:
        # 不断运行Socket、Monitor、Scan和TagCheck模块
        for i in range(0, len(ProcessList)):
            if ps[i].is_alive() == False:
                function.log("MAIN PROCESS ", "error.log").error("Process " + ProcessList[i] + " shutdown...")
                ps[i] = eval(ProcessList[i])()
                ps[i].start()
        time.sleep(1)