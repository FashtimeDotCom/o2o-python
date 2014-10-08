#! /usr/bin/env python
# coding=utf-8
import time, os, inspect, binascii
from threading import Thread
from ctypes import *
from ctypes.wintypes import DWORD, HWND, HANDLE, LPCWSTR, LPCSTR, WPARAM, LPARAM, UINT, RECT, POINT, MSG, POINTER


class GPIO(Structure):
    ''' GPIO类 '''
    _fields_ = [
        ("I", c_int),
        ("O", c_int),
    ]


class BlockInfo(Structure):
    ''' 用于读、写、块写、块擦、锁，杀操作接口类 '''
    _fields_ = [
        ("nEpcLength", c_int),
        ("nTagType", c_int),
        ("nBankType", c_int),
        ("nStartByte", c_int),
        ("nLength", c_int),
        ("szPWD", c_char * 8),
        ("szEPC", c_char * 1024),
        ("szResult", c_char * 1024),
    ]

    def __init__(self):
        pass


class ResultdData(Structure):
    ''' 结果信息类 '''
    _fields_ = [
        ("szMacErr", c_char * 8),
        ("szScatErr", c_char * 8),
        ("pszEPC", c_char * 1024),
    ]

    def __init__(self):
        pass


class LockPermissions(Structure):
    ''' 锁权限类 '''
    _fields_ = [
        ("killPasswordPermissions", c_int),  # 杀死密码
        ("accessPasswordPermissions", c_int),  # 标签访问密码
        ("epcMemoryBankPermissions", c_int),  # EPC区的许可
        ("tidMemoryBankPermissions", c_int),  # TID 区的许可
        ("userMemoryBankPermissions", c_int),  # 用户区许可
    ]

    def __init__(self):
        pass


class DEVICE_ANAINFO_STATUS_RESULT(Structure):
    ''' 设备天线状态类 '''
    _fields_ = [
        ("szAnaStatus", c_char * 8),  # 天线1的使能状态，使用为“1”， 不使用为“0”
        ("szTransmitPower", c_char * 8),  # 天线1发射功率,整数型字符串
        ("szDwellTime", c_char * 8),  # /天线2驻留时长  整数型字符串
        ("szNumInvCyc", c_char * 8),  # 天线3盘点周期 整数型字符串
        ("szAnaStatus2", c_char * 8),
        ("szTransmitPower2", c_char * 8),
        ("szDwellTime2", c_char * 8),
        ("szNumInvCyc2", c_char * 8),
        ("szAnaStatus3", c_char * 8),
        ("szTransmitPower3", c_char * 8),
        ("szDwellTime3", c_char * 8),
        ("szNumInvCyc3", c_char * 8),
        ("szAnaStatus4", c_char * 8),
        ("szTransmitPower4", c_char * 8),
        ("szDwellTime4", c_char * 8),
        ("szNumInvCyc4", c_char * 8)
    ]

    def __init__(self):
        pass


class DEVICE_GPI_STATUS_RESULT(Structure):
    ''' 设置GPI状态类 '''
    _fields_ = [
        ("szEleLevel1", c_char * 4),  # GPI1号口的状态 为 “0” 或者 “1”
        ("szEleLevel2", c_char * 4),  # GPI2号口的状态 为 “0” 或者 “1”
        ("szEleLevel3", c_char * 4),  #GPI3号口的状态 为 “0” 或者 “1”
        ("szEleLevel4", c_char * 4),  #GPI4号口的状态 为 “0” 或者 “1”
    ]

    def __init__(self):
        pass


class SET_ANTENNA_PARAMS(Structure):
    ''' 天线参数类 '''
    _fields_ = [
        ("bEnable", c_bool),  # 天线使能 true为可用， false为不可用
        ("nPower", c_int),  # 天线发射功率
        ("nDwellTime", c_int),  #天线驻留时间
        ("nInvCycle", c_int),  #盘点周期
    ]

    def __init__(self):
        pass


class SET_AllANTENNA_PARAM(Structure):
    ''' 用于天线设置的类 '''
    _fields_ = [
        ("Ant1", SET_ANTENNA_PARAMS),
        ("Ant2", SET_ANTENNA_PARAMS),
        ("Ant3", SET_ANTENNA_PARAMS),
        ("Ant4", SET_ANTENNA_PARAMS),
    ]

    def __init__(self):
        pass


class DEVICE_STATUS_RESULT(Structure):
    ''' 设备状态类 '''
    _fields_ = [
        ("szMacRegion", c_char * 8),  # 频率区域
        ("szAnaNum", c_char * 8),  # 天线数目
        ("szRadioOpen", c_char * 8),  #发射是否开启
        ("szPowerStatus", c_char * 8),  #功率状态
        ("szGPINum", c_char * 8),  #GPI数目
        ("szGPONum", c_char * 8),  #GPO数目
    ]

    def __init__(self):
        pass


class SET_GPO_PARAM(Structure):
    ''' 设置GPO参数类 '''
    _fields_ = [
        ("nLevel1", c_int),
        ("nLevel2", c_int),
        ("nLevel3", c_int),
        ("nLevel4", c_int),
    ]

    def __init__(self):
        pass


class SingleTagInfo(Structure):
    ''' 单个标签信息类 '''
    _fields_ = [
        ("cid", c_char * 1024),  # EPC号
        ("ncidLen", c_short),  # EPC的长度
        ("nCardType", c_short),  # 1为B协议，2为C协议
        ("nAntenna", c_short),  #天线
        ("TimeStamp", c_char * 24),  # 时间戳
        ("szRSSI", c_char * 32),
        ("DeviceID", c_char * 32),
        ("TID", c_char * 32),
        ("Frequency", c_char * 32),
    ]

    def __init__(self):
        pass


class AllTagInfo(Structure):
    ''' 所有标签信息类 '''
    _fields_ = [
        ("OneTagInfo", SingleTagInfo * 255),  # 一次最大识读255个标签
        ("nTagsCount", c_short)
    ]

    def __init__(self):
        pass


class CONNECT_SERVER_INFO(Structure):
    ''' 连接服务器信息 '''
    _fields_ = [
        ("DevType", c_char * 8),  # 设备类型
        ("SocketID", c_char * 32),  # 设备类型
        ("IP", c_char * 234),  #设备连接的IP与端口
    ]

    def __init__(self):
        pass


class INVENTORY_REPORT_RESULT(Structure):
    ''' 该类用于获取盘点结果的时候，传回的盘点数据 '''
    _fields_ = [
        ("DeviceID", c_char * 32),  # 设备号
        ("TimeStamp", c_char * 24),  # 盘点到该标签的机器时间
        ("AntennaID", c_char * 8),  #盘点到标签的天线
        ("EPC", c_char * 1024),  #EPC
        ("RSSI", c_char * 32),  #RSSI值,
        ("TID", c_char * 32),
        ("Frequency", c_char * 32),
    ]

    def __init__(self):
        pass


class READ_REPORT_RESULT(Structure):
    ''' 读取报告类 '''
    _fields_ = [
        ("DeviceID", c_char * 32),
        ("AntennaID", c_char * 8),
        ("strEpc", c_char * 1024),
        ("ReadData", c_char * 1024),
        ("ScatterErr", c_char * 8),
        ("MacErr", c_char * 8),
        ("Ciphertext", c_char * 1024),
        ("Signature", c_char * 1024),
        ("EncryptType", c_int),
    ]

    def __init__(self):
        pass


class FAST_READ_RESULT(Structure):
    ''' 快速读写类 '''
    _fields_ = [
        ("AntennaID", c_char * 8),
        ("DeviceID", c_char * 32),
        ("strEpc", c_char * 1024),
        ("ReadData", c_char * 1024),
    ]

    def __init__(self):
        pass


class ALLReadDataInfo(Structure):
    ''' 所有可读数据信息类 '''
    _fields_ = [
        ("readdata", FAST_READ_RESULT * 255),
        ("tagcount", c_short),
    ]

    def __init__(self):
        pass


class RFIDReader:
    ''' RFID读写器接口类 '''

    def __init__(self):
        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(this_file))
        try:
            self.__dll = CDLL(os.path.join(dirpath, "RFIDReaderNet.dll"))
        except Exception, ex:
            f = open('d:\\log.txt', 'a+')
            f.write(str(ex) + '\n')
            f.close()

        self.code = {
            0: 'SUCCESS ',  # 成功
            1: 'RUSULTERROR',  # 结果错误
            2: 'NIMPLEMENTED',  # 未实现
            3: 'UNHANDLEDEXCEPTION',  # 未处理的异常
            4: 'ALREADYCONNECTED',  # 已连接,
            5: 'UNHANDLEDEXCEPTION',  # 读写器没连接到网络,
            6: 'CONNECTIONSTATUSTIMEOUT',  # 连接超时
            7: 'CONNECTIONSTATUSMALFORMED',  # 连接状态错误
            8: 'READERCONNECTEDTOANOTHER',  # 读写器连接到其它的主机
            9: 'READERREFUSEDCONNECTION',  # 读写器拒绝连接
            10: 'AILEDPREPAREFEATURESET',  # 功能失败
            11: 'NOTCONNECTED',  # 无连接
            12: 'MISSINGFEATURESET',  # 少的功能集
            13: 'BADFEATURESE',  # 坏的功能
            14: 'MISSINGSTATUS',  # 缺失的状态
            15: 'INVALID STATUS REFRESHARGUMENT',  # 无效状态刷新参数
            16: 'INVALIDSETTINGS',  # 无效设置
            17: 'READERNOTSET',  # 读写器没有设置
            18: 'READERNOTIDLE',  # 读写器忙
            19: 'SENDMESSAGEFAILED',  # 发送消息失败
            20: 'RECEIVEDERRORMESSAGE',  # 收到错误消息
            21: 'TIMEOUT',  # 超时
            22: 'LOSTCONNECTION ',  # 连接掉线
            23: 'ENDOFINPUT ',  # 输入结束
            24: 'RESPONSESTATUSMALFORMED',  # 响应状态错误
            25: 'RESPONSESTATUSUNSUCCESSFUL',  # 响应状态失败
            26: 'THREADINGERROR ',  # 线程错误
            27: 'THREAD CONTEXT ERRO'  # 线程上下文错误
        }


    def StartListen(self):
        ''' 当读写器作为客户端时，SDK作为服务端运行，开始服务，等待读写器连接。'''
        func = self.__dll.StartListen
        func.argtypes = ()
        func.restype = UINT
        return func()

    def StopListen(self):
        ''' 停止服务 '''
        func = self.__dll.StopListen
        func.argtypes = ()
        func.restype = UINT
        return func()

    def SetCallBack(self, GetRegisterResulst, GetUnregisterResulst, ErrorCallback):
        ''' 当SDK作为服务端时，可设置该回调函数 '''
        Callback = CFUNCTYPE(UINT, HANDLE, c_void_p)
        prototype = CFUNCTYPE(UINT, Callback, Callback, Callback)
        params = (1, 'GetRegisterResulst'), (1, 'GetUnregisterResulst'), (1, 'ErrorCallback')
        func = prototype(('SetCallBack', self.__dll), params)
        return func(GetRegisterResulst=Callback(GetRegisterResulst),
                    GetUnregisterResulst=Callback(GetUnregisterResulst), ErrorCallback=Callback(ErrorCallback))

    def Connect(self, strIP, DevID, nPort, DisconnectCallback, ErrorCallback):
        ''' 读写器作为服务端，SDK作客户端，请求连接读写器 '''
        Callback = CFUNCTYPE(UINT, HANDLE, c_void_p)
        Callback2 = CFUNCTYPE(UINT, c_void_p)
        prototype = CFUNCTYPE(UINT, c_char_p, c_char_p, c_int, Callback, Callback2)
        params = (1, 'strIP'), (1, 'DevID'), (1, 'nPort'), (1, 'DisconnectCallback'), (1, 'Errorcallback')
        func = prototype(('Connect', self.__dll), params)
        callback = Callback(DisconnectCallback)
        callback2 = Callback2(ErrorCallback)
        return func(strIP=strIP, DevID=DevID, nPort=nPort, DisconnectCallback=callback, Errorcallback=callback2)

    def Disconnect(self, DevID):
        ''' 断开与读写器的连接 '''
        prototype = CFUNCTYPE(UINT, c_char_p)
        params = (1, 'DevID'),
        func = prototype(('Disconnect', self.__dll), params)
        return func(DevID=DevID)


    def GetAntenna(self, DevID, pParams):
        ''' 查询读写器的天线状态，当前正在使用的天线号，天线的盘点周期，驻留时长等信息'''
        func = self.__dll.GetAntenna
        func.argtypes = (c_char_p, POINTER(DEVICE_ANAINFO_STATUS_RESULT))
        func.restype = UINT
        return func(DevID, pParams)

    def SetAntenna(self, DevID, pParams):
        ''' 读写器天线设置，包括天线的便能，驻留时长，盘点周期，发射功率信息 '''
        func = self.__dll.SetAntenna
        func.argtypes = (c_char_p, POINTER(SET_AllANTENNA_PARAM))
        func.restype = UINT
        return func(DevID, pParams)

    def GetReaderInfo(self, DevID, pRepMsg):
        ''' 查询读写器信息， GPIO 口数目，天线数目，电源状态，频段,射频状态 '''
        func = self.__dll.GetReaderInfo
        func.argtypes = (c_char_p, POINTER(DEVICE_STATUS_RESULT))
        func.restype = UINT
        return func(DevID, pRepMsg)

    def SetGpO(self, DevID, pParms):
        ''' 设置GPO口的电平 '''
        func = self.__dll.SetGpO
        func.argtypes = (c_char_p, POINTER(SET_GPO_PARAM))
        func.restype = UINT
        return func(DevID, pParms)

    def GetGpIO(self, DevID, io, pRepMsg):
        ''' 查询GPIO口的信息 '''
        func = self.__dll.GetGpIO
        func.argtypes = (c_char_p, POINTER(GPIO), POINTER(DEVICE_GPI_STATUS_RESULT))
        func.restype = UINT
        return func(DevID, io, pRepMsg)

    def ISO_6C_StartPeriodInventory(self, DevID, callbackReport, bContinues=False):
        ''' 进行盘点，读写器把盘点到的EPC上报给用户层, 适用于只进行盘点操作过程 '''
        Callback = CFUNCTYPE(UINT, HANDLE, c_void_p)
        prototype = CFUNCTYPE(UINT, c_char_p, Callback, c_bool)
        params = (1, 'DevID'), (1, 'callbackReport'), (1, 'bContinues')
        func = prototype(('ISO_6C_StartPeriodInventory', self.__dll), params)
        callback = Callback(callbackReport)
        if bContinues:
            func(DevID=DevID, callbackReport=callback, bContinues=bContinues)
            time.sleep(7300)
            return 1
        else:
            return func(DevID=DevID, callbackReport=callback, bContinues=bContinues)


    def ISO_6C_GetPeriodInventoryResult(self, DevID, tags):
        ''' 配合周期性盘点使用，先调用开始周期性盘点后，再立即循环调用该函数获取盘点到的标签，停止周期性盘点后，也就停止调用该函数 '''
        prototype = CFUNCTYPE(UINT, c_char_p, POINTER(AllTagInfo))
        params = (1, 'DevID'), (1, 'tags')
        func = prototype(('ISO_6C_GetPeriodInventoryResult', self.__dll), params)
        return func(DevID=DevID, tags=byref(tags))

    def ISO_6C_StopPeriodInventory(self, DevID):
        ''' 停止周期盘点，读写器停止盘点工作，配ISO_6C_StartPeriodInventory使用 '''
        func = self.__dll.ISO_6C_StopPeriodInventory
        prototype = CFUNCTYPE(UINT, c_char_p)
        params = (1, 'DevID'),
        func = prototype(('ISO_6C_StopPeriodInventory', self.__dll), params)
        return func(DevID=DevID)

    def ISO_6C_Inventory(self, DevID, tags):
        ''' 单次盘点操作，该函数执行完毕，通过参数返回标签信息，适用于只进行一次盘点，不配合其它操作。'''
        func = self.__dll.ISO_6C_Inventory
        func.argtypes = (c_char_p, POINTER(AllTagInfo))
        func.restype = UINT
        return func(DevID, byref(tags))

    def ISO_6C_Inventory_Cycle(self, DevID, tags):
        ''' 循环盘点操作 '''
        prototype = CFUNCTYPE(UINT, c_char_p, POINTER(AllTagInfo))
        params = (1, 'DevID'), (1, 'tags')
        func = prototype(('ISO_6C_Inventory_Cycle', self.__dll), params)
        return func(DevID=DevID, tags=byref(tags))


    def ISO_6C_Read(self, DevID, antennaID, blockparam, pData, nCount, bEncrypt, bCheckSig):
        ''' 读取标签块区操作，可以读取EPC， User， Reserved， TID区  '''
        prototype = CFUNCTYPE(UINT, c_char_p, c_int, POINTER(BlockInfo), POINTER(READ_REPORT_RESULT), POINTER(c_int),
                              c_bool, c_bool)
        params = (1, 'DevID'), (1, 'antennaID'), (1, 'blockparam'), (1, 'pData'), (1, 'nCount'), (1, 'bEncrypt'), (
            1, 'bCheckSig')
        func = prototype(('ISO_6C_Read', self.__dll), params)
        return func(DevID=DevID, antennaID=antennaID, blockparam=blockparam, pData=pData, nCount=nCount,
                    bEncrypt=bEncrypt, bCheckSig=bCheckSig)


    def ISO_6C_Write(self, DevID, antennaID, blockparam, pData, nCount, bEncrypt, bCheckSig):
        ''' 标签写操作，可以改写EPC， User， Reserved区 '''
        func = self.__dll.ISO_6C_Write
        func.argtypes = (c_char_p, c_byte, POINTER(BlockInfo), POINTER(ResultdData), POINTER(c_int), c_bool, c_bool)
        func.restype = UINT
        return func(DevID, antennaID, blockparam, pData, nCount, bEncrypt, bCheckSig)

    def ISO_6C_BlockWrite(self, DevID, pBlockparam, pData, nCount, nAntennaID):
        ''' 标签块写操作，可以改写EPC， User， Reserved区 '''
        func = self.__dll.ISO_6C_BlockWrite
        func.argtypes = (c_char_p, POINTER(BlockInfo), POINTER(ResultdData), POINTER(c_int), c_int)
        func.restype = UINT
        return func(DevID, pBlockparam, pData, nCount, nAntennaID)

    def ISO_6C_BlockErase(self, DevID, nAntennaID, pBlockparam, pData, nCount):
        ''' 
        标签块擦除操作，可以清理EPC， User， Reserved区 
        该函数的参数：DveID:c_char nAntenna:BlockInfo, pBlockparam:ResultdData, pData:LP_c_long
        '''
        func = self.__dll.ISO_6C_BlockErase
        func.argtypes = (c_char_p, POINTER(BlockInfo), POINTER(ResultdData), POINTER(c_int))
        func.restype = UINT
        return func(DevID, nAntennaID, pBlockparam, pData, nCount)

    def ISO_6C_Kill(self, DevID, unAccessword, unKillword, nAntennaID, strEPC, nEpcLength, pData, nCount):
        ''' 杀死标签操作 '''
        func = self.__dll.ISO_6C_Kill
        func.argtypes = (c_char_p, c_uint, c_uint, c_byte, c_char_p, c_byte, POINTER(ResultdData), POINTER(c_int))
        func.restype = UINT
        return func(DevID, unAccessword, unKillword, nAntennaID, strEPC, nEpcLength, pData, nCount)

    def ISO_6C_Lock(self, DevID, permission, nAntennaID, strEPC, nEpcLength, pData):
        ''' 锁定标签操作 '''
        func = self.__dll.ISO_6C_Lock
        func.argtypes = (c_char_p, POINTER(LockPermissions), c_int, c_char_p, c_int, POINTER(ResultdData))
        func.restype = UINT
        return func(DevID, permission, nAntennaID, strEPC, nEpcLength, pData)

    def ISO_6C_ReadCycle(self, pszDevID, nAntennaID, pBlockparam, ardi, bEncrypt, bCheckSig):
        ''' 进行快速的读取操作， 并且多次循环进行读操作的情形 '''
        prototype = CFUNCTYPE(UINT, c_char_p, c_int, POINTER(BlockInfo), POINTER(ALLReadDataInfo), c_bool, c_bool)
        params = (1, 'pszDevID'), (1, 'nAntennaID'), (1, 'pBlockparam'), (1, 'ardi'), (1, 'bEncrypt'), (1, 'bCheckSig')
        func = prototype(('ISO_6C_ReadCycle', self.__dll), params)
        return func(pszDevID=pszDevID, nAntennaID=nAntennaID, pBlockparam=pBlockparam, ardi=ardi, bEncrypt=bEncrypt,
                    bCheckSig=bCheckSig)

    def ISO_6C_WriteCycle(self, pszDevID, nAntennaID, pBlockparam, bEncrypt, bCheckSig):
        ''' 进行快速的写操作，并且多次循环进行写操作的情形 '''
        func = self.__dll.ISO_6C_WriteCycle
        func.argtypes = (c_char_p, c_int, POINTER(BlockInfo), c_bool, c_bool)
        func.restype = UINT
        return func(pszDevID, nAntennaID, pBlockparam, bEncrypt, bCheckSig)
            
