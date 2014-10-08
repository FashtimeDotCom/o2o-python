#! /usr/bin/env python
# coding=utf-8
"""
监控服务
"""
import socket, os, multiprocessing, redis, json, time, threading, signal
from DataBase import *
from Var import *
import function


class Monitor(multiprocessing.Process):
    ''' 主要通过ping读写器地址来检查读写器的状态，然后存入redis中 '''

    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        '''
        进程主入口方法，连接redis数据库，开启子线程读取读写器的信息
        '''
        self.r = redis.StrictRedis(host=Var.REDIS_HOST, port=Var.REDIS_PORT, db=Var.REDIS_DB)
        dataBase = DataBase()
        ips = dataBase.getReaderIP()
        threads = []

        try:
            for ip in ips:
                # 为每个读写器的验证开一个线程
                threads.append(threading.Thread(target=self.ping, args=(ip, )))

            for thread in threads:
                thread.start()

            while True:

                for i in range(0, len(threads)):
                    if threads[i].isAlive() == False:
                        threads[i] = threading.Thread(target=self.ping, args=(ips[i], ))
                        threads[i].start()

                self.r.ping()
                # self.clearRedis(dataBase)

        except Exception, ex:
            print "Monitor run error function"
            print ex

    def ping(self, ip):
        ''' ping读写器 '''
        states = self.r.get(Var.REDIS_IP_STATE_KEY)

        if states != None and len(states):
            states = json.loads(states)
        else:
            states = {}

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        try:
            sock.connect((ip, 80))
            state = 1
        except Exception, Ex:
            state = 0
        sock.close()

        if ip in states.keys():
            if state == 0:
                if states[ip]['FailTimeStamp'] == 0:
                    states[ip]['TimeLong'] = 1
                else:
                    states[ip]['TimeLong'] = time.time() - states[ip]['FailTimeStamp']  # 断开时间总长

                states[ip]['FailTimeStamp'] = time.time()

            states[ip]['state'] = state
        else:
            states[ip] = {'state': state, 'TimeLong': 0, 'FailTimeStamp': 0}

        self.r.set(Var.REDIS_IP_STATE_KEY, json.dumps(states))
        time.sleep(10)

    def clearRedis(self, dataBase):
        ''' 清除内存数据 '''
        states = self.r.get(Var.REDIS_IP_STATE_KEY)
        try:

            if states != None and len(states):
                states = json.loads(states)

            if isinstance(states, dict) == False:
                return None

            for ip, state in states.items():
                if state['state']:
                    continue
                print ip
                print state
                if state['TimeLong'] >= 3600:
                    i = 0
                else:
                    i = 5
                while i < 10:
                    for groupID, groupInfos in dataBase.groupsInfo.items():
                        for ant in groupInfos:
                            if ip == ant['readerIP']:
                                self.r.set(ip + ':7880', '{}')
                                self.r.hset(groupID, 'on', '{}')
                                self.r.hset(groupID, 'work', '{}')
                                self.r.hset(groupID, 'off', '{}')
                    i = i + 1
                    time.sleep(0.1)
        except Exception, ex:
            print ex
            
        
        
        
