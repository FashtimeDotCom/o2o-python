#! /usr/bin/env python
# -*- coding=utf-8 -*-
"""
客户端服务
"""
import redis, time, urllib2, os, sched, re
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
        YOHOU = "http://api.open.yohobuy.com/?open_key=123554545&method=cnstore.product.view&v=1&sku="  # 有货商品信息接口
        PATH = "D:\\youhuos\\"

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

        allIds = []
        if len(datas) == 0:
            allIds = [321282, 321298, 323840]
            print('data empty')
        else:
            for i in datas:
                allIds.append(re.compile(r'^0+').sub('', i['EPC']))
            print allIds

        # 缓存数据
        if os.path.exists(PATH):
            cachedDatas = self.__loadData(PATH)
            if set(allIds).issubset(set(cachedDatas.keys())):
                pass
        else:
            self.__cache(YOHOU, PATH, allIds)

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

    def __cache(self, url, path, ids):
        '''
        缓存数据
        '''
        list = {}
        if not os.path.exists(path):
            os.mkdir(path)
        for id in ids:
            newUrl = url + str(id)
            data = urllib2.urlopen(newUrl).read()
            data = json.loads(data)

            # 缓存数据中的图片
            if data['code'] == 200:
                # 缓存产品图片
                data = self.cacheImgs(path, data, id, u'goods_img')
                # threading.Thread(target=self.cacheImgs, args=(data, id, u'goods_Img')).start()
                # 缓存商品颜色图片
                data = self.cacheImgs(path, data, id, u'goods')
                # threading.Thread(target=self.cacheImgs, args=(data, id, u'goods')).start()
                # 缓存商标logo
                data = self.cacheImgs(path, data, id, u'brand_ico')
                # threading.Thread(target=self.cacheImgs, args=(data, id, u'brand_ico')).start()
                # 缓存默认商品图片
                data = self.cacheImgs(path, data, id, u'goodsDefault')
                # threading.Thread(target=self.cacheImgs, args=(data, id, u'goodsDefault')).start()
                # 缓存促销banner图片
                data = self.cacheImgs(path, data, id, u'promotion_banner')
                # threading.Thread(target=self.cacheImgs, args=(data, id,  u'promotion_banner')).start()
                # 缓存同等商品图片
                data = self.cacheImgs(path, data, id, u'sameGoods')
                # threading.Thread(target=self.cacheImgs, args=(data, id, u'sameGoods')).start()

            list[id] = json.dumps(data)

        allDatas = json.dumps(list)
        dataPath = path + '\\yoho.txt'
        f = file(dataPath, "w")
        f.write(allDatas)
        f.close()

        # 安排每5分钟运行一次自己
        self.schedule.enter(300, 0, self.__cache, (url, path, ids))

    def __loadData(self, path):
        dataPath = path + '\\yoho.txt'
        f = file(dataPath, "r")
        return json.load(f)
        f.close()

    def cacheImgs(self, path, jsonData, id, item):
        '''
        缓存图片
        :param jsonData:
        :param id:
        :param item:
        :return:
        '''
        if jsonData['data'].has_key(item):
            if isinstance(jsonData[u'data'][item], list):
                l = []
                path = path + '\\goodsImgs\\'
                if not os.path.exists(path):
                    os.mkdir(path)
                for i in jsonData[u'data'][item]:
                    imgPath = path + str(id)
                    imgName = str(jsonData[u'data'][item].index(i)) + '.' + i.split('.')[-1]
                    if not os.path.exists(imgPath):
                        os.mkdir(imgPath)
                    l.append(os.path.join(imgPath, imgName))
                    self.saveImg(imgPath, imgName, i)
                jsonData[u'data'][item] = l
            elif isinstance(jsonData[u'data'][item], dict):
                d = {}
                colorPath = path + '\\goodsColors\\'
                if not os.path.exists(colorPath):
                    os.mkdir(colorPath)
                sameProPath = path + '\\sameProImgs\\'
                if not os.path.exists(sameProPath):
                    os.mkdir(sameProPath)
                for k, v in jsonData[u'data'][item].items():
                    if v.has_key(u'color_image') and v[u'color_image']:
                        imgUrl = v[u'color_image']
                        imgName = str(k) + '.' + imgUrl.split('.')[-1]
                        imgPath = colorPath + str(id)
                        if not os.path.exists(imgPath):
                            os.mkdir(imgPath)
                        v[u'color_image'] = os.path.join(imgPath, imgName)
                    elif v.has_key(u'sameProductImg') and v[u'sameProductImg']:
                        imgUrl = v[u'sameProductImg']
                        imgName = str(k) + '.' + imgUrl.split('.')[-1]
                        imgPath = sameProPath + str(id)
                        if not os.path.exists(imgPath):
                            os.mkdir(imgPath)
                        v[u'sameProductImg'] = os.path.join(imgPath, imgName)
                    else:
                        continue
                    self.saveImg(imgPath, imgName, imgUrl)

            else:
                imgUrl = jsonData[u'data'][item]
                if not imgUrl:
                    return jsonData
                imgPath = path + item + 's'
                imgName = str(id) + '.' + imgUrl.split('.')[-1]
                if not os.path.exists(imgPath):
                    os.mkdir(imgPath)
                jsonData[u'data'][item] = os.path.join(imgPath, imgName)
                self.saveImg(imgPath, imgName, imgUrl)

        return jsonData

    def saveImg(self, path, name, url):
        imgDat = urllib2.urlopen(url).read()
        with open(os.path.join(path, name), "wb") as img:
            img.write(imgDat)