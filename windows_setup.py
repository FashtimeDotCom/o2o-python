#! /usr/bin/env python
# coding=utf-8
"""
windows服务进程
"""
import win32service
import win32service
import win32event
import win32api, win32pdhutil, win32con

try:
    import IDF
except Exception, ex:
    log("IDF_SERVICE").error(ex)
    rsys.exit()


def log(service_name):
    import logging
    import os
    import inspect

    logger = logging.getLogger(service_name)
    this_file = inspect.getfile(inspect.currentframe())
    dirpath = os.path.abspath(os.path.dirname(this_file))
    handler = logging.FileHandler(os.path.join(dirpath, "service.log"))

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


class IDF_SERVICE(win32service.ServiceFramework):
    _svc_name_ = "IDF_SERVICE"
    _svc_display_name_ = "IDF_SERVICE"
    _svc_description_ = "IDF include tagcheck and socket and scan service"

    def _getLogger(self):
        return log(self._svc_name_)


    def __init__(self, args):
        win32service.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        self.logger.info("IDF SERVICE start....")

    def SvcStop(self):
        self.logger.info("IDF SERVICE stop....")
        try:
            pids = win32pdhutil.FindPerformanceAttributesByName("python")
            pids2 = win32pdhutil.FindPerformanceAttributesByName("pythonservice")
            pids.extend(pids2)
            for i in range(len(pids)):
                handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pids[i])
                win32api.TerminateProcess(handle, 0)  # kill by handle
                win32api.CloseHandle(handle)
        except Exception, ex:
            pass

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.logger.info("IDF SERVICE run....")
        try:
            IDF.run()
        except Exception, ex:
            self.logger.error(ex)
            return
            # 这个函数内的上面部分都是逻辑处理的部分，可以根据自己的需求订制，但下面这行代码任何服务都需要
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)


if __name__ == '__main__':
    win32service.HandleCommandLine(IDF_SERVICE)