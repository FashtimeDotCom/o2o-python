#! /usr/bin/env python
# coding=utf-8
"""
标签检查服务
"""
import redis, json, threading, time, os, multiprocessing
from DataBase import *
from Var import *
import function
from CacheData import *


class TagCheck(multiprocessing.Process):
    '''
    标签检查类，分别启动在架、在架到临架、临架到在架、临架到离架、在架到离家和离架的线程不断检测各处于这些状态的标签
    '''

    def __init__(self):
        '''
        标签检查进程初始化函数
        '''
        multiprocessing.Process.__init__(self)
        self.r = None
        self.dataBase = None
        self.cacheData = None
        self.threads = []

    def process(self):
        '''
        主操作
        '''
        func = [self.onLine, self.workLine, self.workToOnLine, self.workToOffLine, self.onToOffLine, self.offLine]
        self.threads.append(threading.Thread(target=self.onLine))
        self.threads.append(threading.Thread(target=self.workLine))
        self.threads.append(threading.Thread(target=self.workToOnLine))
        self.threads.append(threading.Thread(target=self.workToOffLine))
        self.threads.append(threading.Thread(target=self.onToOffLine))
        self.threads.append(threading.Thread(target=self.offLine))
        for thread in self.threads:
            thread.start()
        while True:
            self.r.ping()
            for i in range(0, 6):
                if self.threads[i].isAlive() == False:
                    self.threads[i] = threading.Thread(target=func[i])
                    self.threads[i].start()

    def run(self):
        '''
        入口函数
        '''
        try:
            self.r = redis.StrictRedis(host=Var.REDIS_HOST, port=Var.REDIS_PORT, db=Var.REDIS_DB)
            self.dataBase = DataBase()
            self.cacheData = CacheData()
            self.process()
        except Exception, ex:
            function.log("TagCheck error", "error.log").error(ex)


    def test(self):
        self.r = redis.StrictRedis(host=Var.REDIS_HOST, port=Var.REDIS_PORT, db=Var.REDIS_DB)
        self.dataBase = DataBase()
        self.workLine()


    def onLine(self):
        '''
        在架处理方法
        '''
        try:
            while True:
                for DeviceID in self.r.smembers(Var.REDIS_DEVICE_KEY):
                    epcs = self.r.get(DeviceID)  # 所有标签库
                    if epcs != None and len(epcs):
                        epcs = json.loads(epcs)
                        needIds = []
                        for key, epc in epcs.items():  # 判断是否在架
                            onEpc = {'tagEPC': epc['EPC'], 'lastTime': epc['TimeStamp'], \
                                     'RSSI': epc['RSSI'], 'Frequency': epc['Frequency'], 'OnLineTimes': 0, \
                                     'TID': epc['TID'], 'Times': 1, 'DeviceID': DeviceID, 'ant': epc['AntennaID'],
                                     'desp': ''}

                            # 构建需要缓存的EPC列表
                            needIds.append(epc['EPC'])

                            groupID = self.getGroupID(DeviceID, epc['AntennaID'])
                            if groupID == None:
                                return
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
                                    if onEpc['lastTime'] > onEpcs[key]['lastTime'] and int(epc['Times']) >= groupConfig[
                                        'online_min_times']:
                                        onEpcs[key]['lastTime'] = onEpc['lastTime']  # 更新时间

                            self.r.hset(groupID, 'on', json.dumps(onEpcs))
                            self.r.sadd(Var.REDIS_GROUP_KEY, groupID)

                        # 在新线程中缓存数据
                        if needIds:
                            self.cacheData.realCache(needIds)

                time.sleep(0.001)

        except Exception, ex:
            print "TagCheck onLine function error:\n"
            print ex
            # function.log("TagCheck onLine error","error.log").error(ex)


    def workLine(self):
        '''
        在架到临架处理方法
        '''
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
                                if key in workEpcs.keys():
                                    times = workEpcs[onEpc['tagEPC']]['Times'] + 1
                                else:
                                    times = 1

                                workEpcs[onEpc['tagEPC']] = onEpc
                                workEpcs[onEpc['tagEPC']]['Times'] = times

                                # 加载缓存中的数据
                                if self.cacheData.cachedDatas:
                                    workEpcs[onEpc['tagEPC']]['Datas'] = self.cacheData.getData(onEpc['tagEPC'])
                                else:
                                    workEpcs[onEpc['tagEPC']]['Datas'] = {}

                        self.r.hset(groupID, 'work', json.dumps(workEpcs))
                time.sleep(0.01)

        except Exception, ex:
            function.log("TagCheck workLine error", "error.log").error(ex)

    def workToOffLine(self):
        '''
        临架到离架处理方法
        '''
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

    def workToOnLine(self):
        '''
        临架到在架处理方法
        '''
        try:
            while True:
                for groupID in self.r.smembers(Var.REDIS_GROUP_KEY):

                    groupConfig = self.dataBase.getGroupsConfig(groupID)
                    workEpcs = self.r.hget(groupID, 'work')

                    if workEpcs != None:
                        workEpcs = json.loads(workEpcs)
                        onEpcs = self.r.hget(groupID, 'on')

                        if onEpcs != None:
                            onEpcs = json.loads(onEpcs)

                        for key, workEpc in workEpcs.items():

                            if key in onEpcs.keys():
                                if function.getNowTimeDiff(onEpcs[key]['lastTime']) <= groupConfig['workline_min_time']:
                                    workEpcs[key]['OnLineTimes'] = workEpcs[key]['OnLineTimes'] + 1
                                    # print workEpcs[key]['OnLineTimes']
                                    if workEpcs[key]['OnLineTimes'] == 5:
                                        workEpcs[key]['lastTime'] = time.time() - groupConfig['offline_max_time'] + \
                                                                    groupConfig['workline_stop_time']

                    self.r.hset(groupID, 'work', json.dumps(workEpcs))
                time.sleep(0.01)

        except Exception, ex:
            print "TagCheck workToLine  function error:\n"
            print ex
            function.log("TagCheck workToOffLine error", "error.log").error(ex)


    def onToOffLine(self):
        '''
        在架到离架处理方法
        '''
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

    def offLine(self):
        '''
        离架到在架处理方法
        '''
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
        '''
        设置离架数据
        '''
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
