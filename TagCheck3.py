#! /usr/bin/env python
# coding=utf-8
"""
标签检查服务
"""
import redis, json, threading, time, os, multiprocessing
from DataBase import *
from Var import *
import function


class TagCheck(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.r = None
        self.dataBase = None
        self.threads = []

    def process(self):
        func = [self.onLine, self.workLine, self.workToOffLine, self.onToOffLine, self.offLine]
        self.threads.append(threading.Thread(target=self.onLine))
        self.threads.append(threading.Thread(target=self.workLine))
        self.threads.append(threading.Thread(target=self.workToOffLine))
        self.threads.append(threading.Thread(target=self.onToOffLine))
        self.threads.append(threading.Thread(target=self.offLine))
        for thread in self.threads:
            thread.start()
        while True:
            self.r.ping()
            for i in range(0, 5):
                if self.threads[i].isAlive() == False:
                    self.threads[i] = threading.Thread(target=func[i])
                    self.threads[i].start()

    def run(self):
        try:
            self.r = redis.StrictRedis(host=Var.REDIS_HOST, port=Var.REDIS_PORT, db=Var.REDIS_DB)
            self.dataBase = DataBase()
            self.process()
        except Exception, ex:
            function.log("TagCheck error", "error.log").error(ex)


    def test(self):
        self.r = redis.StrictRedis(host=Var.REDIS_HOST, port=Var.REDIS_PORT, db=Var.REDIS_DB)
        self.dataBase = DataBase()
        self.workLine()


    def onLine(self):  # 在架
        try:
            while True:
                for DeviceID in self.r.smembers(Var.REDIS_DEVICE_KEY):
                    epcs = self.r.get(DeviceID)  # 所有标签库
                    if epcs != None and len(epcs):
                        epcs = json.loads(epcs)
                        for key, epc in epcs.items():  # 判断是否在架
                            onEpc = {'tagEPC': epc['EPC'], 'lastTime': epc['TimeStamp'], \
                                     'RSSI': epc['RSSI'], 'Frequency': epc['Frequency'], \
                                     'TID': epc['TID'], 'Times': 1, 'DeviceID': DeviceID, 'ant': epc['AntennaID'],
                                     'desp': ''}

                            groupID = self.getGroupID(DeviceID, epc['AntennaID'])

                            groupConfig = self.dataBase.getGroupsConfig(groupID)
                            onEpcs = self.r.hget(groupID, 'on')  # 在架标签库

                            if onEpcs == None:
                                onEpcs = dict()
                            else:
                                onEpcs = json.loads(onEpcs)

                            if function.getNowTimeDiff(epc['TimeStamp']) < groupConfig['online_max_time'] and int(
                                    epc['Times']) >= groupConfig['online_min_times']:

                                if key in onEpcs.keys():
                                    onEpcs[key]['Times'] = onEpcs[key]['Times'] + onEpc['Times']

                                    onEpcs[key]['lastTime'] = onEpc['lastTime']
                                else:
                                    onEpcs[onEpc['tagEPC']] = onEpc
                            else:
                                if key in onEpcs.keys():
                                    onEpcs[key]['lastTime'] = onEpc['lastTime']  # 更新时间

                            self.r.hset(groupID, 'on', json.dumps(onEpcs))
                            self.r.sadd(Var.REDIS_GROUP_KEY, groupID)
                time.sleep(0.001)

        except Exception, ex:
            print "TagCheck onLine function error:\n"
            print ex
            # function.log("TagCheck onLine error","error.log").error(ex)


    def workLine(self):  # 在架到临架
        try:
            while True:
                for groupID in self.r.smembers(Var.REDIS_GROUP_KEY):

                    groupConfig = self.dataBase.getGroupsConfig(groupID)
                    onEpcs = self.r.hget(groupID, 'on')

                    workEpcs = self.r.hget(groupID, 'work')
                    if onEpcs != None:
                        onEpcs = json.loads(onEpcs)

                        if workEpcs != None:
                            workEpcs = json.loads(workEpcs)

                        if isinstance(workEpcs, dict) == False:
                            workEpcs = dict()

                        for key, onEpc in onEpcs.items():  # 在架标签
                            try:
                                diff = function.getNowTimeDiff(onEpc['lastTime'])
                            except:
                                continue
                            if diff > groupConfig['workline_min_time'] and diff < groupConfig['workline_max_time']:
                                workEpcs[onEpc['tagEPC']] = onEpc

                            elif diff > groupConfig['offline_max_time']:  #删除时间长的标签
                                self.setOffLineData(groupID, onEpc)
                                del onEpcs[key]

                        self.r.hset(groupID, 'work', json.dumps(workEpcs))
                        self.r.hset(groupID, 'on', json.dumps(onEpcs))
                time.sleep(0.01)

        except Exception, ex:
            function.log("TagCheck workLine error", "error.log").error(ex)

    def workToOffLine(self):  # 临架到离架
        try:
            while True:
                for groupID in self.r.smembers(Var.REDIS_GROUP_KEY):

                    groupConfig = self.dataBase.getGroupsConfig(groupID)
                    workEpcs = self.r.hget(groupID, 'work')

                    if workEpcs != None:
                        workEpcs = json.loads(workEpcs)

                        if isinstance(workEpcs, dict) == False:
                            workEpcs = dict()

                        for key, workEpc in workEpcs.items():
                            if function.getNowTimeDiff(workEpc['lastTime']) > groupConfig['offline_max_time']:
                                self.setOffLineData(groupID, workEpc)
                                del workEpcs[key]

                    self.r.hset(groupID, 'work', json.dumps(workEpcs))
                time.sleep(0.01)

        except Exception, ex:
            print "TagCheck workToOffLine  function error:\n"
            print ex
            function.log("TagCheck workToOffLine error", "error.log").error(ex)

    def onToOffLine(self):  # 在架到离架
        try:
            while True:
                for groupID in self.r.smembers(Var.REDIS_GROUP_KEY):

                    groupConfig = self.dataBase.getGroupsConfig(groupID)
                    onEpcs = self.r.hget(groupID, 'on')

                    if onEpcs != None:
                        onEpcs = json.loads(onEpcs)

                        for key, onEpc in onEpcs.items():
                            if function.getNowTimeDiff(onEpc['lastTime']) > groupConfig['offline_max_time']:
                                self.setOffLineData(groupID, onEpc)
                                del onEpcs[key]

                    self.r.hset(groupID, 'on', json.dumps(onEpcs))
                time.sleep(0.01)

        except Exception, ex:
            print "TagCheck onToOffLine function error:\n"
            print ex
            function.log("TagCheck onToOffLine error", "error.log").error(ex)

    def offLine(self):  # 离架到在架
        try:
            while True:
                AllOnEpcs = []
                for groupID in self.r.smembers(Var.REDIS_GROUP_KEY):
                    onEpcs = self.r.hget(groupID, 'on')
                    if onEpcs != None:
                        AllOnEpcs.append(json.loads(onEpcs))

                for groupID in self.r.smembers(Var.REDIS_GROUP_KEY):

                    groupConfig = self.dataBase.getGroupsConfig(groupID)
                    offEpcs = self.r.hget(groupID, 'off')

                    if isinstance(offEpcs, dict) == False:
                        offEpcs = dict()

                    if len(offEpcs):
                        offEpcs = json.loads(offEpcs)

                        for key, offEpc in offEpcs.items():
                            for onEpcs in AllOnEpcs:
                                if key in onEpcs.keys():
                                    if function.getNowTimeDiff(onEpcs[key]['lastTime']) < groupConfig[
                                        'offline_max_time']:
                                        del offEpcs[key]

                    self.r.hset(groupID, 'off', json.dumps(offEpcs))

        except Exception, ex:
            print "TagCheck offLine function error:\n"
            print ex
            function.log("TagCheck offLine error", "error.log").error(ex)

    def setOffLineData(self, groupID, offEpc):
        offEpcs = self.r.hget(groupID, 'off')
        if offEpcs == None:
            offEpcs = dict()
        else:
            offEpcs = json.loads(offEpcs)

        offEpcs[offEpc['tagEPC']] = offEpc
        self.r.hset(groupID, 'off', json.dumps(offEpcs))


    def getGroupID(self, DeviceID, ant):
        for groupID, groupInfo in self.dataBase.groupsInfo.items():
            for group in groupInfo:
                if DeviceID.startswith(group['readerIP']) and group['antID'] == ant:
                    return groupID

        return None
