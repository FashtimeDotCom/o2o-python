#! /usr/bin/env python
# coding=utf-8
import socket
import threading
import json, time
import function


def output(CommandType=''):
    # ret = {"CommandType":CommandType, 'OnToNearTimes':2.6,'Key':'123456' ,'NearToOffTimes':1.5, 'NearToOnTimes':2.5, 'OffToOnTimes':2.5}
    ret = {"CommandType": CommandType, 'Key': '123456', 'GroupID': 8, 'State': 'ShelfOn'}
    return json.dumps(ret)


def client():
    print time.time()
    HOST = '172.16.13.163'
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
            function.log('client', 'client_0.log').error('data empty')
        else:
            function.log('client ', 'client_data_' + str(len(data)) + '.log').info('data len: ' + str(len(data)))

        print('[tcpServer said]: %s, %s ' % (recv, time.time()))
        time.sleep(1)

    sock.close()


if __name__ == '__main__':
    client()
