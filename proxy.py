#! /usr/bin/env python
# -*- coding: utf8 -*-

__author__ = 'Gtskk'
import urllib, json, os, socket, time

YOHOU = "http://api.open.yohobuy.com/?open_key=123554545&method=cnstore.product.view&v=1&sku="  # 有货商品信息接口
PATH = "D:\\youhuos\\yoho.txt"


def cache(url, ids):
    '''
    缓存数据
    '''
    list = {}
    for id in ids:
        url = url + str(id)
        data = urllib.urlopen(url).read()
        list[id] = data

    allDatas = json.dumps(list)
    f = file(PATH, "w")
    f.write(allDatas)
    f.close()


def loadData():
    f = file(PATH, "r")
    return json.load(f)
    f.close()


def output(CommandType=''):
    ret = {"CommandType": CommandType, 'Key': '123456', 'GroupID': 8, 'State': 'ShelfOn'}
    return json.dumps(ret)


def action():
    HOST = '172.16.13.229'
    PORT = 12345
    BUFFER = 4096
    recv = ''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    while True:
        sock.send(output('GetTagsList'))
        recv = sock.recv(BUFFER)
        val = json.loads(recv)
        data = val[u'Data']
        if len(data) == 0:
            allIds = [321218, 323898, 313840]
            print('data empty')
        else:
            for i in data:
                allIds.append(i['EPC'])
            print('data len: ' + str(len(data)))

        # 缓存数据
        if os.path.exists(PATH):
            cachedDatas = loadData()
            if (u'321218' in cachedDatas.keys()):
                print cachedDatas[u'321218']
        else:
            cache(YOHOU, allIds)

        print('[tcpServer said]: %s ' % recv)
        time.sleep(1)

    sock.close()


if __name__ == '__main__':
    action()