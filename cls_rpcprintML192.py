# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/cls_rpcprintML192.py
# Compiled at: 2020-02-07 09:29:26
"""
Created on Jun 19, 2015

@author: cloud3
"""
from printer.cls_ML192v22 import cls_ML192v22
import os, threading, zipfile, xmlrpclib
from time import sleep
import sys, cv2, datetime, logging, logging.handlers
from logging.handlers import TimedRotatingFileHandler
from ConfigParser import ConfigParser
import time
from cv2 import WINDOW_NORMAL, CV_WINDOW_AUTOSIZE
import xmlrpclib
from multiprocessing import Process
import glob
logger = logging.getLogger('dp110server')

class imgShowThread(threading.Thread):

    def run(self):
        os.system('omxiv -d 5 ' + self.imgPath)
        return 1


class printThread(threading.Thread):

    def setPrint(self, parent, printer, rpcprinter, totalLayer, baseNumber, ZMotorAmount, thickness, ZeroPoint, ZMotorEndUpDistance, ifolder):
        self.parent = parent
        self.printer = printer
        self.rpcprinter = rpcprinter
        self.baseNumber = baseNumber
        CMIDXpath = os.environ.get('HOME', '/home/pi') + '/carima/buffer/image/CMSection.idx'
        self.idxPath = glob.glob(os.environ.get('HOME', '/home/pi') + '/carima/buffer/image/*.idx')
        self.Config = ConfigParser(allow_no_value=True)
        self.Config.read(self.idxPath)
        if os.path.exists(CMIDXpath) == True:
            self.nowLayer = 0
            self.totalLayer = totalLayer - 1
        else:
            self.nowLayer = 1
            self.totalLayer = totalLayer
        self.ZMotorAmount = ZMotorAmount
        self.thickness = thickness
        self.ZeroPoint = ZeroPoint
        self.ZMotorEndUpDistance = ZMotorEndUpDistance
        self.DivideTime = self.printer.DivisionTime
        self.pause = False
        self.stop = False
        self.interimPause = False
        self.interimResume = False
        self.interimcheck = False
        self.startPoint = False
        self.basicTime = int(self.printer.LightTime_Basic * 1000)
        self.beginningTime = int(self.printer.LightTime_Beginning * 1000)
        self.proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8080')
        self.LightStep_Beginning = int(self.printer.LightStep_Beginning)
        self.proxy.Layers(self.nowLayer)
        self.DagerOption = 0
        self.doorOpen = False
        self.checkHome = False
        self.interOption = 0
        self.pauseOption = 0
        self.reTryPause = 0
        self.interimPausing = 0
        self.reservationPause = 0
        self.motorendUpmoveTime = int(self.printer.ZMotorEndUpDistance / 4 * 1000 + 100)
        self.motorMoveAmountTime = int(self.printer.ZMotorAmount / 4 * 1000 + 100)
        self.DoorSignal = False

    def openDoor1(self):
        self.printer.checkSensor()
        self.printer.printConnect1()
        returnData = self.printer.checkSensor()
        number = 0
        for hex1 in returnData:
            Fnumber = number
            number = number + 1
            if hex1 == 'f':
                if returnData[(Fnumber + 1)] == 'f':
                    self.printer.printConnect2()
                    self.DoorSignal = True
                    return True
                if returnData[(Fnumber + 1)] == '1':
                    pass
                elif returnData[(Fnumber - 1)] == 'd':
                    self.printer.printConnect2()
                    self.DoorSignal = False
                    return False

        return 'Fail'

    def xmlrpcclient(self):
        self.proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8080')

    def run(self):
        self.parent.Insertlog('run enter')
        cv2.waitKey(1)
        cv2.waitKey(1)
        while 1:
            self.parent.Insertlog('run while enter')
            self.printer.printConnect1()
            if self.openDoor1() == True:
                self.parent.Insertlog('opendoor1 true')
                self.proxy.Danger(True)
                self.DagerOption = 1
                if self.stop == True:
                    return 1
                self.printer.boardStop()
                sleep(0.1)
            else:
                self.parent.Insertlog('opendoor1 false')
                self.printer.printConnect2()
                if self.stop == True:
                    return 1
                if self.printer.boardHome() == '4f1300000000000000df500a' or '4f1300000000000000ff500a':
                    self.printer.boardHome()
                if self.stop == True:
                    return 1
            if self.printer.boardHome() == '4f0b0000000000000000500a':
                if self.stop == True:
                    return 1
                break
            self.printer.checkSensor()
            if self.DagerOption == 1 and self.openDoor1() == False:
                self.parent.Insertlog('enter3')
                self.proxy.Danger(False)
                self.proxy.Danger(False)
                self.DagerOption = 0

        if self.stop == True:
            return 1
        self.DagerOption = 0
        self.printer.boardUp(self.printer.ZeroPoint)
        if self.stop == True:
            self.printer.boardUp(self.printer.ZMotorEndUpDistance)
            return 1
        if self.beginningTime > self.basicTime and self.LightStep_Beginning != 0:
            Minus_beginningTime = int((self.beginningTime - self.basicTime) / self.LightStep_Beginning)
        else:
            Minus_beginningTime = 0
        while self.nowLayer < self.totalLayer:
            self.parent.Insertlog('enter4')
            try:
                self.parent.Insertlog('enter5')
                pixeldata = int(self.Config.get('PixelData', 'SEC_%04d.png' % self.nowLayer))
            except:
                pixeldata = 1
            else:
                self.parent.Insertlog('enter6')
                if self.pause == True:
                    if self.stop == True:
                        return 1
                    if self.interimPause == True and self.reTryPause == 0:
                        self.reTryPause = 1
                        self.DoorSignal = True
                        self.printer.boardUp(self.printer.ZMotorEndUpDistance)
                        self.interimPausing = 1
                        cv2.waitKey(self.motorendUpmoveTime)
                        self.interimcheck = True
                        self.interimPause = False
                        sleep(0.5)
                        continue
                    else:
                        self.interimPause = False
                        if self.stop == True:
                            return 1
                        if self.openDoor1() == False and self.interOption == 0 and self.pauseOption == 0:
                            if self.DagerOption == 1:
                                self.parent.Insertlog('dangeroption enter')
                                self.proxy.Danger(False)
                                self.pause = False
                                self.DagerOption = 0
                        sleep(0.1)
                        continue
                elif self.interimResume == True and self.interimcheck == True:
                    self.interimResume = False
                    self.interimcheck = False
                    self.printer.boardDown(self.printer.ZMotorEndUpDistance, 0)
                    self.interimPausing = 0
                    cv2.waitKey(self.motorendUpmoveTime)
                    self.reTryPause = 0
                    self.DoorSignal = False
                else:
                    if self.reservationPause == 1:
                        self.pause = True
                    if self.stop == True:
                        return 1

                if self.openDoor1() == True:
                    self.parent.Insertlog('enter7')
                    self.proxy.Danger(True)
                    self.pause = True
                    self.DagerOption = 1
                if self.pause == False:
                    if self.startPoint == True:
                        self.printer.boardDown(self.printer.ZMotorAmount, self.thickness)
                        cv2.waitKey(self.motorMoveAmountTime)
                    if pixeldata >= 2000000:
                        self.parent.Insertlog('enter8')
                        if self.thickness == 0.1:
                            sleep(19.64)
                        elif self.thickness == 0.075:
                            sleep(29.64)
                        elif self.thickness == 0.05:
                            self.parent.Insertlog('enter9')
                            sleep(49.64)
                        elif self.thickness == 0.025:
                            sleep(119.64)
                    else:
                        self.parent.Insertlog('enter10')
                        if self.thickness == 0.1:
                            sleep(2.54)
                        else:
                            if self.thickness == 0.075:
                                sleep(2.54)
                            else:
                                if self.thickness == 0.05:
                                    sleep(4.54)
                                elif self.thickness == 0.025:
                                    sleep(4.54)
                                if self.stop == True:
                                    return 1
                            self.printer.lightOn1(self.nowLayer, self.basicTime, self.beginningTime)
                            if self.stop == True:
                                return 1
                        self.parent.Insertlog('enter11')
                        self.printer.display.showSliceOffImage()
                        self.proxy.EngineOffCall()
                        self.nowLayer += 1
                        self.proxy.Layers(self.nowLayer)
                        if self.nowLayer <= self.LightStep_Beginning:
                            self.beginningTime = self.beginningTime - Minus_beginningTime
                        self.printer.boardUp(self.printer.ZMotorAmount)
                        cv2.waitKey(self.motorMoveAmountTime)
                        if self.stop == True:
                            return 1
                    self.startPoint = True
                if self.nowLayer >= self.totalLayer:
                    self.parent.Insertlog('enter12')
                    try:
                        pixeldata = int(self.Config.get('PixelData', 'SEC_%04d.png' % self.nowLayer))
                    except:
                        pixeldata = 1

                    self.printer.boardDown(self.printer.ZMotorAmount, self.thickness)
                    cv2.waitKey(self.motorMoveAmountTime)
                    if pixeldata >= 2000000:
                        if self.thickness == 0.1:
                            sleep(19.64)
                        elif self.thickness == 0.075:
                            sleep(29.64)
                        elif self.thickness == 0.05:
                            sleep(49.64)
                        elif self.thickness == 0.025:
                            sleep(119.64)
                    elif self.thickness == 0.1:
                        sleep(2.54)
                    elif self.thickness == 0.075:
                        sleep(2.54)
                    elif self.thickness == 0.05:
                        sleep(4.54)
                    elif self.thickness == 0.025:
                        sleep(4.54)
                    self.printer.lightOn1(self.nowLayer, self.basicTime, self.beginningTime)
                    self.printer.display.showSliceOffImage()
                    self.proxy.EngineOffCall()
                    self.printer.ledOn_fanOff()
                    self.printer.printConnect2()
                    sleep(0.1)
                    self.proxy.Printing()
                    self.parent.Insertlog('printing complete')
                    self.printer.removeImageFile()
                    self.printer.boardUp(int(self.printer.ZMotorEndUpDistance))
                    return 1


class cls_RpcPrintML192(object):
    """
    classdocs
    """

    def __init__(self, params):
        """
        Constructor
        """
        self.printer = cls_ML192v22()
        self.rpcprinter = cls_RpcPrintML192
        self.is_open = -1
        self.is_printing = 2
        self.new_img = 0
        self.PausePoint = 0
        self.interimPoint = 0
        self.is_light_on = False
        self.Initlog()
        self.Insertlog('system on ML-192')
        self.printer.display.xmlrpcclient()
        self.proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8080')
        print 'ML-192'
        self.engineUSEStartTime = 0
        self.testSignal = False
        if os.name == 'posix':
            self.configPath = os.environ.get('HOME', '/home/pi') + '/carima/system.cfg'
        else:
            self.configPath = 'System.cfg'

    def engineTest(self):
        return self.proxy.EngineOnCall()

    def engineOffTest(self):
        return self.proxy.EngineOffCall()

    def isOpenPorts(self):
        return self.is_open

    def openPorts(self):
        self.Insertlog('open port')
        return self.printer.printConnect()

    def isPrinting(self):
        return self.is_printing

    def printStart(self, FileType, totalLayer, thickness, totalTime):
        self.printer.readConfig(os.environ.get('HOME', '/home/pi') + '/carima/system.cfg')
        ifolder = os.environ.get('HOME', '/home/dp110') + '/carima/buffer/image'
        if not os.path.exists(ifolder):
            self.logger.error('path not exists: %s' % ifolder)
            return False
        base_index = 1
        self.printer.display.imageRoot = ifolder
        self.printer.display.fileType = 'png'
        self.pthread = printThread()
        self.pthread.setPrint(self, self.printer, self.rpcprinter, totalLayer, base_index, self.printer.ZMotorAmount, thickness, self.printer.ZeroPoint, self.printer.ZMotorEndUpDistance, ifolder)
        self.printer.ledblink_fanOn()
        self.engineLightOn()
        self.pthread.start()
        self.Insertlog('printing start - %d - %d' % (totalTime, totalLayer))
        self.is_printing = 1
        return 1

    def uploadFile(self, fileName, fileData):
        if os.path.isdir(os.environ.get('HOME', '/home/pi') + '/carima/buffer/image'):
            self.printer.removeImageFile()
        fileNames = os.environ.get('HOME', '/home/dp110') + '/carima/buffer/' + fileName
        with open(fileNames, 'wb') as (handle):
            handle.write(fileData.data)
        fzip = zipfile.ZipFile(fileNames)
        fzip.extractall(os.environ.get('HOME', '/home/pi') + '/carima/buffer/image')
        fzip.close()
        return 1

    def sliceUpload(self, fileName, fileData):
        fileNames = os.environ.get('HOME', '/home/dp110') + '/carima/data/' + fileName
        with open(fileNames, 'wb') as (handle):
            handle.write(fileData.data)
        return 1

    def sliceDownload(self):
        with open('/home/dp110/carima/system.cfg', 'rb') as (handle):
            return xmlrpclib.Binary(handle.read())
        handle.close()

    def getCurrentLayer(self):
        return self.pthread.nowLayer

    def printStop(self, nowLayer, remainTime):
        self.proxy.Printing()
        self.pthread.stop = True
        self.printer.printConnect2()
        self.printer.boardStop()
        self.printer.boardUp(self.printer.ZMotorEndUpDistance)
        self.printer.display.showSliceOffImage()
        self.printer.led_fanOn()
        self.Insertlog('printing stop')
        self.printer.removeImageFile()
        return 1

    def isPause(self):
        return self.pthread.pause

    def printPause(self, pauseinterim):
        if pauseinterim == True:
            self.pthread.interOption = 1
            self.pthread.pause = True
            self.pthread.interimPause = True
            self.Insertlog('printing interimpause')
        elif self.pthread.interimPausing == 1:
            self.pthread.reservationPause = 1
            return 1
        else:
            self.pthread.pauseOption = 1
            self.pthread.pause = True
            self.Insertlog('printing pause')

        return 1

    def printResume(self, pauseinterim):
        if pauseinterim == True:
            self.pthread.interOption = 0
            self.pthread.pause = False
            self.pthread.interimResume = True
            self.pthread.interimPause = False
            self.Insertlog('printing interimresume')
        else:
            self.pthread.reservationPause = 0
            self.pthread.pauseOption = 0
            self.pthread.pause = False
            self.Insertlog('printing resume')
        return 1

    def isEngineOn(self):
        return 1

    def danger(self):
        returnData = self.printer.checkSensor()
        if returnData == '4f1300000000000000ff500a':
            return 1
        else:
            return -1

    def enginePower(self, isOn):
        return 1

    def isLightOn(self):
        return 1

    def engineLightOn(self):
        self.Insertlog('engine_on')
        self.engineUSEStartTime = datetime.datetime.now().replace(microsecond=0)
        return 1

    def engineLightOff(self):
        self.Insertlog('engine_off')
        Config = ConfigParser()
        Config.optionxform = str
        engine_EndTime = datetime.datetime.now().replace(microsecond=0)
        engine_CurUseTime = engine_EndTime - self.engineUSEStartTime
        Config.read('/home/dp110/carima/system.cfg')
        pre_Engine_USETime = Config.get('SYSTEM', 'Engine_TotalTime')
        dtime = datetime.datetime.strptime(pre_Engine_USETime, '%H:%M:%S')
        TotalTime = dtime + engine_CurUseTime
        convert = TotalTime.strftime('%H:%M:%S')
        filepath = '/home/dp110/carima/system.cfg'
        Config.set('SYSTEM', 'Engine_TotalTime', convert)
        with open(filepath, 'wb') as (configfile):
            Config.write(configfile)
        return 1

    def boardHome(self):
        return self.printer.boardHome()

    def led_fanOn(self):
        return self.printer.led_fanOn()

    def ledOn_fanOff(self):
        return self.printer.ledOn_fanOff()

    def ledblink_fanOn(self):
        return self.printer.ledblink_fanOn()

    def shutdown(self):
        self.printer.ledOff_fanOff()
        self.printer.shutdownbeep()
        self.Insertlog('system off')
        os.system('sudo shutdown -h 0')
        return 1

    def boardStop(self):
        self.Insertlog('motor control - stop')
        return self.printer.boardStop()

    def boardUp(self, ZMotorAmount):
        self.printer.boardStop()
        self.printer.boardUp(ZMotorAmount)
        self.Insertlog('motor control - up')
        return 1

    def boardDown(self, ZMotorAmount, thickness):
        self.printer.boardStop()
        self.printer.boardDown(ZMotorAmount, thickness)
        self.Insertlog('motor control - down')
        return 1

    def zeropointUp(self, ZMotorAmount):
        self.printer.printConnect1()
        self.printer.boardUp(ZMotorAmount)
        return self.printer.printConnect2()

    def zeropointDown(self, ZMotorAmount, thickness):
        self.printer.printConnect1()
        self.printer.boardDown(ZMotorAmount, thickness)
        return self.printer.printConnect2()

    def BasicImageOff(self):
        self.printer.BasicImageOff()
        self.Insertlog('basicimage_off')
        return 1

    def BasicImageOn(self):
        self.printer.BasicImageOn()
        self.Insertlog('basicimage_on')
        return 1

    def setupGrid(self, xres, yres, xgrid, ygrid, line):
        return self.printer.display.setupGrids(xres, yres, xgrid, ygrid, line)

    def showGrid(self, x, y, val, flag):
        self.printer.display.showGrids(x, y, val, flag)
        return 1

    def clearGrid(self):
        self.printer.display.clearGrids()
        return 1

    def whiteImageOn(self):
        self.printer.display.whiteImageOn()
        return 1

    def cleanImageOn(self):
        self.printer.display.maskImageOn()
        return 1

    def whiteImageOff(self):
        self.printer.display.showSliceOffImage()
        return 1

    def maskImageOn(self):
        maskFile = os.environ.get('HOME', '/home/pi') + '/carima/basic/IM-J_basic/lineMask.png'
        if not os.path.exists(maskFile):
            self.printer.display.MakeLineMask()
        self.printer.display.LinemaskImageOn()
        return 1

    def makeImg(self):
        self.printer.display.maskImageOn()
        return 1

    def adminSet(self):
        self.Insertlog('admin set')

    def Insertlog(self, logmsg):
        now = datetime.datetime.now()
        if self.logtime != now.strftime('%d-%H'):
            self.logbytime.removeHandler(self.logbytime.handlers[0])
            self.Initlog()
        self.logbytime.info(logmsg)

    def Initlog(self):
        now = datetime.datetime.now()
        nowDateYM = now.strftime(os.environ.get('HOME', '/home/pi') + '/SystemLog/%Y-%m')
        if not os.path.exists(nowDateYM):
            os.makedirs(nowDateYM)
        self.logtime = now.strftime('%d-%H')
        nowDateMDH = now.strftime(os.environ.get('HOME', '/home/pi') + '/SystemLog/%Y-%m/%m-%d-%H')
        self.logbytime = logging.getLogger('imjlog')
        hdlr = logging.handlers.TimedRotatingFileHandler(nowDateMDH)
        formatter = logging.Formatter('[%(asctime)s] %(message)s')
        hdlr.setFormatter(formatter)
        self.logbytime.addHandler(hdlr)
        self.logbytime.setLevel(logging.INFO)

    def checkxmlrpcclient(self):
        return self.printer.display.xmlrpcclient()

    def bufferTest(self):
        self.printer.display.bufferImgTest()
        return 1

    def threadTest(self):
        return self.pthread.isAlive()

    def ATsetopenSignal(self, a):
        self.Insertlog('1')
        self.proxy.EngineOnCall()
        self.Insertlog('2')
        self.printer.lightOn1(a, 3000, 3000)
        self.Insertlog('3')
        self.printer.display.closeImgThread()
        self.Insertlog('4')
        self.proxy.EngineOffCall()
        self.Insertlog('5')
        return 1

    def TestCloseSignal(self):
        self.testSignal = False
        return 1

    def openDoor(self):
        if self.pthread.DoorSignal == True:
            return True
        if self.pthread.DoorSignal == False:
            return False