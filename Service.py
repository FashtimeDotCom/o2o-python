#! /usr/bin/env python
# -*- coding=utf-8 -*-
"""
客户端服务
"""
import redis, time, urllib, urllib2, os, sched, re
import json, threading
import ConfigParser
from Var import *
from DataBase import *
import function


class Service:
    ''' 客户端服务类 '''

    # 第一个参数确定任务的时间，返回从某个特定的时间到现在经历的秒数
    # 第二个参数以某种人为的方式衡量时间
    schedule = sched.scheduler(time.time, time.sleep)

    def __init__(self):
        self.dataBase = DataBase()

    def process(self, data):
        """
            处理逻辑数据
        """
        try:
            (CommandType, params) = self.getCommand(data)
            if CommandType == Var.IDF_CLIENT_COMMAND_GETTAGSLIST:
                return self.getTagsList(CommandType, params['GroupID'], params['State'])
            elif CommandType == Var.IDF_CLIENT_COMMAND_SETTING:
                return self.setting(CommandType, params['OnToNearTimes'], params['NearToOffTimes'],
                                    params['NearToOnTimes'], params['OffToOnTimes'])
            else:
                return self.output()
        except Exception, ex:
            print "Service process function error:\n"
            print ex
            return self.output()

    def getCommand(self, data):
        """
            读取命令结果
        """
        # 通过json的反序列化获取源数据
        data = json.loads(data)
        try:
            CommandType = data[u'CommandType']
            params = {}
            Key = data[u'Key']
            if u'GroupID' in data.keys():
                params['GroupID'] = data[u'GroupID']

            if u'State' in data.keys():
                State = data[u'State']
                if State == Var.COMMANDTYPE_STATE_ON_PARAM:
                    State = 'on'
                elif State == Var.COMMANDTYPE_STATE_WORK_PARAM:
                    State = 'work'
                elif State == Var.COMMANDTYPE_STATE_ON_WORK_PARAM:
                    State = 'onAndWork'
                else:
                    State = 'off'
                params['State'] = State

            if u'OnToNearTimes' in data.keys():
                params['OnToNearTimes'] = data[u'OnToNearTimes']

            if u'NearToOffTimes' in data.keys():
                params['NearToOffTimes'] = data[u'NearToOffTimes']

            if u'NearToOnTimes' in data.keys():
                params['NearToOnTimes'] = data[u'NearToOnTimes']

            if u'OnToNearTimes' in data.keys():
                params['OffToOnTimes'] = data[u'OffToOnTimes']

            if Var.SOCKET_KEY == Key:
                return (CommandType, params)
            else:
                return ("", {})
        except Exception, ex:
            print "Service command function error:\n"
            print ex
            return ("", {})


    def getTagsList(self, CommandType, groupID, state):
        ''' 获取标签列表 '''
        # 初始化redis连接对象
        r = redis.StrictRedis(host=Var.REDIS_HOST, port=Var.REDIS_PORT, db=Var.REDIS_DB)
        datas = []
        states = []
        allIds = []

        try:
            # 获取groudIds
            groupIDs = r.smembers(Var.REDIS_GROUP_KEY)
            groupConfig = self.dataBase.getGroupsConfig(groupID)
            if state == 'onAndWork':
                states.append('on')
                states.append('work')
            else:
                states.append(state)

            for state in states:
                # 获取处于指定ID和指定状态下的数据
                epcs = r.hget(groupID, state)
                
                if epcs != None:
                    epcs = json.loads(epcs)

                for key, epc in epcs.items():

                    if state == 'on':
                        diff = function.getNowTimeDiff(epc['lastTime'])
                        if diff > groupConfig['workline_min_time'] and diff < groupConfig['workline_max_time']:
                            continue

                            # elif state == 'work':
                            #      if epc['Times']<groupConfig['workline_times']:
                            #         continue

                    print 'groupID:%s ------- %s' % (groupID, epc['tagEPC'])
                    datas.append({'EPC': epc['tagEPC'], 'GroupID': groupID})

                    # print "now time: %s, workPEC time :%s , onEPC time: %s, scan EPC time: %s \n\n\n" \
                    #    % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),epc['lastTime'], onEpcs[key]['lastTime'], AllEpcs[key]['TimeStamp'])
            
        except Exception, ex:
            # print "Service getTagsList function error:\n"
            #print ex
            pass
        
        return self.output(CommandType, Var.IDF_CLIENT_CODE_SUCCESS, datas)

    def setting(self, CommandType, onToWorkTime, workToOffTime, workToOnTimes, offToOnTimes):
        """
             onToWorkTime :在架到临架消失时间(OnToNearTimes)
             workToOffTime:临架到离架消失时间(NearToOffTimes)
             workToOnTimes:临架到在架读卡次数(NearToOnTimes)
             offToOnTimes : 离架到在架读卡次数(OffToOnTimes)
        """
        Var.setConfig(online_min_times=workToOnTimes, workline_max_time=onToWorkTime, offline_max_time=workToOffTime)
        return self.output(CommandType, Var.IDF_CLIENT_CODE_SUCCESS)

    def output(self, CommandType='', code=Var.IDF_CLIENT_CODE_PRODUCT_EXCEPTION, data=''):
        ''' 输出产生函数 '''
        try:
            ret = {"CommandType": CommandType, "Code": code, "Data": data}
            return json.dumps(ret)
        except:
            return "{}"
