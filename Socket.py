#! /usr/bin/env python
# coding=utf-8
"""
socket服务
"""
import socket, os, multiprocessing, select, threading, time
from Var import *
from Service import *
import function


class Socket(multiprocessing.Process):
    '''
    Socket进程
    该模块主要用来和socket服务器进行通信，然后通过Service模块去处理返回的指令
    '''

    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        ''' Socket线程主要操作 '''
        try:
            # 创建一个socket对象
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 将socket绑定到指定地址
            sock.bind((Var.SOCKET_HOST, Var.SOCKET_PORT))
            #使用socket套接字的listen方法接收连接请求
            sock.listen(Var.SOCKET_DEFAULT_MAX_CLIENT)
            print 'tcpServer listen at:  (%s, %d)\n\r' % (Var.SOCKET_HOST, Var.SOCKET_PORT)
            while True:
                #异步等待socket对象准备好，其中第一个参数为等待读取的对象，第二个参数为等待写入的对象，第三个参数为等待异常的对象，
                #最后一个是可选对象，表示等待的时间，返回3个tuple，每个都是一个准备好的对象列表,和前面参数顺序一致    
                infds, outfds, errfds = select.select([sock, ], [], [], Var.SOCKET_DEFAULT_MAX_CLIENT)
                if len(infds) != 0:  # 如果infds状态改变,进行处理,否则不予理会
                    #服务器套接字通过socket的accept方法等待客户请求一个连接
                    client_sock, clientaddr = sock.accept()
                    infds_c, outfds_c, errfds_c = select.select([client_sock, ], [], [], 5)
                    if len(infds_c) != 0:
                        # 在新线程中从客户端接收数据
                        threading.Thread(target=self.threadProcess, args=(client_sock, clientaddr)).start()
            #关闭socket连接
            sock.close()
        except Exception, ex:
            function.log("Socket error", "error.log").error(ex)

    def threadProcess(self, client, clientaddr):
        recv = client.recv(int(Var.IDF_SOCKET_BUFFER))
        try:
            while len(recv):
                service = Service()
                # 处理发送过来的指令
                print recv
                ret = service.process(recv)
                # 向服务端发送数据
                client.send(ret + "\n")
                time.sleep(0.1)
                recv = client.recv(int(Var.IDF_SOCKET_BUFFER))
                #print recv
                #function.log('socket recv data', 'data/data-'+clientaddr[0]+'.log').info(recv)
                #function.log('socket send data', 'data/data-'+clientaddr[0]+'.log').info(ret)
            function.log('socket data', 'data/data-' + clientaddr[0] + '.log').info("socket close\n")
        except Exception, ex:
            print "Socket threadProcess function error:\n"
            print ex
        finally:
            print "close"
            client.close()