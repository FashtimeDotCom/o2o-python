#! /usr/bin/env python
# coding=utf-8
"""
数据库服务
"""
from Var import *


class DataBase:
    def __init__(self):
        # 组数据
        # offline_max_time:   离架最大时间 [默认配置，在config.ini]
        # online_max_time:    在架最大时间
        # online_min_times:   在架最小次数
        # workline_min_time:  临架最小时间
        # workline_stop_time: 临架停留时间
        # workline_times:     临架停留时间
        # workline_max_time:  临架最大时间
        # workline_max_time:  临架次数,不用
        self.groups = [
            {'id': '0', 'name': 'group0', 'desp': '', 'groupID': '0', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 0, 'workline_min_time': 1.5, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},

            {'id': '1', 'name': 'group1', 'desp': '', 'groupID': '1', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 8, 'workline_min_time': 0.89, 'workline_stop_time': 1,
             'workline_times': 0, \
             'workline_max_time': 0},

            {'id': '2', 'name': 'group2', 'desp': '', 'groupID': '2', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 10, 'workline_min_time': 0, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},

            {'id': '3', 'name': 'group3', 'desp': '', 'groupID': '3', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 10, 'workline_min_time': 0, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},

            {'id': '4', 'name': 'group4', 'desp': '', 'groupID': '4', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 10, 'workline_min_time': 0, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},

            {'id': '5', 'name': 'group5', 'desp': '', 'groupID': '5', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 10, 'workline_min_time': 2, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},
            {'id': '6', 'name': 'group6', 'desp': '', 'groupID': '6', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 10, 'workline_min_time': 2, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},
            {'id': '7', 'name': 'group7', 'desp': '', 'groupID': '7', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 10, 'workline_min_time': 0, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},
            {'id': '8', 'name': 'group8', 'desp': '', 'groupID': '8', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 5, 'workline_min_time': 0, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},
            {'id': '9', 'name': 'group9', 'desp': '', 'groupID': '9', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 10, 'workline_min_time': 0, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},
            {'id': '10', 'name': 'group10', 'desp': '', 'groupID': '10', 'offline_max_time': 0, \
             'online_max_time': 0, 'online_min_times': 0, 'workline_min_time': 0, 'workline_stop_time': 0,
             'workline_times': 0, \
             'workline_max_time': 0},
        ]

        # 读写器数据
        #readerIP:读写器IP地址
        self.readers = [
            {'id': '1', 'readerID': '1', 'readerIP': '172.16.13.225', 'desp': '', 'nLevel1': 0, 'nLevel2': 0,
             'nLevel3': 0, 'nLevel4': 0},
            #  {'id':'2','readerID':'2', 'readerIP':'172.16.13.223','desp':'','nLevel1':0,'nLevel2':0, 'nLevel3':0, 'nLevel4':0},
            #{'id':'3','readerID':'3', 'readerIP':'172.16.13.224','desp':'','nLevel1':0,'nLevel2':0, 'nLevel3':0, 'nLevel4':0},
            # {'id':'4','readerID':'4', 'readerIP':'172.16.13.225','desp':'','nLevel1':0,'nLevel2':0, 'nLevel3':0, 'nLevel4':0},
            #{'id':'5','readerID':'5', 'readerIP':'172.16.13.226','desp':'','nLevel1':0,'nLevel2':0, 'nLevel3':0, 'nLevel4':0},
            # {'id':'6','readerID':'6', 'readerIP':'172.16.13.227','desp':'','nLevel1':0,'nLevel2':0, 'nLevel3':0, 'nLevel4':0},

        ]

        #读写器天线数据
        # groupID:组ID
        # readerID: 读写器ID
        # antID:天线ID (0-3)
        self.ants = [
            #readerID 3
            {'id': '1', 'antID': '2', 'readerID': '4', 'groupID': '1', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '2', 'antID': '3', 'readerID': '4', 'groupID': '1', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},

            {'id': '3', 'antID': '1', 'readerID': '4', 'groupID': '1', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '4', 'antID': '0', 'readerID': '4', 'groupID': '1', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},

            {'id': '5', 'antID': '2', 'readerID': '6', 'groupID': '3', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '6', 'antID': '3', 'readerID': '6', 'groupID': '3', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},

            {'id': '7', 'antID': '0', 'readerID': '6', 'groupID': '3', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '8', 'antID': '1', 'readerID': '6', 'groupID': '3', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},

            {'id': '9', 'antID': '0', 'readerID': '2', 'groupID': '5', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '10', 'antID': '1', 'readerID': '2', 'groupID': '5', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '11', 'antID': '2', 'readerID': '2', 'groupID': '5', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '12', 'antID': '3', 'readerID': '2', 'groupID': '5', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '13', 'antID': '0', 'readerID': '5', 'groupID': '5', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '14', 'antID': '0', 'readerID': '1', 'groupID': '8', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '15', 'antID': '1', 'readerID': '1', 'groupID': '8', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '16', 'antID': '2', 'readerID': '1', 'groupID': '8', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            {'id': '17', 'antID': '3', 'readerID': '1', 'groupID': '8', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},
            #{'id':'18', 'antID':'2', 'readerID':'5','groupID':'8','desp':'','nPower':0,'bEnable':True, 'nDwellTime':0, 'nInvCycle':0},

            #{'id':'19','antID':'2', 'readerID':'4','groupID':'7','desp':'','nPower':0,'bEnable':True, 'nDwellTime':0, 'nInvCycle':0},
            #{'id':'20','antID':'3', 'readerID':'4','groupID':'7','desp':'','nPower':0,'bEnable':True, 'nDwellTime':0, 'nInvCycle':0},

            #{'id':'21','antID':'0', 'readerID':'4','groupID':'7','desp':'','nPower':0,'bEnable':True, 'nDwellTime':0, 'nInvCycle':0},
            #{'id':'22','antID':'1', 'readerID':'4','groupID':'7','desp':'','nPower':0,'bEnable':True, 'nDwellTime':0, 'nInvCycle':0},

            {'id': '23', 'antID': '3', 'readerID': '5', 'groupID': '9', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},

            {'id': '24', 'antID': '0', 'readerID': '7', 'groupID': '10', 'desp': '', 'nPower': 0, 'bEnable': True,
             'nDwellTime': 0, 'nInvCycle': 0},

        ]

        self.groupsInfo = dict()
        self.getGroupsInfo()

    def getGroupsInfo(self):
        ''' 获取组信息 '''
        i = 0
        for group in self.groups:
            groupID = group['groupID']
            self.groupsInfo[groupID] = []
            for ant in self.ants:
                if group['groupID'] == ant['groupID']:
                    for reader in self.readers:
                        if reader['readerID'] == ant['readerID']:
                            info = {'antID': ant['antID'], 'readerIP': reader['readerIP']}
                            self.groupsInfo[groupID].append(info)

            if group['offline_max_time'] == 0:
                group['offline_max_time'] = Var.TAG_OFFLINE_MAX_TIME

            if group['online_max_time'] == 0:
                group['online_max_time'] = Var.TAG_ONLINE_MAX_TIME

            if group['online_min_times'] == 0:
                group['online_min_times'] = Var.TAG_ONLINE_MIN_TIMES

            if group['workline_min_time'] == 0:
                group['workline_min_time'] = Var.TAG_WORKLINE_MIN_TIME

            if group['workline_max_time'] == 0:
                group['workline_max_time'] = Var.TAG_WORKLINE_MAX_TIME

            if group['workline_times'] == 0:
                group['workline_times'] = Var.TAG_WORKLINE_TIMES

            if group['workline_stop_time'] == 0:
                group['workline_stop_time'] = Var.TAG_WORKLINE_STOP_TIME

            self.groups[i] = group
            i = i + 1


    def getGroupsConfig(self, id):
        ''' 获取组配置 '''
        if id != None:
            for group in self.groups:
                if int(group['groupID']) == int(id):
                    return group
        return None

    def getReaderIP(self):
        ''' 获取读写器ip地址 '''
        readerIPs = []
        for reader in self.readers:
            if len(reader['readerIP']):
                readerIPs.append(reader['readerIP'])

        return readerIPs

    def getReaderConfig(self):
        ''' 获取读写器配置 '''
        readers = {}
        for reader in self.readers:
            readers[reader['readerIP']] = {'nLevel1': reader['nLevel1'], 'nLevel2': reader['nLevel2'], \
                                           'nLevel3': reader['nLevel3'], 'nLevel4': reader['nLevel4'], 'ants': []}
            for ant in self.ants:
                if ant['readerID'] == reader['readerID']:
                    readers[reader['readerIP']]['ants'].append({'ant': ant['antID'], 'nPower': ant['nPower'], \
                                                                'bEnable': ant['bEnable'],
                                                                'nDwellTime': ant['nDwellTime'],
                                                                'nInvCycle': ant['nInvCycle']})

        return readers
    
