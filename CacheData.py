#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, sched, time, re, urllib2, json, random
from Var import *
from DataBase import  *

class CacheData:
    '''
    缓存数据类
    '''

    def __init__(self):
        self.cachedDatas = self.__loadData(os.path.join(Var.CACHE_PATH, 'yoho.txt'))
        # 第一个参数确定任务的时间，返回从某个特定的时间到现在经历的秒数
        # 第二个参数以某种人为的方式衡量时间
        self.schedule = sched.scheduler(time.time, time.sleep)

    def getData(self, neededId):
        '''
        获取指定ID的数据
        :param neededIds:
        :return:
        '''
        for z in self.cachedDatas:
            if z['EPC'] == neededId:
                return z
        return None

    def realCache(self, neededIds):
        '''
        缓存数据
        :return:
        '''
        if self.cachedDatas:
            cachedIds = [x['EPC'] for x in self.cachedDatas]
            newIds = [y for y in neededIds if y not in cachedIds]
            # 查到有新信息需要缓存
            if newIds:
                datas = self.__cache(Var.YOHO_URL, Var.CACHE_PATH, newIds)
                allData = self.cachedDatas + datas
                self.__saveTxtData(allData, Var.CACHE_PATH)
        else:
            if neededIds:
                initialData = self.__cache(Var.YOHO_URL, Var.CACHE_PATH, neededIds)
                # 保存数据文件
                self.__saveTxtData(initialData, Var.CACHE_PATH)

    def __cache(self, url, path, ids):
        '''
        缓存数据
        '''
        list = []
        tagCasts = DataBase().tagCasts
        if not os.path.exists(path):
            os.mkdir(path)
        for iid in ids:

            # 标签EPC映射
            castedId = tagCasts.has_key(iid) and tagCasts[iid] or iid

            id = re.compile(r'^0+').sub('', castedId)
            newUrl = url + str(id)
            data = urllib2.urlopen(newUrl).read()
            data = json.loads(data)

            data['EPC'] = iid
            qrCodes = DataBase().qrCodes
            data['qrCode'] = qrCodes.has_key(iid) and  qrCodes[iid] or None

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

            list.append(data)

        # 安排每5分钟运行一次自己
        self.schedule.enter(300, 0, self.__cache, (url, path, ids))

        return list

    def __saveTxtData(self, dat, path):
        self.cachedDatas = dat
        allDatas = json.dumps(dat)
        dataPath = os.path.join(path, 'yoho.txt')
        f = file(dataPath, "wb")
        f.write(allDatas)
        f.close()

    def __loadData(self, path):
        if os.path.exists(path):
            f = file(path, "rb")
            d = json.load(f)
            f.close()
            return d
        return None

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
                path = os.path.join(path, 'goodsImgs')
                if not os.path.exists(path):
                    os.mkdir(path)
                for i in jsonData[u'data'][item]:
                    imgPath = os.path.join(path, str(id))
                    extAll = i.split('.')[-1]
                    ext = extAll.split('-')[0]
                    ur = i[0:i.rfind('.')] + '.' + ext + '?' + str(random.randint(1, 99))
                    
                    imgName = str(jsonData[u'data'][item].index(i)) + '.' + ext
                    if not os.path.exists(imgPath):
                        os.mkdir(imgPath)
                    l.append(os.path.join(imgPath, imgName))
                    self.saveImg(imgPath, imgName, ur)
                jsonData[u'data'][item] = l
            elif isinstance(jsonData[u'data'][item], dict):
                d = {}
                colorPath = os.path.join(path, 'goodsColors')
                if not os.path.exists(colorPath):
                    os.mkdir(colorPath)
                sameProPath = os.path.join(path, 'sameProImgs')
                if not os.path.exists(sameProPath):
                    os.mkdir(sameProPath)
                for k, v in jsonData[u'data'][item].items():
                    if v.has_key(u'color_image') and v[u'color_image']:
                        imgUrl = v[u'color_image']
                        imgName = str(k) + '.' + imgUrl.split('.')[-1]
                        imgPath = os.path.join(colorPath, str(id))
                        if not os.path.exists(imgPath):
                            os.mkdir(imgPath)
                        v[u'color_image'] = os.path.join(imgPath, imgName)
                    elif v.has_key(u'sameProductImg') and v[u'sameProductImg']:
                        imgUrl = v[u'sameProductImg']
                        imgName = str(k) + '.' + imgUrl.split('.')[-1]
                        imgPath = os.path.join(sameProPath, str(id))
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
                imgPath = os.path.join(path, item + 's')
                imgName = str(id) + '.' + imgUrl.split('.')[-1]
                if not os.path.exists(imgPath):
                    os.mkdir(imgPath)
                jsonData[u'data'][item] = os.path.join(imgPath, imgName)
                self.saveImg(imgPath, imgName, imgUrl)

        return jsonData

    def saveImg(self, path, name, url):
        img = urllib.urlopen(url)
        if(img.getcode() == 200):
            imgDat = img.read()
            with open(os.path.join(path, name), "wb") as img:
                img.write(imgDat)
