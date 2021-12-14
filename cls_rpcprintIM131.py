# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/cls_rpcprintIM131.py
# Compiled at: 2017-12-12 12:40:08
"""
Created on Jun 19, 2015

@author: cloud3
"""
from printer.cls_IM131 import cls_IM131
import os, threading, zipfile, ConfigParser, xmlrpclib
from time import sleep
import time, sys, cv2, datetime, logging, logging.handlers
from logging.handlers import TimedRotatingFileHandler
from ConfigParser import ConfigParser
from time import time
import xmlrpclib
from multiprocessing import Process
logger = logging.getLogger('dp110server')

class printThread(threading.Thread):

    def Insertlog(self, logmsg):
        now = datetime.datetime.now()
        if self.logtime != now.strftime('%d-%H'):
            self.logbytime.removeHandler(self.logbytime.handlers[0])
            self.Initlog()
        self.logbytime.info(logmsg)

    def setPrint(self, parent, printer, rpcprinter, totalLayer, baseNumber, ZMotorAmount, thickness, ZeroPoint, ZMotorEndUpDistance, ifolder):
        self.parent = parent
        self.printer = printer
        self.rpcprinter = rpcprinter
        self.baseNumber = baseNumber
        CMIDXpath = os.environ.get('HOME', '/home/pi') + '/carima/buffer/image/CMSection.idx'
        if os.path.exists(CMIDXpath) == True:
            self.nowLayer = 0
            self.totalLayer = totalLayer - 1
        else:
            self.nowLayer = 1
            self.totalLayer = totalLayer
        self.ZMotorAmount = ZMotorAmount
        self.HalfZMotorAmount = ZMotorAmount / 2
        self.thickness = thickness
        self.ZeroPoint = ZeroPoint
        self.ZMotorEndUpDistance = ZMotorEndUpDistance
        self.beginningTime = int(self.printer.LightTime_Beginning * 1000)
        self.basicTime = int(self.printer.LightTime_Basic * 1000)
        self.LightStep_Beginning = int(self.printer.LightStep_Beginning)
        self.BasicwaitTime = float(self.printer.BasicWaitTime)
        self.beginningWaitTime = float(self.printer.BeginningWaitTime)
        self.motorSpeed = float(self.printer.DivisionTime * 2)
        self.pause = False
        self.stop = False
        self.interimPause = False
        self.interimResume = False
        self.interimcheck = False
        self.startPoint = False
        self.subtime = 0
        self.xmlrpcclient()
        self.is_testPause = False
        self.MoveMount = 0
        self.zeroMoveTime = int(self.ZeroPoint / 4 + 2)

    def xmlrpcclient(self):
        self.proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8080')

    def run(self):
        cv2.waitKey(1)
        cv2.waitKey(1)
        self.proxy.Layers(self.nowLayer)
        self.proxy.EngineOffCall()
        self.printer.printConnect1()
        self.printer.boardGo(self.ZeroPoint, 0)
        sleep(self.zeroMoveTime)
        if self.stop == True:
            return 1
        if self.beginningTime > self.basicTime and self.LightStep_Beginning != 0:
            Minus_beginningTime = int((self.beginningTime - self.basicTime) / self.LightStep_Beginning)
        else:
            Minus_beginningTime = 0
        while self.nowLayer < self.totalLayer:
            if self.stop == True:
                self.printer.boardUp(200, 0)
                return 1
            if self.pause == True:
                if self.stop == True:
                    return 1
                if self.interimPause == True:
                    self.printer.boardUp(self.ZeroPoint - self.printer.ZMotorEndUpDistance, 1)
                    self.interimPause = False
                    self.interimcheck = True
                    sleep(0.5)
                    continue
                elif self.stop == True:
                    return 1
                else:
                    sleep(0.5)
                    continue

            elif self.interimResume == True & self.interimcheck == True:
                self.printer.boardGo(self.ZeroPoint - self.printer.ZMotorEndUpDistance, 1)
                self.interimResume = False
                self.interimcheck = False
            else:
                if self.startPoint == True:
                    if self.printer.LowSpeedAmount == 0:
                        self.printer.boardGo(self.ZeroPoint - self.MoveMount, 1)
                    else:
                        self.printer.boardGo(self.ZeroPoint - (self.printer.LowSpeedAmount + self.MoveMount), 1)
                        if self.stop == True:
                            self.printer.boardUp(200, 0)
                            return 1
                        self.printer.changeTimer(self.motorSpeed)
                        if self.stop == True:
                            self.printer.boardUp(200, 0)
                            return 1
                        self.printer.boardGo(self.ZeroPoint - self.MoveMount, 1)
                        if self.stop == True:
                            self.printer.boardUp(200, 0)
                            return 1
                        self.printer.orginalTimer()
                if self.stop == True:
                    self.printer.boardUp(200, 0)
                    return 1

            if self.nowLayer <= self.printer.LightStep_Beginning:
                if self.beginningWaitTime != 0:
                    sleep(self.beginningWaitTime - 0.36)
            elif self.BasicwaitTime != 0:
                if self.thickness == 0.1:
                    sleep(self.BasicwaitTime - 0.36)
                if self.thickness == 0.075:
                    sleep(self.BasicwaitTime - 0.36)
                if self.thickness == 0.05:
                    sleep(self.BasicwaitTime - 0.36)
                if self.thickness == 0.025:
                    sleep(self.BasicwaitTime - 0.36)
            else:
                if self.stop == True:
                    self.printer.boardUp(200, 0)
                    return 1
                self.printer.lightOn1(self.nowLayer, self.basicTime, self.beginningTime)
                self.nowLayer += 1
                self.printer.display.showSliceOffImage()
                if self.stop == True:
                    self.printer.boardUp(200, 0)
                    return 1
                self.proxy.EngineOffCall()
                self.proxy.Layers(self.nowLayer)
                if self.nowLayer <= self.LightStep_Beginning:
                    self.beginningTime = self.beginningTime - Minus_beginningTime
                if self.printer.LowSpeedAmount == 0:
                    self.printer.boardGo(self.ZeroPoint - self.printer.ZMotorAmount - self.MoveMount, 1)
                else:
                    self.printer.changeTimer(self.motorSpeed)
                    if self.stop == True:
                        self.printer.boardUp(200, 0)
                        return 1
                    self.printer.boardGo(self.ZeroPoint - (self.printer.LowSpeedAmount + self.MoveMount), 1)
                    if self.stop == True:
                        self.printer.boardUp(200, 0)
                        return 1
                    self.printer.orginalTimer()
                    if self.stop == True:
                        self.printer.boardUp(200, 0)
                        return 1
                    self.printer.boardGo(self.ZeroPoint - self.ZMotorAmount - self.MoveMount, 1)
                self.MoveMount += self.thickness
                if self.stop == True:
                    self.printer.boardUp(200, 0)
                    return 1
                self.startPoint = True
                if self.nowLayer >= self.totalLayer:
                    if self.printer.LowSpeedAmount == 0:
                        self.printer.boardGo(self.ZeroPoint - self.MoveMount, 1)
                    else:
                        self.printer.boardGo(self.ZeroPoint - (self.printer.LowSpeedAmount + self.MoveMount), 1)
                        self.printer.changeTimer(self.motorSpeed)
                        self.printer.boardGo(self.ZeroPoint - self.MoveMount, 1)
                        self.printer.orginalTimer()
                    sleep(self.BasicwaitTime)
                    self.printer.lightOn1(self.nowLayer, self.basicTime, self.beginningTime)
                    self.printer.display.showSliceOffImage()
                    if self.printer.LowSpeedAmount == 0:
                        self.printer.boardGo(self.ZeroPoint - self.printer.ZMotorAmount - self.MoveMount, 1)
                    else:
                        self.printer.changeTimer(self.motorSpeed)
                        self.printer.boardGo(self.ZeroPoint - (self.printer.LowSpeedAmount + self.MoveMount), 1)
                        self.printer.orginalTimer()
                    self.printer.printConnect2()
                    self.proxy.Printing()
                    self.parent.Insertlog('printing complete')
                    self.printer.boardGo(0, 1)
                    self.proxy.EngineOffCall()
                    self.printer.removeImageFile()
                    return 1


class AduThread(threading.Thread):

    def AdusetPrint(self, printer):
        self.printer = printer

    def run(self):
        self.proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8080')
        while 1:
            RfidValue = self.printer.readRFIDvalue()
            IMmodel = RfidValue.count('A')
            if IMmodel == 1:
                self.proxy.Rfid(RfidValue)
                return 1
            sleep(1)


class cls_RpcPrint131(object):
    """
    classdocs
    """

    def __init__(self, params):
        """
        Constructor
        """
        self.printer = cls_IM131()
        self.rpcprinter = cls_RpcPrint131
        self.is_open = -1
        self.is_printing = 3
        self.new_img = 0
        self.is_light_on = False
        self.Initlog()
        self.Insertlog('system on')
        self.proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8080')
        self.printer.display.xmlrpcclient()
        self.trySerial = 0
        print 'IM131'
        self.engineUSEStartTime = 0
        if os.name == 'posix':
            self.configPath = os.environ.get('HOME', '/home/pi') + '/carima/system.cfg'
        else:
            self.configPath = 'System.cfg'

    def isOpenPorts(self):
        return self.is_open

    def reopenPorts(self):
        self.Insertlog('open port')
        if self.printer.printConnect() == False:
            self.Insertlog('Motor Serial Connect Failed')
            return -1
        else:
            self.Insertlog('Motor Serial Connect success')
            return 1

    def openPorts(self):
        self.Insertlog('open port')
        if self.printer.printConnect() == False:
            self.reopenPorts()
        else:
            self.Insertlog('Motor Serial Connect success')
            return 1

    def isPrinting(self):
        return self.is_printing

    def chkBrightness(self):
        self.assdasd = True

    def printStart(self, FileType, totalLayer, thickness, totalTime):
        self.printer.readConfig(self.configPath)
        ifolder = os.environ.get('HOME', '/home/dp110') + '/carima/buffer/image'
        if not os.path.exists(ifolder):
            self.logger.error('path not exists: %s' % ifolder)
            return False
        base_index = 1
        self.printer.display.imageRoot = ifolder
        self.printer.display.fileType = 'png'
        self.pthread = printThread()
        self.pthread.setPrint(self, self.printer, self.rpcprinter, totalLayer, base_index, self.printer.ZMotorAmount, thickness, self.printer.ZeroPoint, self.printer.ZMotorEndUpDistance, ifolder)
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
        sleep(0.3)
        return self.pthread.nowLayer

    def printStop(self, nowLayer, remainTime):
        self.pthread.stop = True
        self.printer.orginalTimer()
        self.printer.boardUp(200, 0)
        self.printer.display.clear()
        self.proxy.Printing()
        self.Insertlog('printing stop')
        self.printer.removeImageFile()
        return 1

    def motorSpeedTest(self):
        self.printer.changeTimer(8)
        return 1

    def isPause(self):
        return self.pthread.pause

    def printPause(self, pauseinterim):
        if pauseinterim == True:
            self.pthread.pause = True
            self.pthread.interimPause = True
            self.Insertlog('printing pause_interim')
        else:
            self.pthread.pause = True
            self.Insertlog('printing pause')
        return 1

    def printResume(self, pauseinterim):
        if pauseinterim == True:
            self.pthread.pause = False
            self.pthread.interimResume = True
        else:
            self.pthread.pause = False
        self.Insertlog('printing resume')
        return 1

    def isEngineOn(self):
        return 1

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

    def temperature(self):
        return self.printer.checkTmpSensor()

    def rfid(self):
        self.AThread = AduThread()
        self.AThread.AdusetPrint(self.printer)
        self.AThread.start()

    def shutdown(self):
        self.Insertlog('system off')
        self.printer.boardGo(0)
        os.system('sudo shutdown -h 0')
        return 1

    def boardStop(self):
        self.Insertlog('motor control - stop')
        return self.printer.boardStop()

    def boardUp(self, ZMotorAmount):
        self.printer.boardUp(ZMotorAmount, 0)
        return 1

    def boardDown(self, ZMotorAmount, thickness):
        self.printer.boardDown(ZMotorAmount, thickness, 0)
        return 1

    def motorUpDir(self):
        self.printer.motorUpDir()
        return 1

    def motorPosition(self):
        self.printer.motorPosition()
        return 1

    def DownTray(self, value):
        self.printer.TrayDown(value)
        return 1

    def UpTray(self, value):
        self.printer.TrayUp(value)
        return 1

    def zeropointUp(self, ZMotorAmount):
        self.printer.printConnect1()
        self.printer.boardUp(ZMotorAmount, 1)
        return self.printer.printConnect2()

    def zeropointDown(self, ZMotorAmount, thickness):
        self.printer.printConnect1()
        self.printer.boardDown(ZMotorAmount, thickness, 1)
        return self.printer.printConnect2()

    def BasicImageOff(self):
        self.printer.BasicImageOff()
        self.Insertlog('basicimage_off')
        return 1

    def BasicImageOn(self):
        self.printer.BasicImageOn()
        self.Insertlog('basicimage_on')
        return 1

    def BasicImageOncont(self):
        self.printer.display.whiteclearcont()
        return 1

    def setupGrid(self, xres, yres, xgrid, ygrid, line):
        return self.printer.display.setupGrids(xres, yres, xgrid, ygrid, line)

    def showGrid(self, x, y, val, flag):
        self.printer.display.showGrids(x, y, val, flag)
        return 1

    def clearGrid(self):
        self.printer.display.clearGrids()
        return 1

    def maskImageOn(self):
        self.printer.display.maskImageOn()
        return 1

    def whiteImageOn(self):
        self.printer.display.whiteImageOn()
        return 1

    def whiteImageOff(self):
        self.printer.display.whiteImageOff()
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