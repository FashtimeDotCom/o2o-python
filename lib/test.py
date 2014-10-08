#! /usr/bin/env python
# coding=utf-8
from RFIDReader import *


def DisconnectCallback(handle, context):
    print "hello"
    return 1


def Error(handle, context):
    print "error"
    return 1


# 盘点
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


def main():
    Reader = RFIDReader()
    DevID = create_string_buffer(128)
    Reader.Connect("172.16.13.222", DevID, 7880, DisconnectCallback, Error)
    print DevID.value
    # params = DEVICE_ANAINFO_STATUS_RESULT()
    #params2 = SET_AllANTENNA_PARAM()
    #params2.Ant1.bEnable = True
    #params2.Ant1.nPower = 40 # nInvCycle
    #params2.Ant1.nDwellTime = 400
    #print Reader.SetAntenna(DevID, params2)
    #print Reader.GetAntenna(DevID, params)
    #print params.szAnaStatus
    #print params.szTransmitPower
    #print params.szDwellTime
    #print params.szNumInvCyc
    # params = DEVICE_STATUS_RESULT()
    #print Reader.GetReaderInfo(DevID, params) 
    #print params.szAnaNum
    #print params.szMacRegion
    #print params.szRadioOpen
    #print params.szGPINum
    #print params.szGPONum
    #params = SET_GPO_PARAM()
    #params.nLevel1 = 1
    #params.nLevel2 = 1
    #print Reader.SetGpO(DevID, params)
    #params = DEVICE_GPI_STATUS_RESULT()
    #io = GPIO() #有问题
    #Reader.GetGpIO(DevID, io, params)
    #print params.szEleLevel1
    #print params.szEleLevel2
    #print params.szEleLevel3
    print Reader.ISO_6C_StartPeriodInventory(DevID, callbackReport)

    #print Reader.ISO_6C_Inventory(DevID, tags)

    #print tags.nTagsCount

    nAntennaID = 0
    blockparam = BlockInfo()
    pData = READ_REPORT_RESULT()
    nCount = c_int(0)
    bEncrypt = False
    bCheckSig = False
    blockparam.pszPWD = '00000000'
    epc = "E2001018741302250490E357"
    blockparam.nEpcLength = len(epc)
    blockparam.nBankType = 0
    blockparam.nLength = 0
    blockparam.nStartByte = 0
    blockparam.nTagType = 0
    blockparam.szEPC = epc
    data = ALLReadDataInfo()
    data.tagcount = c_short(0)
    tags = AllTagInfo()
    print Reader.ISO_6C_Read(DevID, nAntennaID, blockparam, pData, nCount, bEncrypt, bCheckSig)
    print Reader.ISO_6C_Inventory(DevID, tags)
    print Reader.ISO_6C_Inventory_Cycle(DevID, tags)
    # while(True):
    #   Reader.ISO_6C_StartPeriodInventory(DevID, callbackReport, True)
    #print tags.nTagsCount
    #print tags.OneTagInfo[0].cid[:]
    #tags = AllTagInfo()
    #while(True):
    #  Reader.ISO_6C_Inventory_Cycle(DevID, tags)
    #  if tags.nTagsCount> 0:
    #     print tags.OneTagInfo[0].cid[:]
    # time.sleep(1)

    print Reader.Disconnect(DevID)


""" 
    Reader.ISO_6C_ReadCycle(DevID, nAntennaID, blockparam, data, bEncrypt, bCheckSig)
        if data.tagcount>0:
            print data.tagcount
            print data.readdata[0].DeviceID
            print data.readdata[0].AntennaID
            print data.readdata[0].strEpc
            print data.readdata[0].ReadData
        data = ALLReadDataInfo()    
"""

# print pData.DeviceID
# print pData.AntennaID
# print pData.strEpc
# print pData.ReadData
# print pData.ScatterErr
#print pData.Ciphertext
#  print pData.EncryptType

#tags = AllTagInfo()


#print  Reader.ISO_6C_Inventory_Cycle(DevID, tags)
#print tags.nTagsCount
#print pData.ReadData
#print pData.DeviceID
#print Reader.ISO_6C_Read(DevID, nAntennaID)
#print Reader.ISO_6C_StopPeriodInventory(DevID)
#print Reader.ISO_6C_Write(DevID, antennaID, blockparam, pData, nCount, bEncrypt, bCheckSig)
# print Reader.ISO_6C_BlockWrite(DevID, blockparam, pData, nCount, antennaID)
#print Reader.ISO_6C_ReadCycle(DevID, antennaID, blockparam, ardi, bEncrypt, bCheckSig)
#print Reader.ISO_6C_Inventory_Cycle(DevID, tags)
# print tags.OneTagInfo[0].cid[:]
#print tags.nTagsCount
#permission = LockPermissions()
#strEPC = create_string_buffer(100)
#strEPC.value=""
#print Reader.ISO_6C_Lock(DevID, permission, antennaID, strEPC, 0, pData)
if __name__ == '__main__':
    main()
