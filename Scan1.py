#! /usr/bin/env python
# coding=utf-8
"""
程序扫描服务
"""
import socket, os, multiprocessing, redis, json, time, threading, signal
from lib.RFIDReader import *
from DataBase import *
from Var import *
import function


class Scan(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.__readers = {}
        self.r = None

    def callbackLook(self, handle, context):  # 盘点回调查找
        card = cast(context, POINTER(INVENTORY_REPORT_RESULT))[0]
        cards = dict()
        if len(card.EPC):
            cards[card.EPC] = card
            self.save(cards, card.DeviceID)
            # self.FrequencySave(cards, card.DeviceID)
        # print "scan Time: \n"
        #print time.time()
        return 0

    def look(self, tags, DeviceID):  # 单次查找所有标签
        try:
            print "scan Time: \n"
            print time.time()
            cards = dict()
            if tags.nTagsCount > 0:
                for tag in tags.OneTagInfo:
                    if len(tag.cid) > 0:
                        card = INVENTORY_REPORT_RESULT()
                        card.EPC = tag.cid
                        card.AntennaID = str(tag.nAntenna)
                        card.TimeStamp = tag.TimeStamp
                        card.TID = tag.TID
                        card.Frequency = tag.Frequency
                        card.RSSI = tag.szRSSI
                        card.DeviceID = DeviceID
                        cards[tag.cid] = card

            self.save(cards, DeviceID)
        except Exception, ex:
            function.log("Scan look error", "error.log").error(ex)

    def lookRecycle(self, DevID):  # 快速查找标签
        blockparam = BlockInfo()
        blockparam.nEpcLength = 0
        blockparam.nBankType = 0
        blockparam.nLength = 1
        blockparam.nStartByte = 0
        blockparam.nTagType = 0
        data = ALLReadDataInfo()
        data.tagcount = c_short(0)
        cards = dict()
        newDevID = create_string_buffer(128)
        newDevID.value = DevID.value  # 多线程防止篡改
        ip = self.getIP(DevID.value)
        try:
            self.__readers[ip].ISO_6C_ReadCycle(newDevID, 0, blockparam, data, False, False)
            if data.tagcount > 0:
                for i in range(0, data.tagcount):
                    card = INVENTORY_REPORT_RESULT()
                    card.EPC = data.readdata[i].strEpc
                    card.AntennaID = str(data.readdata[i].AntennaID)
                    card.TimeStamp = str(time.time())
                    card.TID = ''
                    card.Frequency = ''
                    card.RSSI = ''
                    card.DeviceID = DevID.value
                    cards[card.EPC] = card
                    if DevID.value.startswith(ip) == False:
                        print DevID.value
                        print ip
            self.save(cards, DevID.value)
            return data.tagcount
        except Exception, ex:
            print "scan lookRecycle function error:\n"
            print ex
            return -1

    def save(self, cards, DeviceID):  # 把一组标签保存到内存数据中
        try:
            isExist = False
            epcs = self.r.get(DeviceID)
            if epcs == None:
                epcs = dict()
            else:
                epcs = json.loads(epcs)

            for key, card in cards.items():
                now = time.time()
                epc = {'EPC': card.EPC, 'TimeStamp': now, 'RSSI': card.RSSI, 'AntennaID': card.AntennaID, \
                       'Frequency': card.Frequency, 'TID': card.TID, 'Times': 1, 'FirstStamp': now, 'FrequencyTimes': 1,
                       'OldTimeStamp': now}
                if card.EPC in epcs.keys():
                    t = 0
                    if function.getDiffTime(epc['TimeStamp'], epcs[card.EPC]['OldTimeStamp']) > 5:
                        t = 1
                    else:
                        t = epc['Times'] + epcs[card.EPC]['Times']
                        epc['FirstStamp'] = epcs[card.EPC]['FirstStamp']  # 记录第一次时间
                        epc['OldTimeStamp'] = epcs[card.EPC]['TimeStamp']
                    epcs[card.EPC] = epc
                    epcs[card.EPC]['Times'] = t
                    epcs[card.EPC]['TimeStamp'] = now
                else:
                    epcs[card.EPC] = epc
                self.r.sadd(Var.REDIS_DEVICE_KEY, card.DeviceID)
                # print epcs
            self.r.set(DeviceID, json.dumps(epcs))

        except Exception, ex:
            print "scan save function error:\n"
            print ex
            # function.log("Scan save error","error.log").error(ex)

        return 1

    def FrequencySave(self, cards, DeviceID):  # 频率保存
        try:
            isExist = False
            epcs = self.r.get(DeviceID)
            if epcs == None:
                epcs = dict()
            else:
                epcs = json.loads(epcs)

            for key, card in cards.items():
                now = time.time()
                epc = {'EPC': card.EPC, 'TimeStamp': now, 'RSSI': card.RSSI, 'AntennaID': card.AntennaID, \
                       'Frequency': card.Frequency, 'TID': card.TID, 'Times': 0.2, 'FirstStamp': now,
                       'FrequencyTimes': 1, 'OldTimeStamp': now}
                if card.EPC in epcs.keys():
                    t = 0
                    if function.getDiffTime(epc['TimeStamp'], epcs[card.EPC]['OldTimeStamp']) > 5:
                        t = 1
                    else:
                        t = epcs[card.EPC]['FrequencyTimes'] + epc['FrequencyTimes']
                        epc['FirstStamp'] = epcs[card.EPC]['FirstStamp']  # 记录第一次时间
                        epc['OldTimeStamp'] = epcs[card.EPC]['TimeStamp']
                    if t > 10000:
                        t = 2.5 * 2
                        epcs[card.EPC]['FirstStamp'] = now
                    second = function.getDiffTime(epcs[card.EPC]['TimeStamp'], epcs[card.EPC]['FirstStamp'])
                    if second == 0:
                        second = 1
                    epcs[card.EPC]['FrequencyTimes'] = t
                    epcs[card.EPC]['Times'] = t / 125.0 * second / (2.5 / 125.0)  # 频率计算方式
                    epcs[card.EPC] = epc
                    epcs[card.EPC]['TimeStamp'] = now
                else:
                    epcs[card.EPC] = epc

                print card.DeviceID
                self.r.sadd(Var.REDIS_DEVICE_KEY, card.DeviceID)

            self.r.set(DeviceID, json.dumps(epcs))

        except Exception, ex:
            print ex
            # function.log("FrequencySave","error.log").error(ex)

    def __disconnectCallback(handle, context):
        print "connect fail"
        return 1


    def __errorCallback(handle, context):
        print "connect error"
        return 1


    def process(self):
        self.r.flushdb()
        dataBase = DataBase()
        threads = []
        ips = dataBase.getReaderIP()
        for ip in ips:
            self.__readers[ip] = RFIDReader()
            threads.append(threading.Thread(target=self.scan, args=(ip, )))

        for thread in threads:
            thread.start()

        while True:
            for i in range(0, len(threads)):
                if threads[i].isAlive() == False:
                    threads[i] = threading.Thread(target=self.scan, args=(ips[i], ))
                    threads[i].start()
            self.r.ping()
            time.sleep(1)

    def scan(self, ip):  # 扫描程序
        try:
            DevID = create_string_buffer(128)
            self.__readers[ip].Connect(ip, DevID, 7880, self.__disconnectCallback, self.__errorCallback)

            if len(DevID.value):
                self.__readers[ip].ISO_6C_StartPeriodInventory(DevID, self.callbackLook, True)

            if len(DevID.value):
                self.__readers[ip].Disconnect(DevID)
        except Exception, ex:
            print "scan scan function error:\n"
            print ex
            # function.log("Scan scan error","error.log").error(ex)

    def run(self):
        try:
            self.r = redis.StrictRedis(host=Var.REDIS_HOST, port=Var.REDIS_PORT, db=Var.REDIS_DB)
            self.process()
        except Exception, ex:
            print ex
            function.log("Scan run error", "error.log").error(ex)

    def initReader(self):  # 初始化设备
        dataBase = DataBase()
        reader = RFIDReader()
        for ip, reader in dataBase.getReaderConfig():
            DevID = create_string_buffer(128)
            reader.Connect(ip, DevID, 7880, self.__disconnectCallback, self.__errorCallback)
            # 初始化参数

            reader.Disconnect(DevID)

    def getIP(self, val):
        return val.split(':')[0]
        
