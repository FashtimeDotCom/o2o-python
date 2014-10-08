#! /usr/bin/env python
# coding=utf-8
"""
系统变量
"""
import ConfigParser, os, inspect


class Var:
    def __init__(self):
        self.getDefine()
        self.loadConfig()

    def getDefine(self):
        # 常量定义
        self.IDF_CLIENT_CODE_SUCCESS = 100  # 连接正常
        self.IDF_CLIENT_CODE_ANTENNA_EXCEPTION = 101  # 天线异常
        self.IDF_CLIENT_CODE_KEY_EXCEPTION = 102  # 密钥异常
        self.IDF_CLIENT_CODE_PRODUCT_EXCEPTION = 103  # 产品异常
        self.IDF_CLIENT_CODE_NETWORK_EXCEPTION = 104  # 网络异常
        self.IDF_CLIENT_CODE_NETWORK_TIMEOUT_EXCEPTION = 105  # 网络超时异常
        self.IDF_CLIENT_COMMAND_GETTAGSLIST = 'GetTagsList'
        self.IDF_CLIENT_COMMAND_SETTING = 'Setting'
        self.IDF_SOCKET_BUFFER = 4096
        self.REDIS_GROUP_KEY = 'GroupIDs'
        self.REDIS_DEVICE_KEY = 'DeviceIDs'
        self.REDIS_IP_STATE_KEY = 'IPSTATE'
        self.COMMANDTYPE_STATE_ON_PARAM = 'ShelfOn'  # 请求参数State:  在架
        self.COMMANDTYPE_STATE_WORK_PARAM = 'ShelfNear'  # 请求参数State:  临架
        self.COMMANDTYPE_STATE_OFF_PARAM = 'ShelfOut'  # 请求参数State:  离架
        self.COMMANDTYPE_STATE_ON_WORK_PARAM = 'ShelfOnAndNear'  # 请求参数State 在架临架

    def loadConfig(self):
        """
              读取IDF_client配置
        """
        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(this_file))
        config = ConfigParser.ConfigParser()
        config.readfp(open(os.path.join(dirpath, "config.ini")))
        self.REDIS_HOST = config.get("redis", "host")  # redis连接主机
        self.REDIS_PORT = int(config.get("redis", "port"))  # redis连接端口号
        self.REDIS_DB = int(config.get("redis", "db"))  # redis连接数据库
        self.SOCKET_HOST = config.get("socket", "host")  # socket连接主机
        self.SOCKET_PORT = int(config.get("socket", "port"))  # socket连接端口号
        self.SOCKET_KEY = config.get("socket", "key")  # socket连接key
        self.SOCKET_DEFAULT_MAX_CLIENT = int(config.get("socket", "default_max_client"))  # 连接最大数
        self.TAG_ONLINE_MAX_TIME = float(config.get("tag", "online_max_time"))  # 在架时间
        self.TAG_ONLINE_MIN_TIMES = int(config.get("tag", "online_min_times"))  # 在架次数
        self.TAG_WORKLINE_TIMES = int(config.get("tag", "workline_times"))  # 临架次数
        self.TAG_WORKLINE_STOP_TIME = float(config.get("tag", "workline_stop_time"))  # 临架停留时间
        self.TAG_WORKLINE_MAX_TIME = float(config.get("tag", "workline_max_time"))  # 临架最大时间
        self.TAG_WORKLINE_MIN_TIME = float(config.get("tag", "workline_min_time"))  # 临架最小时间
        self.TAG_OFFLINE_MAX_TIME = float(config.get("tag", "offline_max_time"))  # 离架时间

    def setConfig(self, **params):

        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(this_file))
        config = ConfigParser.ConfigParser()
        config.readfp(open(os.path.join(dirpath, "config.ini")))

        if 'online_min_times' in params.keys():
            self.TAG_ONLINE_MIN_TIMES = int(params['online_min_times'])

        if 'online_max_time' in params.keys():
            self.TAG_ONLINE_MAX_TIME = float(params['online_max_time'])

        if 'workline_max_time' in params.keys():
            self.TAG_WORKLINE_MAX_TIME = float(params['workline_max_time'])

        if 'workline_min_time' in params.keys():
            self.WORKLINE_MIN_TIME = float(params['workline_min_time'])

        if 'offline_max_time' in params.keys():
            self.TAG_OFFLINE_MAX_TIME = float(params['offline_max_time'])
        config.set('tag', 'online_min_times', self.TAG_ONLINE_MIN_TIMES)
        config.set('tag', 'online_max_time', self.TAG_ONLINE_MAX_TIME)
        config.set('tag', 'workline_max_time', self.TAG_WORKLINE_MAX_TIME)
        config.set('tag', 'workline_min_time', self.TAG_WORKLINE_MIN_TIME)
        config.set('tag', 'offline_max_time', self.TAG_OFFLINE_MAX_TIME)
        config.write(open(os.path.join(dirpath, "config.ini"), 'w'))


Var = Var()
