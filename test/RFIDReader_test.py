#!/usr/bin/env python
# coding: utf-8

import unittest, sys

sys.path.append('..')
from lib.RFIDReader import *


class TestRFIDReader(unittest.TestCase):
    ''' RFIDReader接口测试类 '''

    def setUp(self):
        self.reader = RFIDReader()

    def test_connect(self):
        ''' 测试连接接口 '''

        def __disconnectCallback(handle, context):
            print "connect fail"
            return 1

        def __errorCallback(handle, context):
            print "connect error"

        return 1

        DevID = create_string_buffer(128)
        self.assertEquals(self.reader.Connect('172.16.13.130', DevID, 7880, __disconnectCallback, __errorCallback), 0)

    def test_startlisten(self):
        ''' 测试开始监听接口 '''
        self.assertEquals(self.reader.StartListen(), 0)

    def test_stoplisten(self):
        ''' 测试停止监听接口 '''
        self.assertEquals(self.reader.StopListen(), 0)

    def test_disconnect(self):
        ''' 测试断开连接接口 '''
        DevID = create_string_buffer(128)
        self.assertEquals(self.reader.Disconnect(DevID), 0)

    def test_getantenna(self):
        ''' 测试获取天线信息接口 '''
        DevID = create_string_buffer(128)
        params = DEVICE_ANAINFO_STATUS_RESULT()
        self.assertEquals(self.reader.GetAntenna(DevID, params), 0)

    def test_setantenna(self):
        ''' 测试设置天线信息接口 '''
        DevID = create_string_buffer(128)
        params = SET_AllANTENNA_PARAM()
        self.assertEquals(self.reader.SetAntenna(DevID, params), 0)

    def test_getreaderinfo(self):
        ''' 测试查询读写器信息接口 '''
        DevID = create_string_buffer(128)
        pRepMsg = DEVICE_STATUS_RESULT()
        self.assertEquals(self.reader.GetReaderInfo(DevID, pRepMsg), 0)

    def test_setgpo(self):
        ''' 测试设置GPO电平的接口 '''
        DevID = create_string_buffer(128)
        params = SET_GPO_PARAM()
        self.assertEquals(self.reader.SetGpO(DevID, params), 0)

    def test_getgpio(self):
        ''' 测试查询GPIO口的信息 '''
        DevID = create_string_buffer(128)
        io = GPIO()
        pRepMsg = DEVICE_GPI_STATUS_RESULT()
        self.assertEquals(self.reader.GetGpIO(DevID, io, pRepMsg), 0)

    def test_ISO_6C_StartPeriodInventory(self):
        ''' 测试盘点操作接口 '''
        DevID = create_string_buffer(128)

        def callbackReport(handle, context):
            result = cast(context, POINTER(INVENTORY_REPORT_RESULT))[0]
            print result.DeviceID
            print result.AntennaID
            print result.EPC
            print result.RSSI
            print result.TimeStamp
            print result.TID
            print result.Frequency
            return 1

        self.assertEquals(self.reader.ISO_6C_StartPeriodInventory(DevID, callbackReport), 0)

    def test_ISO_6C_GetPeriodInventoryResult(self):
        '''
        测试获取盘点结果操作接口
        单元测试结果：返回4294967295L !=0
         '''
        DevID = create_string_buffer(128)
        tags = AllTagInfo()
        self.assertEquals(self.reader.ISO_6C_GetPeriodInventoryResult(DevID, tags), 0)

    def test_ISO_6C_StopPeriodInventory(self):
        ''' 测试停止周期盘点操作接口 '''
        DevID = create_string_buffer(128)
        self.assertEquals(self.reader.ISO_6C_StopPeriodInventory(DevID), 0)

    def test_ISO_6C_Inventory(self):
        '''
        测试单次盘点操作接口
        单元测试结果：返回4294967295L !=0
         '''
        DevID = create_string_buffer(128)
        print DevID.value
        tags = AllTagInfo()
        self.assertEquals(self.reader.ISO_6C_Inventory(DevID, tags), 0)

    def test_ISO_6C_Inventory_Cycle(self):
        '''
        测试循环盘点操作
        单元测试结果：返回4294967295L !=0
         '''
        DevID = create_string_buffer(128)
        tags = AllTagInfo()
        self.assertEquals(self.reader.ISO_6C_Inventory_Cycle(DevID, tags), 0)

    def test_ISO_6C_Read(self):
        '''
        测试读取标签块区操作
        单元测试结果：返回4294967295L !=0
         '''
        DevID = create_string_buffer(128)
        antennaId = 0
        pBlockparam = BlockInfo()
        pData = READ_REPORT_RESULT()
        nCount = c_int(0)
        bDecrypt = False
        bCheckSig = False
        self.assertEquals(self.reader.ISO_6C_Read(DevID, antennaId, pBlockparam, pData, nCount, bDecrypt, bCheckSig), 0)

    def test_ISO_6C_BlockWrite(self):
        '''
        测试标签块写操作
        单元测试结果：返回4294967295L !=0
        '''
        DevID = create_string_buffer(128)
        antennaId = 0
        pBlockparam = BlockInfo()
        pData = ResultdData()
        nCount = c_int(0)
        self.assertEquals(self.reader.ISO_6C_BlockWrite(DevID, pBlockparam, pData, nCount, antennaId), 0)

    def test_ISO_6C_BlockErase(self):
        '''
        测试标签块擦除操作
        单元测试结果：返回4294967295L !=0
         '''
        DevID = create_string_buffer(128)
        antennaId = 2
        pBlockparam = BlockInfo()
        pData = ResultdData()
        nCount = c_int(5)
        self.assertEquals(self.reader.ISO_6C_BlockErase(DevID, pBlockparam, pData, nCount, antennaId), 0)

    def test_ISO_6C_Kill(self):
        '''
        测试杀死标签操作
        单元测试结果：返回4294967295L !=0
         '''
        DevID = create_string_buffer(128)
        unAccessword = 123
        unKillword = 123
        antennaId = 0
        strEPC = 'd'
        length = 5
        pData = ResultdData()
        nCount = c_int(0)
        self.assertEquals(
            self.reader.ISO_6C_Kill(DevID, unAccessword, unKillword, antennaId, strEPC, length, pData, nCount), 0)

    def test_ISO_6C_Lock(self):
        '''
        测试锁定标签操作
        单元测试结果：返回4294967295L !=0
         '''
        DevID = create_string_buffer(128)
        permission = LockPermissions()
        antennaId = 0
        strEPC = 'd'
        length = 5
        pData = ResultdData()
        self.assertEquals(self.reader.ISO_6C_Lock(DevID, permission, antennaId, strEPC, length, pData), 0)

    def test_ISO_6C_ReadCycle(self):
        '''
        测试快速读取操作
        单元测试结果：返回4294967295L !=0
        '''
        DevID = create_string_buffer(128)
        nCount = 5
        antennaId = 0
        pBlockparam = BlockInfo()
        ardi = ALLReadDataInfo()
        bEncrypt = False
        bCheckSig = False
        self.assertEquals(self.reader.ISO_6C_ReadCycle(DevID, antennaId, pBlockparam, ardi, bEncrypt, bCheckSig), 0)

        # def test_ISO_6C_WriteCycle(self):
        # ''' 测试快速写操作 '''
        # DevID = create_string_buffer(128)
        # 	nCount = c_int(0)
        # 	pBlockparam = BlockInfo()
        # 	bEncrypt = False
        # 	bCheckSig = False
        # 	self.assertEquals(self.reader.ISO_6C_WriteCycle(DevID, nCount, pBlockparam, bEncrypt, bCheckSig), 0)